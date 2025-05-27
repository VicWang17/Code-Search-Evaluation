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
    print(f"📊 {title}")
    print("="*60)

def explain_path_matching_result(result):
    """详细解释路径匹配结果"""
    print("\n🔍 路径匹配详细分析:")
    print(f"  📈 总匹配分数: {result['total_score']:.3f}")
    print("     ├─ 分数范围: 0.0-1.0 (越高越好)")
    print("     └─ 计算公式: (精确匹配×1.0 + 部分匹配×0.7 + 扩展名匹配×0.3) / 期望结果数")
    
    print(f"\n  ✅ 精确匹配: {result['exact_matches']} 个")
    print("     └─ 文件路径完全相同")
    
    print(f"  🎯 部分匹配: {result['partial_matches']} 个") 
    print("     └─ 文件名相同但路径不同，或路径有重叠部分")
    
    print(f"  📄 扩展名匹配: {result['extension_matches']} 个")
    print("     └─ 文件扩展名相同但文件名不同")
    
    print(f"  📋 期望结果总数: {result['total_expected']} 个")

def explain_new_framework_metrics(framework_metrics):
    """详细解释新评估框架指标"""
    print("\n🎯 新评估框架分析:")
    
    details = framework_metrics.get("details", {})
    weights = details.get("weights", {})
    
    print(f"  🏆 综合评分: {framework_metrics['total_score']:.3f}")
    print("     ├─ 计算公式: 相关性×0.5 + 全面性×0.3 + 可用性×0.2")
    print(f"     └─ 评估范围: 前{details.get('k', 10)}个结果")
    
    print(f"\n  📊 相关性 (权重{weights.get('relevance', 0.5)*100:.0f}%): {framework_metrics['relevance']:.3f}")
    print("     ├─ 含义: 前k个结果中相关结果的比例")
    print(f"     ├─ 计算: {details.get('relevant_in_top_k', 0)} / {details.get('k', 10)}")
    if framework_metrics['relevance'] >= 0.7:
        print("     └─ 评价: 🟢 优秀 - 返回的结果大部分都相关")
    elif framework_metrics['relevance'] >= 0.5:
        print("     └─ 评价: 🟡 良好 - 返回结果有一定相关性")
    else:
        print("     └─ 评价: 🔴 较差 - 返回了太多不相关结果")
    
    print(f"\n  📈 全面性 (权重{weights.get('completeness', 0.3)*100:.0f}%): {framework_metrics['completeness']:.3f}")
    print("     ├─ 含义: 找到了多少比例的相关结果")
    print(f"     ├─ 计算: {details.get('relevant_in_top_k', 0)} / {details.get('total_relevant', 0)}")
    if framework_metrics['completeness'] >= 0.7:
        print("     └─ 评价: 🟢 优秀 - 找到了大部分相关结果")
    elif framework_metrics['completeness'] >= 0.5:
        print("     └─ 评价: 🟡 良好 - 找到了部分相关结果")
    else:
        print("     └─ 评价: 🔴 较差 - 遗漏了很多相关结果")
    
    print(f"\n  🎯 可用性 (权重{weights.get('usability', 0.2)*100:.0f}%): {framework_metrics['usability']:.3f}")
    print("     ├─ 含义: 第一个相关结果的排名质量 (MRR)")
    print("     ├─ 计算: 第一个相关结果排名的倒数")
    if framework_metrics['usability'] >= 0.7:
        print("     └─ 评价: 🟢 优秀 - 相关结果排名很靠前")
    elif framework_metrics['usability'] >= 0.5:
        print("     └─ 评价: 🟡 良好 - 相关结果排名较靠前")
    else:
        print("     └─ 评价: 🔴 较差 - 相关结果排名太靠后")

def explain_traditional_metrics(precision, recall, f1):
    """解释传统指标 (对比参考)"""
    print("\n📈 传统指标对比:")
    
    print(f"  📐 传统精确率: {precision:.3f}")
    print(f"  🎪 传统召回率: {recall:.3f}")
    print(f"  ⚖️ 传统F1分数: {f1:.3f}")
    print("     └─ 注: 传统指标基于所有检索结果，新框架基于前k个结果")

def test_path_matching():
    """测试路径匹配功能"""
    print_separator("代码检索评估结果分析")
    
    print("🔄 正在测试路径匹配功能...")
    
    # 创建评估指标实例
    metrics = EvaluationMetrics()
    
    # 模拟API返回结果
    actual_results = [
        {"path": "pages\\points\\exchange.vue", "score": 0.8},
        {"path": "pages\\coupon\\list.vue", "score": 0.6},
        {"path": "api\\goods.js", "score": 0.4}
    ]
    
    # 期望结果
    expected_results = [
        {"path": "pages\\points\\exchange.vue", "relevance_score": 1.0},
        {"path": "pages\\settlement\\style.scss", "relevance_score": 0.5}
    ]
    
    print("\n📋 测试数据说明:")
    print("  🔍 查询: '积分商品列表样式'")
    print("  📤 API返回结果:")
    for i, result in enumerate(actual_results, 1):
        print(f"    {i}. {result['path']} (分数: {result['score']})")
    
    print("  🎯 期望结果:")
    for i, result in enumerate(expected_results, 1):
        print(f"    {i}. {result['path']} (相关性: {result['relevance_score']})")
    
    # 测试配置格式的权重参数（模拟config.py中的格式）
    config_weights = {
        "exact_match_weight": 1.0,
        "partial_match_weight": 0.7,
        "extension_match_weight": 0.3
    }
    
    try:
        # 测试路径匹配
        result = metrics.calculate_path_matching_score(
            actual_results, 
            expected_results, 
            config_weights
        )
        
        print("\n✅ 路径匹配计算成功!")
        explain_path_matching_result(result)
        
        # 测试新评估框架指标
        framework_metrics = metrics.calculate_new_framework_metrics(actual_results, expected_results, k=10)
        explain_new_framework_metrics(framework_metrics)
        
        # 测试传统指标 (对比)
        precision, recall, f1 = metrics.calculate_precision_recall_f1(actual_results, expected_results)
        explain_traditional_metrics(precision, recall, f1)
        
        # 额外的建议
        print_separator("改进建议")
        
        total_score = framework_metrics['total_score']
        if total_score < 0.6:
            print("🔧 改进建议:")
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
        
        print("\n🎉 测试完成! 系统运行正常")
        return True
        
    except Exception as e:
        print(f"❌ 路径匹配测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_path_matching()
    if success:
        print_separator("总结")
        print("🎉 修复验证成功!")
        print("✅ exact_match 键错误已解决")
        print("✅ 评估系统可以正常使用")
        print("\n📚 接下来您可以:")
        print("  1. 运行完整评估: python run_evaluation.py")
        print("  2. 运行快速测试: python quick_start.py")
        print("  3. 查看详细文档: USAGE.md")
    else:
        print("\n❌ 修复验证失败，请检查错误信息") 