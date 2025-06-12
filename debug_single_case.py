import json
import argparse
from typing import List, Dict, Any, Set, Optional
import sys
import time
from statistics import mean
from config import API_CONFIG
from utils.api_client import create_api_client
import math

def load_test_case(json_path: str, target_idx: str) -> Dict[str, Any]:
    """加载指定idx的测试用例"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for case in data['test_cases']:
        if case['idx'] == target_idx:
            return case
    
    raise ValueError(f"找不到idx为 {target_idx} 的测试用例")

def create_custom_case(query: str, expected_paths: List[str] = None) -> Dict[str, Any]:
    """创建自定义测试用例"""
    return {
        "idx": "custom",
        "query": query,
        "category": "custom",
        "description": "自定义查询测试",
        "expected_results": [{"path": path} for path in (expected_paths or [])]
    }

def search_code(query: str) -> List[str]:
    """调用代码检索API"""
    # 创建API客户端
    api_client = create_api_client(API_CONFIG)
    
    try:
        # 调用API
        response = api_client.search_code(query)
        
        # 检查是否有错误
        if "error" in response:
            print(f"API调用失败: {response['error']}", file=sys.stderr)
            return []
            
        # 提取文件路径列表
        if isinstance(response, dict):
            if "data" in response:
                results = response["data"]
            elif "results" in response:
                results = response["results"]
            else:
                results = response
        else:
            results = response
            
        # 确保结果是列表
        if not isinstance(results, list):
            print(f"无效的结果格式: {type(results)}", file=sys.stderr)
            return []
            
        # 提取路径
        paths = []
        for item in results:
            if isinstance(item, dict):
                if "path" in item:
                    paths.append(item["path"])
                elif "file_path" in item:
                    paths.append(item["file_path"])
            elif isinstance(item, str):
                paths.append(item)
                
        return paths
        
    except Exception as e:
        print(f"API调用失败: {str(e)}", file=sys.stderr)
        return []

def calculate_relevance_scores(expected_paths: List[str], actual_results: List[str]) -> float:
    """计算相关性得分，与metrics.py保持一致"""
    N = len(expected_paths)
    actual_top_n = actual_results[:N]
    
    # 如果所有expected paths都在前N位，直接返回1.0
    if all(path in actual_top_n for path in expected_paths):
        return 1.0
        
    # 计算每个expected path的位置分数
    scores = []
    for exp_path in expected_paths:
        try:
            pos = actual_results.index(exp_path) + 1  # 1-based position
            score = 1 / (1 + (math.log2(pos) ** 2))
            scores.append(score)
        except ValueError:  # 如果路径没找到
            scores.append(0)
    
    return sum(scores) / len(expected_paths)

def calculate_completeness(expected: Set[str], actual: Set[str]) -> float:
    """计算完整性得分 (召回率)"""
    if not expected:
        return 0.0
    return len(expected.intersection(actual)) / len(expected)

def calculate_mrr(expected_paths: List[str], actual_results: List[str]) -> float:
    """计算MRR (Mean Reciprocal Rank) 得分
    只计算第一个相关结果的位置倒数
    """
    if not expected_paths or not actual_results:
        return 0.0
        
    # 转换为集合以加快查找
    expected_set = set(expected_paths)
    
    # 找到第一个相关结果的位置
    for i, path in enumerate(actual_results):
        if path in expected_set:
            return 1.0 / (i + 1)
            
    return 0.0

def evaluate_single_case(case: Dict[str, Any], mock_results: Optional[List[str]] = None) -> Dict[str, Any]:
    """评估单个测试用例"""
    expected_paths = [r.get("path", "") for r in case.get("expected_results", [])]
    
    # 获取实际结果
    actual_results = mock_results if mock_results is not None else search_code(case['query'])
    
    # 找到期望路径在实际结果中的位置
    found_positions = []
    for exp_path in expected_paths:
        try:
            pos = actual_results.index(exp_path) + 1  # 转换为1-based索引
        except ValueError:
            pos = 0  # 未找到
        found_positions.append(pos)
    
    # 计算相关性得分
    relevance_scores = calculate_relevance_scores(expected_paths, actual_results)
    
    # 计算完整性得分
    completeness = calculate_completeness(set(expected_paths), set(actual_results))
    
    # 计算MRR得分
    mrr_score = calculate_mrr(expected_paths, actual_results)
    
    # 计算综合得分 (0.3 * 相关性 + 0.3 * 完整性 + 0.4 * MRR)
    final_score = (
        relevance_scores * 0.3 +
        completeness * 0.3 +
        mrr_score * 0.4
    ) if expected_paths else None
    
    return {
        'query': case.get('query', ''),  # 添加查询字段
        'expected_paths': expected_paths,
        'actual_results': actual_results,
        'found_positions': found_positions,
        'relevance_score': relevance_scores if expected_paths else None,
        'completeness_score': completeness if expected_paths else None,
        'mrr_score': mrr_score if expected_paths else None,
        'final_score': final_score
    }

def evaluate_multiple_times(case: Dict[str, Any], times: int, delay: float = 0.5) -> List[Dict[str, Any]]:
    """多次评估同一个用例"""
    results = []
    for i in range(times):
        result = evaluate_single_case(case)
        results.append(result)
        print(f"\r评估进度: {i+1}/{times}, 当前得分: {result['final_score']:.3f}", end="")
        if i < times - 1:  # 不是最后一次
            time.sleep(delay)
    print()  # 换行
    return results

def calculate_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算多次评估的统计信息"""
    if not results:
        return {}
        
    metrics = ['relevance_score', 'completeness_score', 'mrr_score', 'final_score']
    stats = {}
    
    for metric in metrics:
        scores = [r[metric] for r in results if r[metric] is not None]
        if scores:
            stats[metric] = {
                'avg': mean(scores),
                'max': max(scores),
                'min': min(scores)
            }
    
    return stats

