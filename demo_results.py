# -*- coding: utf-8 -*-
"""
演示改进后的结果注释功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from utils.result_formatter import format_evaluation_result, print_formatted_result
from utils.metrics import EvaluationMetrics

def create_demo_result():
    """创建一个演示用的评估结果"""
    return {
        "idx": "demo-001",
        "query": "积分商品列表样式",
        "category": "style",
        "weight": 1.0,
        "description": "测试积分兑换页面商品列表的CSS样式检索",
        
        # 新评估框架指标
        "total_score": 0.72,
        "relevance": 0.8,
        "completeness": 0.6,
        "usability": 0.9,
        
        # 框架详情
        "framework_metrics": {
            "total_score": 0.72,
            "relevance": 0.8,
            "completeness": 0.6,
            "usability": 0.9,
            "details": {
                "relevant_in_top_k": 8,
                "total_relevant": 2,
                "k": 10,
                "mrr": 0.9,
                "weights": {"relevance": 0.5, "completeness": 0.3, "usability": 0.2}
            }
        },
        
        # 传统指标 (保留)
        "precision": 0.6,
        "recall": 0.8,
        "f1_score": 0.686,
        
        # 路径匹配
        "path_matching": {
            "total_score": 0.75,
            "exact_matches": 1,
            "partial_matches": 1,
            "extension_matches": 0,
            "total_expected": 2
        },
        
        # Top-K准确率
        "top_k_accuracy": {
            1: 1.0,
            3: 0.8,
            5: 0.6,
            10: 0.5
        },
        
        # 分数分析
        "score_analysis": {
            "max_score": 0.85,
            "min_score": 0.32,
            "avg_score": 0.58,
            "std_score": 0.18,
            "score_gap": 0.53,
            "top_3_avg": 0.72
        },
        
        # 高级指标
        "mrr": 0.8,
        "ndcg": 0.75,
        "diversity": 0.6,
        
        # 原始数据
        "expected_results": [
            {"path": "pages\\points\\exchange.vue", "relevance_score": 1.0},
            {"path": "pages\\coupon\\list.vue", "relevance_score": 0.7}
        ],
        "actual_results": [
            {"path": "pages\\points\\exchange.vue", "score": 0.85},
            {"path": "pages\\coupon\\list.vue", "score": 0.72},
            {"path": "components\\goods-card.vue", "score": 0.58},
            {"path": "api\\goods.js", "score": 0.32}
        ],
        "total_results": 4,
        
        # 元数据
        "timestamp": 1640995200.0,
        "success": True
    }

def demo_formatted_results():
    """演示格式化结果功能"""
    print("🎯 代码检索评估结果注释演示")
    print("=" * 60)
    
    # 创建演示数据
    demo_result = create_demo_result()
    
    print("\n📋 原始结果 (简化版):")
    print(f"  查询: {demo_result['query']}")
    print(f"  🏆 综合评分: {demo_result['total_score']:.3f}")
    print(f"  📊 相关性: {demo_result['relevance']:.3f}")
    print(f"  📈 全面性: {demo_result['completeness']:.3f}")
    print(f"  🎯 可用性: {demo_result['usability']:.3f}")
    print(f"  (传统F1分数: {demo_result['f1_score']:.3f})")
    
    print("\n" + "="*60)
    print("🔄 正在添加详细注释...")
    
    # 格式化结果
    formatted_result = format_evaluation_result(demo_result)
    
    print("\n📊 格式化后的详细结果:")
    print_formatted_result(formatted_result, show_details=True)
    
    print("\n" + "="*60)
    print("💡 注释功能说明:")
    print("✅ 每个指标都有详细的含义解释")
    print("✅ 提供计算公式和取值范围")
    print("✅ 根据分数给出评价等级和颜色标识")
    print("✅ 包含具体的改进建议")
    print("✅ 路径匹配有详细的分类统计")
    print("✅ 高级指标有专业的解释说明")
    
    return formatted_result

def demo_different_scores():
    """演示不同分数等级的显示效果"""
    print("\n\n🎨 不同评价等级演示")
    print("=" * 60)
    
    test_scores = [
        {"name": "优秀案例", "total": 0.85, "relevance": 0.9, "completeness": 0.8, "usability": 0.9},
        {"name": "良好案例", "total": 0.65, "relevance": 0.7, "completeness": 0.6, "usability": 0.7},
        {"name": "一般案例", "total": 0.45, "relevance": 0.5, "completeness": 0.4, "usability": 0.5},
        {"name": "较差案例", "total": 0.25, "relevance": 0.3, "completeness": 0.2, "usability": 0.3},
        {"name": "很差案例", "total": 0.05, "relevance": 0.1, "completeness": 0.05, "usability": 0.1}
    ]
    
    for test_case in test_scores:
        demo_result = create_demo_result()
        demo_result["query"] = test_case["name"]
        demo_result["total_score"] = test_case["total"]
        demo_result["relevance"] = test_case["relevance"]
        demo_result["completeness"] = test_case["completeness"]
        demo_result["usability"] = test_case["usability"]
        
        formatted_result = format_evaluation_result(demo_result)
        
        print(f"\n📊 {test_case['name']}:")
        if "framework_explanation" in formatted_result:
            framework = formatted_result["framework_explanation"]
            total_info = framework["total_score"]
            interp = total_info["interpretation"]
            print(f"  {interp['color']} 综合评分: {total_info['value']:.3f} ({interp['level']})")
            print(f"  💡 建议: {interp.get('advice', '无特殊建议')}")

def main():
    """主演示函数"""
    print("🚀 代码检索评估结果注释系统演示")
    print("=" * 80)
    
    # 演示基本格式化功能
    formatted_result = demo_formatted_results()
    
    # 演示不同分数等级
    demo_different_scores()
    
    print("\n\n🎉 演示完成!")
    print("=" * 80)
    print("📚 现在您可以:")
    print("  1. 在实际评估中看到这些详细注释")
    print("  2. 更容易理解每个指标的含义")
    print("  3. 根据颜色和等级快速判断性能")
    print("  4. 获得具体的改进建议")
    print("\n💡 提示: 运行 'python run_evaluation.py' 查看完整评估的注释效果")

if __name__ == "__main__":
    main() 