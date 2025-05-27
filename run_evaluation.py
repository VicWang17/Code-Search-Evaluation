# -*- coding: utf-8 -*-
"""
代码检索评估系统主运行脚本
"""

import os
import sys
import argparse
import logging
import json
from datetime import datetime
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from config import (
    API_CONFIG, EVALUATION_CONFIG, CATEGORY_CONFIG, 
    PERFORMANCE_CONFIG, PATH_CONFIG, LOGGING_CONFIG,
    validate_config
)
from evaluator import CodeSearchEvaluator
from utils.result_formatter import format_evaluation_result, print_formatted_result, format_summary_with_explanations

def setup_logging(debug=False):
    """设置日志配置"""
    level = logging.DEBUG if debug else getattr(logging, LOGGING_CONFIG["level"])
    
    # 创建格式化器
    formatter = logging.Formatter(LOGGING_CONFIG["format"])
    
    # 设置根日志器
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 控制台处理器
    if LOGGING_CONFIG["console_output"]:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if LOGGING_CONFIG["file"]:
        file_handler = logging.FileHandler(
            LOGGING_CONFIG["file"], 
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

def create_directories():
    """创建必要的目录"""
    directories = [
        PATH_CONFIG["results_dir"],
        PATH_CONFIG["reports_dir"],
        PATH_CONFIG["history_dir"]
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def run_evaluation(args):
    """运行评估"""
    logger = logging.getLogger(__name__)
    
    try:
        # 验证配置
        validate_config()
        logger.info("配置验证通过")
        
        # 创建必要目录
        create_directories()
        
        # 构建完整配置
        config = {
            "api": API_CONFIG,
            "evaluation": EVALUATION_CONFIG,
            "categories": CATEGORY_CONFIG,
            "performance": PERFORMANCE_CONFIG,
            "paths": PATH_CONFIG
        }
        
        # 创建评估器
        logger.info("初始化代码检索评估器...")
        evaluator = CodeSearchEvaluator(config)
        
        # 测试API连接
        if not evaluator.api_client.test_connection():
            logger.error("API连接失败，请检查服务状态")
            return False
        
        logger.info("API连接正常")
        
        # 加载测试数据集
        dataset_path = args.dataset or PATH_CONFIG["test_dataset"]
        logger.info(f"加载测试数据集: {dataset_path}")
        
        if not os.path.exists(dataset_path):
            logger.error(f"测试数据集文件不存在: {dataset_path}")
            return False
        
        dataset = evaluator.load_test_dataset(dataset_path)
        
        # 如果指定了测试案例数量限制
        if args.limit and args.limit > 0:
            original_count = len(dataset["test_cases"])
            dataset["test_cases"] = dataset["test_cases"][:args.limit]
            logger.info(f"限制测试案例数量: {original_count} -> {len(dataset['test_cases'])}")
        
        # 如果指定了类别过滤
        if args.category:
            original_count = len(dataset["test_cases"])
            dataset["test_cases"] = [
                tc for tc in dataset["test_cases"] 
                if tc.get("category") == args.category
            ]
            logger.info(f"按类别 '{args.category}' 过滤: {original_count} -> {len(dataset['test_cases'])}")
        
        if not dataset["test_cases"]:
            logger.error("没有测试案例需要评估")
            return False
        
        # 执行评估
        logger.info("开始执行代码检索评估...")
        results = evaluator.evaluate_dataset(dataset)
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存最新结果
        latest_path = PATH_CONFIG["latest_result"]
        evaluator.save_results(results, latest_path)
        
        # 保存历史结果
        if args.save_history:
            history_path = os.path.join(
                PATH_CONFIG["history_dir"],
                f"evaluation_{timestamp}.json"
            )
            evaluator.save_results(results, history_path)
            logger.info(f"历史结果已保存: {history_path}")
        
        # 生成报告
        if args.generate_report:
            generate_reports(results, timestamp)
        
        # 显示简要结果
        show_summary(results)
        
        # 识别问题查询
        if args.show_problems:
            show_problematic_queries(evaluator)
        
        logger.info("评估完成!")
        return True
        
    except Exception as e:
        logger.error(f"评估过程中发生错误: {e}")
        if args.debug:
            logger.exception("详细错误信息:")
        return False

def generate_reports(results, timestamp):
    """生成评估报告"""
    logger = logging.getLogger(__name__)
    
    try:
        # 生成Markdown报告
        md_report_path = os.path.join(
            PATH_CONFIG["reports_dir"],
            f"evaluation_report_{timestamp}.md"
        )
        
        generate_markdown_report(results, md_report_path)
        logger.info(f"Markdown报告已生成: {md_report_path}")
        
        # 生成简要报告
        summary_path = os.path.join(
            PATH_CONFIG["reports_dir"],
            f"summary_{timestamp}.txt"
        )
        
        generate_summary_report(results, summary_path)
        logger.info(f"简要报告已生成: {summary_path}")
        
    except Exception as e:
        logger.error(f"生成报告失败: {e}")

def generate_markdown_report(results, output_path):
    """生成Markdown格式的详细报告"""
    summary = results["summary_metrics"]
    meta = results["meta"]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 代码检索评估报告\n\n")
        
        # 基本信息
        f.write("## 评估概览\n\n")
        f.write(f"- **评估时间**: {meta['evaluation_time']}\n")
        f.write(f"- **测试案例总数**: {meta['total_test_cases']}\n")
        f.write(f"- **成功评估**: {meta['successful_evaluations']}\n")
        f.write(f"- **失败评估**: {meta['failed_evaluations']}\n")
        f.write(f"- **成功率**: {summary['evaluation_statistics']['success_rate']:.1%}\n\n")
        
        # 整体性能
        f.write("## 整体性能指标\n\n")
        overall = summary["overall_performance"]
        f.write(f"- **平均精确率**: {overall['avg_precision']:.3f}\n")
        f.write(f"- **平均召回率**: {overall['avg_recall']:.3f}\n")
        f.write(f"- **平均F1分数**: {overall['avg_f1_score']:.3f}\n")
        f.write(f"- **平均MRR**: {overall['avg_mrr']:.3f}\n")
        f.write(f"- **平均NDCG**: {overall['avg_ndcg']:.3f}\n\n")
        
        # Top-K性能
        f.write("## Top-K准确率\n\n")
        top_k = summary["top_k_performance"]
        for k, accuracy in top_k.items():
            f.write(f"- **{k.replace('_', '-').title()}**: {accuracy:.3f}\n")
        f.write("\n")
        
        # 路径匹配性能
        f.write("## 路径匹配分析\n\n")
        path_matching = summary["path_matching_performance"]
        f.write(f"- **平均路径匹配分数**: {path_matching['avg_path_match_score']:.3f}\n")
        f.write(f"- **精确匹配总数**: {path_matching['total_exact_matches']}\n")
        f.write(f"- **部分匹配总数**: {path_matching['total_partial_matches']}\n")
        f.write(f"- **精确匹配率**: {path_matching['exact_match_rate']:.3f}\n\n")
        
        # 分类别性能
        if "category_metrics" in results:
            f.write("## 分类别性能\n\n")
            for category, metrics in results["category_metrics"].items():
                f.write(f"### {metrics['name']}\n\n")
                f.write(f"- **测试案例数**: {metrics['count']}\n")
                f.write(f"- **权重**: {metrics['weight']}\n")
                f.write(f"- **平均精确率**: {metrics['avg_precision']:.3f}\n")
                f.write(f"- **平均召回率**: {metrics['avg_recall']:.3f}\n")
                f.write(f"- **平均F1分数**: {metrics['avg_f1']:.3f}\n")
                f.write(f"- **加权分数**: {metrics['weighted_score']:.3f}\n\n")

def generate_summary_report(results, output_path):
    """生成简要文本报告"""
    summary = results["summary_metrics"]
    meta = results["meta"]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("代码检索评估结果简要报告\n")
        f.write("=" * 40 + "\n\n")
        
        f.write(f"评估时间: {meta['evaluation_time']}\n")
        f.write(f"测试案例: {meta['total_test_cases']} (成功: {meta['successful_evaluations']})\n")
        f.write(f"成功率: {summary['evaluation_statistics']['success_rate']:.1%}\n\n")
        
        overall = summary["overall_performance"]
        f.write("整体性能:\n")
        f.write(f"  精确率: {overall['avg_precision']:.3f}\n")
        f.write(f"  召回率: {overall['avg_recall']:.3f}\n")
        f.write(f"  F1分数: {overall['avg_f1_score']:.3f}\n")
        f.write(f"  MRR: {overall['avg_mrr']:.3f}\n")

def show_summary(results):
    """显示评估结果摘要"""
    print("\n" + "="*60)
    print("📊 代码检索评估结果摘要")
    print("="*60)
    
    meta = results["meta"]
    summary = results["summary_metrics"]
    
    print(f"⏰ 评估时间: {meta['evaluation_time']}")
    print(f"📋 测试案例: {meta['total_test_cases']} (成功: {meta['successful_evaluations']})")
    print(f"✅ 成功率: {summary['evaluation_statistics']['success_rate']:.1%}")
    
    # 使用格式化工具添加详细解释
    formatted_summary = format_summary_with_explanations(summary)
    
    print("\n🎯 新评估框架整体表现:")
    if "new_framework_performance" in summary:
        new_framework = summary["new_framework_performance"]
        weights = new_framework.get("framework_weights", {})
        
        # 总分
        total_score = new_framework["avg_total_score"]
        total_interp = get_total_score_interpretation(total_score)
        print(f"  {total_interp['color']} 平均综合评分: {total_score:.3f} ({total_interp['level']})")
        print(f"     💡 {total_interp.get('advice', '')}")
        
        # 三个维度
        dimensions = [
            ("avg_relevance", "平均相关性", weights.get("relevance", 0.5)),
            ("avg_completeness", "平均全面性", weights.get("completeness", 0.3)),
            ("avg_usability", "平均可用性", weights.get("usability", 0.2))
        ]
        
        for metric_key, metric_name, weight in dimensions:
            value = new_framework.get(metric_key, 0.0)
            interp = get_score_interpretation(value)
            print(f"  {interp['color']} {metric_name}: {value:.3f} ({interp['level']}) - 权重: {weight*100:.0f}%")
    
    # 传统指标对比
    if "traditional_performance" in summary:
        traditional = summary["traditional_performance"]
        print(f"\n📈 传统指标对比:")
        print(f"  📐 平均精确率: {traditional['avg_precision']:.3f}")
        print(f"  🎪 平均召回率: {traditional['avg_recall']:.3f}")
        print(f"  ⚖️ 平均F1分数: {traditional['avg_f1_score']:.3f}")

def get_total_score_interpretation(total_score):
    """获取总分解释"""
    if total_score >= 0.8:
        return {"level": "优秀", "color": "🟢", "advice": "综合表现优秀，检索系统可以投入使用"}
    elif total_score >= 0.6:
        return {"level": "良好", "color": "🟡", "advice": "综合表现良好，建议针对薄弱环节进一步优化"}
    elif total_score >= 0.4:
        return {"level": "一般", "color": "🟠", "advice": "综合表现一般，需要重点改进相关性和全面性"}
    elif total_score >= 0.2:
        return {"level": "较差", "color": "🔴", "advice": "综合表现较差，建议重新审视检索策略"}
    else:
        return {"level": "很差", "color": "⚫", "advice": "综合表现很差，需要重新设计检索系统"}
    
    print("\n📈 Top-K准确率:")
    top_k = summary["top_k_performance"]
    for k, accuracy in top_k.items():
        interp = get_score_interpretation(accuracy)
        print(f"  {interp['color']} {k.replace('_', '-').title()}: {accuracy:.3f} ({interp['level']})")
    
    # 路径匹配性能
    if "path_matching_performance" in summary:
        path_perf = summary["path_matching_performance"]
        print(f"\n🔍 路径匹配性能:")
        print(f"  📈 平均匹配分数: {path_perf['avg_path_match_score']:.3f}")
        print(f"  ✅ 精确匹配总数: {path_perf['total_exact_matches']}")
        print(f"  🎯 精确匹配率: {path_perf['exact_match_rate']:.3f}")
    
    # 分数分布
    if "score_distribution" in summary:
        score_dist = summary["score_distribution"]
        print(f"\n📊 检索分数分析:")
        print(f"  📈 平均结果分数: {score_dist['avg_result_score']:.3f}")
        print(f"  🔝 平均最高分: {score_dist['avg_max_score']:.3f}")
        print(f"  📏 分数一致性: {score_dist['score_consistency']:.3f}")
    
    print("\n" + "="*60)

def get_score_interpretation(score):
    """获取分数解释（从result_formatter导入）"""
    if score >= 0.8:
        return {"level": "优秀", "color": "🟢", "description": "表现很好"}
    elif score >= 0.6:
        return {"level": "良好", "color": "🟡", "description": "表现不错，有改进空间"}
    elif score >= 0.4:
        return {"level": "一般", "color": "🟠", "description": "表现一般，需要优化"}
    elif score >= 0.2:
        return {"level": "较差", "color": "🔴", "description": "表现较差，急需改进"}
    else:
        return {"level": "很差", "color": "⚫", "description": "表现很差，需要重新设计"}

def show_problematic_queries(evaluator):
    """显示问题查询"""
    problematic = evaluator.get_problematic_queries(threshold=0.4)
    
    if not problematic:
        print("\n✅ 没有发现问题查询 (总分 < 0.4)")
        return
    
    print(f"\n⚠️  发现 {len(problematic)} 个问题查询 (总分 < 0.4):")
    print("-" * 60)
    
    for i, query in enumerate(problematic[:5]):  # 只显示前5个
        print(f"{i+1}. {query['query']} (总分: {query['total_score']:.3f})")
        print(f"   类别: {query['category']}")
        print(f"   详情: 相关性={query['relevance']:.3f}, 全面性={query['completeness']:.3f}, 可用性={query['usability']:.3f}")
        print(f"   问题: {', '.join(query['issues'])}")
        print()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="代码检索评估系统")
    
    parser.add_argument(
        "--dataset", "-d",
        type=str,
        help="测试数据集文件路径 (默认: test_dataset.json)"
    )
    
    parser.add_argument(
        "--limit", "-l",
        type=int,
        help="限制测试案例数量"
    )
    
    parser.add_argument(
        "--category", "-c",
        type=str,
        choices=["style", "function", "layout", "api"],
        help="按类别过滤测试案例"
    )
    
    parser.add_argument(
        "--generate-report", "-r",
        action="store_true",
        help="生成详细报告"
    )
    
    parser.add_argument(
        "--save-history",
        action="store_true",
        help="保存历史结果"
    )
    
    parser.add_argument(
        "--show-problems", "-p",
        action="store_true",
        help="显示问题查询"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.debug)
    
    # 运行评估
    success = run_evaluation(args)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 