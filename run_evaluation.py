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
import numpy as np
import plotly.graph_objects as go
import re

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
    # 在debug模式下使用INFO级别，否则使用WARNING级别
    level = logging.INFO if debug else logging.WARNING
    
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

def save_history_score(results, timestamp):
    """保存历史分数"""
    logger = logging.getLogger(__name__)
    
    try:
        # 创建历史分数文件
        history_scores_path = os.path.join(PATH_CONFIG["history_dir"], "scores_history.json")
        
        # 读取现有历史记录
        if os.path.exists(history_scores_path):
            with open(history_scores_path, 'r', encoding='utf-8') as f:
                history_scores = json.load(f)
        else:
            history_scores = []
        
        # 提取当前评估的分数
        summary = results["summary_metrics"]
        if "new_framework_performance" in summary:
            new_framework = summary["new_framework_performance"]
            current_score = {
                "timestamp": timestamp,
                "total_score": new_framework["avg_total_score"],
                "relevance": new_framework["avg_relevance"],
                "completeness": new_framework["avg_completeness"],
                "usability": new_framework["avg_usability"]
            }
            
            # 添加到历史记录
            history_scores.append(current_score)
            
            # 保存更新后的历史记录
            with open(history_scores_path, 'w', encoding='utf-8') as f:
                json.dump(history_scores, f, ensure_ascii=False, indent=2)
            
            logger.info(f"历史分数已保存: {history_scores_path}")
            return True
            
    except Exception as e:
        logger.error(f"保存历史分数失败: {e}")
        if args.debug:
            logger.exception("详细错误信息:")
        return False

