# -*- coding: utf-8 -*-
"""
代码检索评估器核心逻辑
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from utils.api_client import create_api_client
from utils.metrics import EvaluationMetrics, CategoryEvaluator

class CodeSearchEvaluator:
    """代码检索评估器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化评估器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.api_client = create_api_client(config["api"])
        self.metrics = EvaluationMetrics(config.get("evaluation", {}))
        self.category_evaluator = CategoryEvaluator()
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 评估结果存储
        self.evaluation_results = []
        self.summary_metrics = {}
        
    def load_test_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """
        加载测试数据集
        
        Args:
            dataset_path: 数据集文件路径
            
        Returns:
            Dict: 测试数据集
        """
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            self.logger.info(f"成功加载测试数据集: {len(dataset.get('test_cases', []))} 个测试案例")
            return dataset
            
        except FileNotFoundError:
            self.logger.error(f"找不到测试数据集文件: {dataset_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"测试数据集JSON格式错误: {e}")
            raise
    
    def evaluate_single_query(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估单个查询
        
        Args:
            test_case: 测试案例
            
        Returns:
            Dict: 评估结果
        """
        query = test_case["query"]
        expected_results = test_case["expected_results"]
        category = test_case.get("category", "unknown")
        weight = test_case.get("weight", 1.0)
        
        self.logger.info(f"正在评估查询: {query}")
        
        # 调用API进行代码检索
        api_response = self.api_client.search_code_with_retry(query)
        
        if "error" in api_response:
            self.logger.error(f"API调用失败: {api_response['error']}")
            return {
                "idx": test_case["idx"],
                "query": query,
                "category": category,
                "error": api_response["error"],
                "success": False
            }
        
        actual_results = api_response.get("results", [])
        
        # 计算新评估框架指标
        framework_metrics = self.metrics.calculate_new_framework_metrics(
            actual_results, expected_results,
            self.config["evaluation"].get("default_k", 10)
        )
        
        # 计算传统指标 (保留用于对比分析)
        precision, recall, f1 = self.metrics.calculate_precision_recall_f1(
            actual_results, expected_results
        )
        
        path_matching = self.metrics.calculate_path_matching_score(
            actual_results, expected_results,
            self.config["evaluation"]["path_matching"]
        )
        
        top_k_accuracy = self.metrics.calculate_top_k_accuracy(
            actual_results, expected_results,
            self.config["evaluation"]["top_k_values"]
        )
        
        score_analysis = self.metrics.calculate_score_analysis(actual_results)
        
        diversity = self.metrics.calculate_diversity_score(actual_results)
        
        # 构建评估结果
        evaluation_result = {
            "idx": test_case["idx"],
            "query": query,
            "category": category,
            "weight": weight,
            "description": test_case.get("description", ""),
            
            # 新评估框架指标 (主要指标)
            "framework_metrics": framework_metrics,
            "relevance": framework_metrics["relevance"],
            "completeness": framework_metrics["completeness"],
            "usability": framework_metrics["usability"],
            "total_score": framework_metrics["total_score"],
            
            # 传统指标 (保留用于对比)
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            
            # 详细分析
            "path_matching": path_matching,
            "top_k_accuracy": top_k_accuracy,
            "score_analysis": score_analysis,
            "diversity": diversity,
            
            # 原始数据
            "expected_results": expected_results,
            "actual_results": actual_results[:5],  # 只保存前5个结果
            "total_results": len(actual_results),
            
            # 元数据
            "timestamp": time.time(),
            "success": True
        }
        
        self.logger.info(f"查询评估完成: 总分={framework_metrics['total_score']:.3f} (相关性={framework_metrics['relevance']:.3f}, 全面性={framework_metrics['completeness']:.3f}, 可用性={framework_metrics['usability']:.3f})")
        
        return evaluation_result
    
    def evaluate_dataset(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估整个数据集
        
        Args:
            dataset: 测试数据集
            
        Returns:
            Dict: 完整评估结果
        """
        test_cases = dataset.get("test_cases", [])
        
        if not test_cases:
            raise ValueError("测试数据集为空")
        
        self.logger.info(f"开始评估数据集，共 {len(test_cases)} 个测试案例")
        
        # 重置评估结果
        self.evaluation_results = []
        
        # 批量评估
        for i, test_case in enumerate(test_cases):
            self.logger.info(f"进度: {i+1}/{len(test_cases)}")
            
            try:
                result = self.evaluate_single_query(test_case)
                self.evaluation_results.append(result)
                
                # 控制请求频率
                if i < len(test_cases) - 1:
                    time.sleep(self.config["performance"]["retry_delay"])
                    
            except Exception as e:
                self.logger.error(f"评估测试案例失败 {test_case['idx']}: {e}")
                # 记录失败的案例
                self.evaluation_results.append({
                    "idx": test_case["idx"],
                    "query": test_case["query"],
                    "category": test_case.get("category", "unknown"),
                    "error": str(e),
                    "success": False,
                    "timestamp": time.time()
                })
        
        # 计算汇总指标
        self.summary_metrics = self._calculate_summary_metrics()
        
        # 计算分类别指标
        category_metrics = self.category_evaluator.evaluate_by_category(
            self.evaluation_results,
            self.config["categories"]
        )
        
        # 生成完整报告
        full_report = {
            "meta": {
                "dataset_info": dataset.get("meta", {}),
                "evaluation_time": datetime.now().isoformat(),
                "total_test_cases": len(test_cases),
                "successful_evaluations": len([r for r in self.evaluation_results if r.get("success", False)]),
                "failed_evaluations": len([r for r in self.evaluation_results if not r.get("success", False)])
            },
            "summary_metrics": self.summary_metrics,
            "category_metrics": category_metrics,
            "detailed_results": self.evaluation_results,
            "config": self.config
        }
        
        self.logger.info("数据集评估完成")
        return full_report
    
    def _calculate_summary_metrics(self) -> Dict[str, Any]:
        """计算汇总指标"""
        successful_results = [r for r in self.evaluation_results if r.get("success", False)]
        
        if not successful_results:
            return {"error": "没有成功的评估结果"}
        
        # 计算新框架平均指标
        total_scores = [r["total_score"] for r in successful_results]
        relevance_scores = [r["relevance"] for r in successful_results]
        completeness_scores = [r["completeness"] for r in successful_results]
        usability_scores = [r["usability"] for r in successful_results]
        
        # 计算传统指标 (保留用于对比)
        precisions = [r["precision"] for r in successful_results]
        recalls = [r["recall"] for r in successful_results]
        f1_scores = [r["f1_score"] for r in successful_results]
        
        # Top-K准确率汇总
        top_k_summary = {}
        k_values = self.config["evaluation"]["top_k_values"]
        for k in k_values:
            k_accuracies = [r["top_k_accuracy"].get(k, 0.0) for r in successful_results]
            top_k_summary[f"top_{k}_accuracy"] = sum(k_accuracies) / len(k_accuracies)
        
        # 路径匹配汇总
        path_match_scores = [r["path_matching"]["total_score"] for r in successful_results]
        exact_matches = sum(r["path_matching"]["exact_matches"] for r in successful_results)
        partial_matches = sum(r["path_matching"]["partial_matches"] for r in successful_results)
        
        # 分数分析汇总
        avg_scores = [r["score_analysis"]["avg_score"] for r in successful_results]
        max_scores = [r["score_analysis"]["max_score"] for r in successful_results]
        
        return {
            "new_framework_performance": {
                "avg_total_score": sum(total_scores) / len(total_scores),
                "avg_relevance": sum(relevance_scores) / len(relevance_scores),
                "avg_completeness": sum(completeness_scores) / len(completeness_scores),
                "avg_usability": sum(usability_scores) / len(usability_scores),
                "framework_weights": successful_results[0]["framework_metrics"]["details"]["weights"] if successful_results else {}
            },
            "traditional_performance": {
                "avg_precision": sum(precisions) / len(precisions),
                "avg_recall": sum(recalls) / len(recalls),
                "avg_f1_score": sum(f1_scores) / len(f1_scores)
            },
            "top_k_performance": top_k_summary,
            "path_matching_performance": {
                "avg_path_match_score": sum(path_match_scores) / len(path_match_scores),
                "total_exact_matches": exact_matches,
                "total_partial_matches": partial_matches,
                "exact_match_rate": exact_matches / len(successful_results)
            },
            "score_distribution": {
                "avg_result_score": sum(avg_scores) / len(avg_scores),
                "avg_max_score": sum(max_scores) / len(max_scores),
                "score_consistency": 1.0 - (max(avg_scores) - min(avg_scores)) if avg_scores else 0.0
            },
            "evaluation_statistics": {
                "total_queries": len(self.evaluation_results),
                "successful_queries": len(successful_results),
                "success_rate": len(successful_results) / len(self.evaluation_results),
                "avg_results_per_query": sum(r["total_results"] for r in successful_results) / len(successful_results)
            }
        }
    
    def get_problematic_queries(self, threshold: float = 0.4) -> List[Dict[str, Any]]:
        """
        识别表现较差的查询 (基于新评估框架)
        
        Args:
            threshold: 总分阈值
            
        Returns:
            List: 问题查询列表
        """
        problematic = []
        
        for result in self.evaluation_results:
            if result.get("success", False) and result.get("total_score", 0.0) < threshold:
                problematic.append({
                    "idx": result["idx"],
                    "query": result["query"],
                    "category": result["category"],
                    "total_score": result["total_score"],
                    "relevance": result["relevance"],
                    "completeness": result["completeness"],
                    "usability": result["usability"],
                    "issues": self._analyze_query_issues(result)
                })
        
        return sorted(problematic, key=lambda x: x["total_score"])
    
    def _analyze_query_issues(self, result: Dict[str, Any]) -> List[str]:
        """分析查询的具体问题 (基于新评估框架)"""
        issues = []
        
        # 基于新框架的问题分析
        if result.get("relevance", 0.0) < 0.3:
            issues.append("相关性过低 - 前k个结果中相关结果太少")
        
        if result.get("completeness", 0.0) < 0.3:
            issues.append("全面性不足 - 遗漏了太多相关结果")
        
        if result.get("usability", 0.0) < 0.3:
            issues.append("可用性较差 - 相关结果排名太靠后")
        
        # 详细问题分析
        if result.get("framework_metrics", {}).get("details", {}).get("relevant_in_top_k", 0) == 0:
            issues.append("前k个结果中没有相关结果")
        
        if result.get("path_matching", {}).get("exact_matches", 0) == 0:
            issues.append("路径匹配失败 - 没有找到期望的文件")
        
        if result.get("top_k_accuracy", {}).get(1, 0.0) == 0.0:
            issues.append("Top-1准确率为0 - 第一个结果不相关")
        
        if result.get("score_analysis", {}).get("max_score", 0.0) < 0.5:
            issues.append("检索分数过低 - 可能存在匹配问题")
        
        return issues
    
    def save_results(self, results: Dict[str, Any], output_path: str) -> None:
        """
        保存评估结果
        
        Args:
            results: 评估结果
            output_path: 输出文件路径
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"评估结果已保存到: {output_path}")
            
        except Exception as e:
            self.logger.error(f"保存评估结果失败: {e}")
            raise

if __name__ == "__main__":
    # 测试代码
    import os
    import sys
    
    # 添加当前目录到Python路径
    sys.path.append(os.path.dirname(__file__))
    
    from config import API_CONFIG, EVALUATION_CONFIG, CATEGORY_CONFIG, PERFORMANCE_CONFIG
    
    # 构建配置
    test_config = {
        "api": API_CONFIG,
        "evaluation": EVALUATION_CONFIG,
        "categories": CATEGORY_CONFIG,
        "performance": PERFORMANCE_CONFIG
    }
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建评估器
    evaluator = CodeSearchEvaluator(test_config)
    
    # 测试API连接
    if evaluator.api_client.test_connection():
        print("评估器初始化成功，API连接正常")
    else:
        print("API连接失败，请检查服务状态") 