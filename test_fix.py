# -*- coding: utf-8 -*-
"""
测试路径匹配修复的简单脚本
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from utils.metrics import EvaluationMetrics

def print_separator(title):
    """打印分隔线和标题"""
    print("\n" + "="*60)
    print(f"{title}")
    print("="*60)

def explain_path_matching_result(result):
    """详细解释路径匹配结果"""
    print("\n路径匹配详细分析:")
    print(f"  总匹配分数: {result['total_score']:.3f}")
    print("     ├─ 分数范围: 0.0-1.0 (越高越好)")
    print("     └─ 计算公式: (精确匹配×1.0 + 部分匹配×0.7 + 扩展名匹配×0.3) / 期望结果数")
    
    print(f"\n  精确匹配: {result['exact_matches']} 个")
    print("     └─ 文件路径完全相同")
    
    print(f"  部分匹配: {result['partial_matches']} 个") 
    print("     └─ 文件名相同但路径不同，或路径有重叠部分")
    
    print(f"  扩展名匹配: {result['extension_matches']} 个")
    print("     └─ 文件扩展名相同但文件名不同")
    
    print(f"  期望结果总数: {result['total_expected']} 个")

def explain_new_framework_metrics(metrics):
    """解释新评估框架指标"""
    print("\n新评估框架指标:")
    print(f"  总分: {metrics['total_score']:.3f}")
    print(f"  相关性 (30%权重): {metrics['relevance']:.3f}")
    print(f"  全面性 (30%权重): {metrics['completeness']:.3f}")
    print(f"  可用性 (40%权重): {metrics['usability']:.3f}")
    
    # 详细解释
    details = metrics.get("details", {})
    print("\n详细分析:")
    print(f"  前{details.get('k', 10)}个结果中相关数: {details.get('relevant_in_top_k', 0)}")
    print(f"  总相关结果数: {details.get('total_relevant', 0)}")
    print(f"  MRR (可用性): {details.get('mrr', 0.0):.3f}")
    
    # 权重分解
    weights = details.get("weights", {})
    print(f"\n权重分解:")
    print(f"  相关性权重: {weights.get('relevance', 0.5)*100:.0f}%")
    print(f"  全面性权重: {weights.get('completeness', 0.3)*100:.0f}%")
    print(f"  可用性权重: {weights.get('usability', 0.2)*100:.0f}%")

def test_path_matching():
    """测试路径匹配评分"""
    # 测试数据
    actual_results = [
        {"path": "src/components/Button.vue"},
        {"path": "src/components/Input.vue"},
        {"path": "src/utils/helpers.js"}
    ]
    expected_results = [
        {"path": "src/components/Button.vue"},
        {"path": "src/components/Input.vue"}
    ]
    
    # 使用默认配置初始化EvaluationMetrics
    default_config = {
        "default_k": 10
    }
    metrics = EvaluationMetrics(default_config)
    
    # 计算路径匹配评分
    score = metrics.calculate_path_matching_score(actual_results, expected_results)
    
    # 验证结果
    assert score["total_score"] == 1.0  # 两个完全匹配
    assert score["exact_matches"] == 2
    assert score["partial_matches"] == 0
    assert score["extension_matches"] == 0
    
    print_separator("代码检索评估结果分析")
    
    print("正在测试路径匹配功能...")
    
    print("\n测试数据说明:")
    print("  查询: '积分商品列表样式'")
    print("  API返回结果:")
    for i, result in enumerate(actual_results, 1):
        print(f"    {i}. {result['path']}")
    
    print("  期望结果:")
    for i, result in enumerate(expected_results, 1):
        print(f"    {i}. {result['path']}")
    
    try:
        # 测试路径匹配
        result = metrics.calculate_path_matching_score(
            actual_results, 
            expected_results
        )
        
        print("\n路径匹配计算成功!")
        explain_path_matching_result(result)
        
        # 测试新评估框架指标
        framework_metrics = metrics.calculate_new_framework_metrics(actual_results, expected_results, k=10)
        explain_new_framework_metrics(framework_metrics)
        
        # 额外的建议
        print_separator("改进建议")
        
        total_score = framework_metrics['total_score']
        if total_score < 0.6:
            print("改进建议:")
            if framework_metrics['relevance'] < 0.5:
                print("  • 相关性较低: 前k个结果中相关结果太少")
                print("  • 建议: 提高匹配阈值或改进相似度计算")
            
            if framework_metrics['completeness'] < 0.5:
                print("  • 全面性不足: 遗漏了太多相关结果")
                print("  • 建议: 扩展搜索范围或使用同义词匹配")
            
            if framework_metrics['usability'] < 0.5:
                print("  • 可用性较差: 相关结果排名太靠后")
                print("  • 建议: 优化排序算法或调整相关性权重")
        
        if result['exact_matches'] == 0:
            print("  • 没有精确匹配: 检查文件路径格式是否一致")
            print("  • 建议: 统一路径分隔符（\\或/）和大小写")
        
        print("\n测试完成! 系统运行正常")
        return True
        
    except Exception as e:
        print(f"路径匹配测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_path_matching()
    if success:
        print_separator("总结")
        print("修复验证成功!")
        print("exact_match 键错误已解决")
        print("评估系统可以正常使用")
        print("\n接下来您可以:")
        print("  1. 运行完整评估: python run_evaluation.py")
        print("  2. 运行快速测试: python quick_start.py")
        print("  3. 查看详细文档: USAGE.md")
    else:
        print("\n修复验证失败，请检查错误信息") 