def generate_history_chart():
    """生成历史分数折线图"""
    logger = logging.getLogger(__name__)
    
    try:
        # 读取历史分数
        history_scores_path = os.path.join(PATH_CONFIG["history_dir"], "scores_history.json")
        if not os.path.exists(history_scores_path):
            logger.error("历史分数文件不存在")
            return False
            
        with open(history_scores_path, 'r', encoding='utf-8') as f:
            history_scores = json.load(f)
        
        if not history_scores:
            logger.error("没有历史分数数据")
            return False
        
        # 创建图表
        fig = go.Figure()
        
        # 添加总分折线
        fig.add_trace(go.Scatter(
            x=[score["timestamp"] for score in history_scores],
            y=[score["total_score"] for score in history_scores],
            mode='lines+markers',
            name='总分',
            line=dict(color='#1f77b4', width=2)
        ))
        
        # 添加各维度折线
        dimensions = [
            ("relevance", "相关性", "#ff7f0e"),
            ("completeness", "全面性", "#2ca02c"),
            ("usability", "可用性", "#d62728")
        ]
        
        for metric, name, color in dimensions:
            fig.add_trace(go.Scatter(
                x=[score["timestamp"] for score in history_scores],
                y=[score[metric] for score in history_scores],
                mode='lines+markers',
                name=name,
                line=dict(color=color, width=2)
            ))
        
        # 设置图表布局
        fig.update_layout(
            title="评估分数历史趋势",
            xaxis_title="评估时间",
            yaxis_title="分数",
            yaxis=dict(range=[0, 1]),
            showlegend=True,
            hovermode='x unified'
        )
        
        # 保存图表
        charts_dir = os.path.join(PATH_CONFIG["reports_dir"], "charts")
        Path(charts_dir).mkdir(parents=True, exist_ok=True)
        
        chart_path = os.path.join(charts_dir, "history_scores.html")
        fig.write_html(chart_path)
        logger.info(f"历史分数折线图已生成: {chart_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"生成历史分数折线图失败: {e}")
        if args.debug:
            logger.exception("详细错误信息:")
        return False

def generate_api_performance_chart():
    """生成API性能对比图"""
    logger = logging.getLogger(__name__)
    
    try:
        # 读取所有历史报告
        reports_dir = PATH_CONFIG["reports_dir"]
        report_files = [f for f in os.listdir(reports_dir) if f.startswith("evaluation_report_") and f.endswith(".md")]
        
        if not report_files:
            logger.error("没有找到历史报告")
            return False
        
        # 收集数据
        api_data = {}  # {method: {rank_method: {"scores": [], "times": []}}}
        
        for report_file in report_files:
            with open(os.path.join(reports_dir, report_file), 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 提取搜索方法信息
                method_match = re.search(r"\*\*搜索方法\*\*: (.*?)\n", content)
                if not method_match:
                    continue
                method = method_match.group(1)
                
                # 提取排序方法信息
                rank_method_match = re.search(r"\*\*排序方法\*\*: (.*?)\n", content)
                if not rank_method_match:
                    continue
                rank_method = rank_method_match.group(1)
                
                # 提取平均分数
                score_match = re.search(r"\*\*平均总分\*\*: ([\d.]+)", content)
                if not score_match:
                    continue
                score = float(score_match.group(1))
                
                # 提取平均时间
                time_match = re.search(r"\*\*平均每个案例耗时\*\*: ([\d.]+)秒", content)
                if not time_match:
                    continue
                time = float(time_match.group(1))
                
                # 存储数据
                if method not in api_data:
                    api_data[method] = {}
                if rank_method not in api_data[method]:
                    api_data[method][rank_method] = {"scores": [], "times": []}
                api_data[method][rank_method]["scores"].append(score)
                api_data[method][rank_method]["times"].append(time)
        
        if not api_data:
            logger.error("没有找到有效的API数据")
            return False
        
        # 计算每个方法组合的平均值
        api_metrics = {}
        for method, rank_methods in api_data.items():
            api_metrics[method] = {}
            for rank_method, data in rank_methods.items():
                api_metrics[method][rank_method] = {
                    "avg_score": sum(data["scores"]) / len(data["scores"]),
                    "avg_time": sum(data["times"]) / len(data["times"])
                }
        
        # 创建图表
        fig = go.Figure()
        
        # 获取所有唯一的排序方法
        rank_methods = set()
        for method_data in api_metrics.values():
            rank_methods.update(method_data.keys())
        rank_methods = sorted(list(rank_methods))
        
        # 为每个排序方法创建一组柱状图
        for rank_method in rank_methods:
            # 准备数据
            methods = []
            scores = []
            times = []
            
            for method in api_metrics.keys():
                if rank_method in api_metrics[method]:
                    methods.append(method)
                    scores.append(api_metrics[method][rank_method]["avg_score"])
                    times.append(api_metrics[method][rank_method]["avg_time"])
            
            # 添加分数折线图
            fig.add_trace(go.Scatter(
                x=methods,
                y=scores,
                name=f'{rank_method} - 分数',
                mode='lines+markers',
                line=dict(width=2),
                marker=dict(size=8)
            ))
            
            # 添加时间柱状图
            fig.add_trace(go.Bar(
                x=methods,
                y=times,
                name=f'{rank_method} - 耗时',
                opacity=0.7
            ))
        
        # 设置图表布局
        fig.update_layout(
            title="搜索方法性能对比",
            xaxis_title="搜索方法",
            yaxis_title="数值",
            showlegend=True,
            hovermode='x unified',
            barmode='group',  # 将柱状图分组显示
            # 添加双Y轴
            yaxis=dict(
                title="耗时(秒)",
                side="left",
                showgrid=True
            ),
            yaxis2=dict(
                title="分数",
                side="right",
                overlaying="y",
                range=[0, 1],
                showgrid=False
            )
        )
        
        # 更新折线图的Y轴
        for i in range(0, len(fig.data), 2):
            fig.data[i].yaxis = "y2"
        
        # 保存图表
        charts_dir = os.path.join(PATH_CONFIG["reports_dir"], "charts")
        Path(charts_dir).mkdir(parents=True, exist_ok=True)
        
        chart_path = os.path.join(charts_dir, "api_performance.html")
        fig.write_html(chart_path)
        logger.info(f"搜索方法性能对比图已生成: {chart_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"生成搜索方法性能对比图失败: {e}")
        if args.debug:
            logger.exception("详细错误信息:")
        return False

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
        
        # 保存历史分数
        if args.save_history:
            save_history_score(results, timestamp)
        
        # 生成报告（默认行为）
        generate_reports(results, timestamp)
        
        # 显示简要结果
        show_summary(results, args.debug)
        
        # 识别问题查询
        if args.show_problems:
            show_problematic_queries(evaluator)
        
        # 生成历史分数折线图
        if args.show_history:
            generate_history_chart()
            generate_api_performance_chart()
        
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
    config = results.get("config", {})
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 代码检索评估报告\n\n")
        
        # 基本信息
        f.write("## 评估概览\n\n")
        f.write(f"- **评估时间**: {meta['evaluation_time']}\n")
        f.write(f"- **测试案例总数**: {meta['total_test_cases']}\n")
        f.write(f"- **成功评估**: {meta['successful_evaluations']}\n")
        f.write(f"- **失败评估**: {meta['failed_evaluations']}\n")
        f.write(f"- **成功率**: {summary['evaluation_statistics']['success_rate']:.1%}\n")
        f.write(f"- **总耗时**: {meta['total_elapsed_time']:.2f}秒\n")
        f.write(f"- **平均每个案例耗时**: {meta['avg_elapsed_time']:.2f}秒\n\n")
        
        api_config = config.get("api", {})
        # API配置信息
        f.write("## API配置\n\n")
        f.write(f"- **基础URL**: {api_config.get('base_url', 'N/A')}\n")
        f.write(f"- **API端点**: {api_config.get('endpoint', 'N/A')}\n")
        f.write(f"- **项目ID**: {api_config.get('project_id', 'N/A')}\n")
        f.write(f"- **搜索方法**: {api_config.get('method', 'N/A')}\n")
        f.write(f"- **排序方法**: {api_config.get('rank_method', 'N/A')}\n\n")
        
        # 整体性能
        successful_results = [r for r in results["detailed_results"] if r.get("success", False)]
        if successful_results:
            f.write("## 整体性能指标\n\n")
            total_scores = [r.get("total_score", 0.0) for r in successful_results]
            relevance_scores = [r.get("relevance", 0.0) for r in successful_results]
            completeness_scores = [r.get("completeness", 0.0) for r in successful_results]
            usability_scores = [r.get("usability", 0.0) for r in successful_results]
            
            f.write(f"- **平均总分**: {np.mean(total_scores):.3f}\n")
            f.write(f"- **平均相关性**: {np.mean(relevance_scores):.3f}\n")
            f.write(f"- **平均全面性**: {np.mean(completeness_scores):.3f}\n")
            f.write(f"- **平均可用性**: {np.mean(usability_scores):.3f}\n\n")

        
        # 详细测试样例结果
        f.write("## 详细测试样例结果\n\n")
        for idx, result in enumerate(results["detailed_results"], 1):
            f.write(f"### 测试样例 {idx}\n\n")
            f.write(f"- **查询语句**: {result.get('query', 'N/A')}\n")
            f.write(f"- **类别**: {result.get('category', 'N/A')}\n")
            f.write(f"- **描述**: {result.get('description', 'N/A')}\n")
            f.write(f"- **评估状态**: {'成功' if result.get('success', False) else '失败'}\n")
            f.write(f"- **耗时**: {result.get('elapsed_time', 0):.2f}秒\n")
            
            if result.get('success', False):
                f.write(f"- **总分**: {result.get('total_score', 0.0):.3f}\n")
                f.write(f"- **相关性**: {result.get('relevance', 0.0):.3f}\n")
                f.write(f"- **全面性**: {result.get('completeness', 0.0):.3f}\n")
                f.write(f"- **可用性**: {result.get('usability', 0.0):.3f}\n")
                
                # 检索结果
                if "retrieved_results" in result:
                    f.write("\n#### 检索结果\n\n")
                    for rank, res in enumerate(result["retrieved_results"], 1):
                        f.write(f"##### 结果 {rank}\n\n")
                        f.write(f"- **文件路径**: {res.get('path', 'N/A')}\n")
                        f.write(f"- **相关性分数**: {res.get('score', 0.0):.3f}\n")
                        if "snippet" in res:
                            f.write("\n```\n")
                            f.write(res["snippet"])
                            f.write("\n```\n")
                        f.write("\n")
            
            # 错误信息
            if not result.get('success', False) and "error" in result:
                f.write(f"\n#### 错误信息\n\n")
                f.write(f"```\n{result['error']}\n```\n")
            
            f.write("\n---\n\n")

def generate_summary_report(results, output_path):
    """生成简要文本报告"""
    summary = results["summary_metrics"]
    meta = results["meta"]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("代码检索评估结果简要报告\n")
        f.write("=" * 40 + "\n\n")
        
        f.write(f"评估时间: {meta['evaluation_time']}\n")
        f.write(f"测试案例: {meta['total_test_cases']} (成功: {meta['successful_evaluations']})\n")
        f.write(f"成功率: {summary['evaluation_statistics']['success_rate']:.1%}\n")
        f.write(f"总耗时: {meta['total_elapsed_time']:.2f}秒\n")
        f.write(f"平均每个案例耗时: {meta['avg_elapsed_time']:.2f}秒\n\n")
        
        # 新评估框架表现
        if "new_framework_performance" in summary:
            new_framework = summary["new_framework_performance"]
            f.write("新评估框架表现:\n")
            f.write(f"  综合评分: {new_framework['avg_total_score']:.3f}\n")
            f.write(f"  相关性: {new_framework['avg_relevance']:.3f}\n")
            f.write(f"  全面性: {new_framework['avg_completeness']:.3f}\n")
            f.write(f"  可用性: {new_framework['avg_usability']:.3f}\n")

def show_summary(results, debug=False):
    """显示评估结果摘要"""
    print("\n" + "="*60)
    print("代码检索评估结果摘要")
    print("="*60)
    
    meta = results["meta"]
    summary = results["summary_metrics"]
    
    print(f"评估时间: {meta['evaluation_time']}")
    print(f"测试案例: {meta['total_test_cases']} (成功: {meta['successful_evaluations']})")
    print(f"成功率: {summary['evaluation_statistics']['success_rate']:.1%}")
    print(f"总耗时: {meta['total_elapsed_time']:.2f}秒")
    print(f"平均每个案例耗时: {meta['avg_elapsed_time']:.2f}秒")
    
    # 使用格式化工具添加详细解释
    formatted_summary = format_summary_with_explanations(summary)
    
    print("\n新评估框架整体表现:")
    if "new_framework_performance" in summary:
        new_framework = summary["new_framework_performance"]
        weights = new_framework.get("framework_weights", {})
        
        # 总分
        total_score = new_framework["avg_total_score"]
        total_interp = get_total_score_interpretation(total_score)
        print(f"  平均综合评分: {total_score:.3f} ({total_interp['level']})")
        print(f"     {total_interp.get('advice', '')}")
        
        # 三个维度
        dimensions = [
            ("avg_relevance", "平均相关性", weights.get("relevance", 0.3)),
            ("avg_completeness", "平均全面性", weights.get("completeness", 0.3)),
            ("avg_usability", "平均可用性", weights.get("usability", 0.4))
        ]
        
        for metric_key, metric_name, weight in dimensions:
            value = new_framework.get(metric_key, 0.0)
            interp = get_score_interpretation(value)
            print(f"  {metric_name}: {value:.3f} ({interp['level']}) - 权重: {weight*100:.0f}%")
    
    print("\n" + "=" * 50)

def get_total_score_interpretation(total_score):
    """获取总分解释"""
    if total_score >= 0.8:
        return {"level": "优秀", "advice": "综合表现优秀，检索系统可以投入使用"}
    elif total_score >= 0.6:
        return {"level": "良好", "advice": "综合表现良好，建议针对薄弱环节进一步优化"}
    elif total_score >= 0.4:
        return {"level": "一般", "advice": "综合表现一般，需要重点改进相关性和全面性"}
    elif total_score >= 0.2:
        return {"level": "较差", "advice": "综合表现较差，建议重新审视检索策略"}
    else:
        return {"level": "很差", "advice": "综合表现很差，需要重新设计检索系统"}

def get_score_interpretation(score):
    """获取分数解释"""
    if score >= 0.8:
        return {"level": "优秀", "description": "表现很好"}
    elif score >= 0.6:
        return {"level": "良好", "description": "表现不错，有改进空间"}
    elif score >= 0.4:
        return {"level": "一般", "description": "表现一般，需要优化"}
    elif score >= 0.2:
        return {"level": "较差", "description": "表现较差，急需改进"}
    else:
        return {"level": "很差", "description": "表现很差，需要重新设计"}

def show_problematic_queries(evaluator):
    """显示问题查询"""
    problematic = evaluator.get_problematic_queries(threshold=0.4)
    
    if not problematic:
        print("\n 没有发现问题查询 (总分 < 0.4)")
        return
    
    print(f"\n  发现 {len(problematic)} 个问题查询 (总分 < 0.4):")
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
        choices=list(CATEGORY_CONFIG.keys()),
        help="按类别过滤测试案例"
    )
    
    parser.add_argument(
        "--save-history",
        action="store_true",
        help="保存历史评估结果"
    )
    
    parser.add_argument(
        "--show-history",
        action="store_true",
        help="显示历史评估趋势图"
    )
    
    parser.add_argument(
        "--show-problems",
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
    if run_evaluation(args):
        # 生成历史分数折线图
        if args.show_history:
            generate_history_chart()
            generate_api_performance_chart()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()