def print_detailed_results(last_result: Dict[str, Any], mock_results: Optional[List[str]] = None):
    """打印详细的评估结果"""
    if not last_result:
        print("没有可用的评估结果")
        return
        
    try:
        print("\n详细信息:")
        print(f"查询: {last_result.get('query', '未提供查询')}")
        print(f"期望路径数量: {len(last_result['expected_paths'])}")
        print(f"实际返回数量: {len(last_result['actual_results'])}")
        
        if last_result['final_score'] is not None:
            print("\n各项得分:")
            print(f"相关性得分: {last_result['relevance_score']:.4f}")
            print(f"完整性得分: {last_result['completeness_score']:.4f}")
            print(f"MRR得分: {last_result['mrr_score']:.4f}")
            print(f"综合得分: {last_result['final_score']:.4f}")
        
        print("\n期望结果详情:")
        actual_results = last_result['actual_results']
        for i, exp_path in enumerate(last_result['expected_paths']):
            try:
                pos = actual_results.index(exp_path) + 1
                status = f"在第{pos}位"
                score = 1.0 / (1.0 + (math.log2(pos) ** 2))
                mrr = 1.0 / pos
            except ValueError:
                status = "未找到"
                score = 0.0
                mrr = 0.0
            
            print(f"期望结果 {i+1}: {exp_path}")
            print(f"  状态: {status}")
            print(f"  相关性得分: {score:.4f}")
            print(f"  MRR得分: {mrr:.4f}")
        
        print("\n实际返回结果:")
        for i, result in enumerate(actual_results[:10], 1):  # 只显示前10个结果
            print(f"{i}. {result}")
    except Exception as e:
        print(f"输出详细信息时出错: {str(e)}")
        print("原始结果:", last_result)

def main():
    parser = argparse.ArgumentParser(description='调试单个测试用例或自定义查询')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--idx', type=str, help='要测试的用例idx')
    group.add_argument('--query', type=str, help='自定义查询语句')
    parser.add_argument('--dataset', type=str, default='test_dataset.json', help='测试数据集文件路径')
    parser.add_argument('--mock-results', type=str, nargs='+', default=None, help='模拟的检索结果路径列表')
    parser.add_argument('--expected', type=str, nargs='+', default=None, help='期望的结果路径（仅用于自定义查询）')
    parser.add_argument('--times', type=int, default=1, help='评估次数')
    parser.add_argument('--delay', type=float, default=0.5, help='每次评估之间的延迟（秒）')
    
    args = parser.parse_args()
    
    try:
        # 根据参数选择测试用例或创建自定义用例
        if args.idx:
            case = load_test_case(args.dataset, args.idx)
        else:
            case = create_custom_case(args.query, args.expected)
        
        print(f"\n测试用例信息:")
        print(f"ID: {case['idx']}")
        print(f"查询: {case['query']}")
        print(f"类别: {case['category']}")
        print(f"描述: {case['description']}")
        if case['expected_results']:
            print(f"期望结果: {[r['path'] for r in case['expected_results']]}")
        
        # 多次评估
        if args.times > 1:
            print(f"\n开始进行 {args.times} 次评估...")
            all_results = evaluate_multiple_times(case, args.times, args.delay)
            stats = calculate_statistics(all_results)
            
            # 打印统计信息
            print("\n统计信息:")
            metrics_zh = {
                'relevance_score': '相关性得分',
                'completeness_score': '完整性得分',
                'mrr_score': 'MRR得分',
                'final_score': '综合得分'
            }
            
            for metric, zh_name in metrics_zh.items():
                if metric in stats:
                    print(f"\n{zh_name}:")
                    print(f"  平均值: {stats[metric]['avg']:.3f}")
                    print(f"  最高分: {stats[metric]['max']:.3f}")
                    print(f"  最低分: {stats[metric]['min']:.3f}")
            
            # 显示最后一次的详细结果
            last_result = all_results[-1]
        else:
            # 单次评估
            last_result = evaluate_single_case(case, args.mock_results)
        
        # 显示最后一次评估的详细结果
        print_detailed_results(last_result, args.mock_results)
        
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 