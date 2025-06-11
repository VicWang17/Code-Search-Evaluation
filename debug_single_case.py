import json
import argparse
from typing import List, Dict, Any, Set
import sys
from config import API_CONFIG
from utils.api_client import create_api_client

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

def calculate_relevance_score(actual_pos: int) -> float:
    """计算位置相关性得分"""
    if actual_pos <= 0:  # 未找到结果
        return 0.0
    return 1.0 / (1.0 + (2.0 * pow(max(0, actual_pos - 1), 2)))

def calculate_completeness(expected: Set[str], actual: Set[str]) -> float:
    """计算完整性得分 (召回率)"""
    if not expected:
        return 0.0
    return len(expected.intersection(actual)) / len(expected)

def calculate_mrr(expected_paths: List[str], actual_results: List[str]) -> float:
    """计算MRR (Mean Reciprocal Rank) 得分"""
    if not expected_paths or not actual_results:
        return 0.0
    
    reciprocal_ranks = []
    for exp_path in expected_paths:
        try:
            rank = actual_results.index(exp_path) + 1  # 1-based rank
            reciprocal_ranks.append(1.0 / rank)
        except ValueError:
            reciprocal_ranks.append(0.0)
    
    return sum(reciprocal_ranks) / len(expected_paths)

def evaluate_single_case(case: Dict[str, Any], mock_results: List[str] = None) -> Dict[str, Any]:
    """评估单个测试用例的结果"""
    expected_paths = [r['path'] for r in case['expected_results']]
    
    # 如果没有提供mock结果，则调用API获取结果
    actual_results = mock_results if mock_results is not None else search_code(case['query'])
    
    found_positions = []
    # 记录每个期望结果在实际结果中的位置
    for exp_path in expected_paths:
        try:
            pos = actual_results.index(exp_path) + 1  # 1-based position
            found_positions.append(pos)
        except ValueError:
            found_positions.append(0)  # 未找到则记为0
    
    # 计算相关性得分
    relevance_scores = [calculate_relevance_score(pos) for pos in found_positions]
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
    
    # 计算完整性得分
    expected_set = set(expected_paths)
    actual_set = set(actual_results)
    completeness = calculate_completeness(expected_set, actual_set)
    
    # 计算MRR得分
    mrr_score = calculate_mrr(expected_paths, actual_results)
    
    # 计算综合得分
    final_score = (avg_relevance + completeness + mrr_score) / 3 if expected_paths else None
    
    return {
        'relevance_score': avg_relevance if expected_paths else None,
        'completeness_score': completeness if expected_paths else None,
        'mrr_score': mrr_score if expected_paths else None,
        'final_score': final_score,
        'found_positions': found_positions,
        'expected_paths': expected_paths,
        'actual_results': actual_results[:10]  # 只显示前10个结果
    }

def main():
    parser = argparse.ArgumentParser(description='调试单个测试用例或自定义查询')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--idx', type=str, help='要测试的用例idx')
    group.add_argument('--query', type=str, help='自定义查询语句')
    parser.add_argument('--dataset', type=str, default='test_dataset.json', help='测试数据集文件路径')
    parser.add_argument('--mock-results', type=str, nargs='+', default=None, help='模拟的检索结果路径列表')
    parser.add_argument('--expected', type=str, nargs='+', default=None, help='期望的结果路径（仅用于自定义查询）')
    
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
        
        # 评估结果
        results = evaluate_single_case(case, args.mock_results)
        
        # 只有在有期望结果时才显示评分
        if case['expected_results']:
            print("\n评分结果:")
            print(f"相关性得分: {results['relevance_score']:.3f}")
            print(f"完整性得分: {results['completeness_score']:.3f}")
            print(f"MRR得分: {results['mrr_score']:.3f}")
            print(f"综合得分: {results['final_score']:.3f}")
            
            print("\n详细信息:")
            for i, (exp_path, pos) in enumerate(zip(results['expected_paths'], results['found_positions'])):
                status = f"在第{pos}位" if pos > 0 else "未找到"
                score = calculate_relevance_score(pos)
                mrr = 1.0 / pos if pos > 0 else 0.0
                print(f"期望结果 {i+1}: {exp_path}")
                print(f"  - 状态: {status}")
                print(f"  - 位置得分: {score:.3f}")
                print(f"  - 倒数排名得分: {mrr:.3f}")
        
        print("\n实际返回结果(前10个):")
        for i, path in enumerate(results['actual_results'], 1):
            print(f"{i}. {path}")
            
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 