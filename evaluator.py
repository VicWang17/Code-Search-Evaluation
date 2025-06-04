# -*- coding: utf-8 -*-
"""
代码检索评估器核心逻辑
"""

import json
import logging
import time
import os
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
    
    def evaluate_single_query(self, query: Dict) -> Dict:
        """
        评估单个查询
        
        Args:
            query: 查询信息，包含query和expected_results
            
        Returns:
            Dict: 评估结果
        """
        self.logger.info(f"开始评估查询: {query['query']}")
        
        try:
            # 调用API获取实际结果
            api_response = self.api_client.search_code(query["query"])
            
            # 检查API返回的错误
            if "error" in api_response:
                self.logger.error(f"API返回错误: {api_response['error']}")
                return {
                    "query": query["query"],
                    "error": api_response["error"],
                    "timestamp": datetime.now().isoformat(),
                    "success": False
                }
            
            # 获取实际结果列表
            actual_results = api_response.get("results", [])
            
            # 计算新框架指标
            metrics = self.metrics.calculate_new_framework_metrics(
                actual_results=actual_results,
                expected_results=query["expected_results"]
            )
            
            # 构建评估结果
            evaluation_result = {
                "query": query["query"],
                "category": query.get("category", "unknown"),
                "description": query.get("description", ""),
                "metrics": metrics,
                "expected_results": query["expected_results"],
                "actual_results": actual_results,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "total_score": metrics["total_score"],
                "relevance": metrics["relevance"],
                "completeness": metrics["completeness"],
                "usability": metrics["usability"]
            }
            
            self.logger.info(f"查询评估完成: {query['query']}")
            self.logger.info(f"总分: {metrics['total_score']:.3f} (相关性={metrics['relevance']:.3f}, 全面性={metrics['completeness']:.3f}, 可用性={metrics['usability']:.3f})")
            
            return evaluation_result
            
        except Exception as e:
            self.logger.error(f"评估查询时出错: {str(e)}")
            return {
                "query": query["query"],
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
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
                    "timestamp": datetime.now().isoformat()
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
        
        # 打印评估结果摘要
        self.logger.info("\n评估完成!")
        self.logger.info("\n新评估框架结果:")
        if "new_framework_performance" in self.summary_metrics:
            perf = self.summary_metrics["new_framework_performance"]
            self.logger.info(f"平均总分: {perf['avg_total_score']:.3f}")
            self.logger.info(f"平均相关性: {perf['avg_relevance']:.3f}")
            self.logger.info(f"平均全面性: {perf['avg_completeness']:.3f}")
            self.logger.info(f"平均可用性: {perf['avg_usability']:.3f}")
        
        self.logger.info("\n分类别评估结果:")
        for category, metrics in category_metrics.items():
            self.logger.info(f"\n{metrics['name']}:")
            self.logger.info(f"  测试案例数: {metrics['count']}")
            self.logger.info(f"  平均总分: {metrics['avg_total_score']:.3f}")
            self.logger.info(f"  平均相关性: {metrics['avg_relevance']:.3f}")
            self.logger.info(f"  平均全面性: {metrics['avg_completeness']:.3f}")
            self.logger.info(f"  平均可用性: {metrics['avg_usability']:.3f}")
        
        self.logger.info("\n所有测试通过! 系统运行正常")
        self.logger.info("\n接下来您可以:")
        self.logger.info("  1. 运行完整评估: python run_evaluation.py")
        self.logger.info("  2. 查看测试数据集: test_dataset.json")
        self.logger.info("  3. 修改配置: config.py")
        self.logger.info("  4. 查看结果: results/mini_evaluation_result.json")
        
        return full_report
    
    def _calculate_summary_metrics(self) -> Dict[str, Any]:
        """计算汇总指标"""
        successful_results = [r for r in self.evaluation_results if r.get("success", False)]
        
        if not successful_results:
            return {"error": "没有成功的评估结果"}
        
        # 计算新框架平均指标
        total_scores = [r.get("total_score", 0.0) for r in successful_results]
        relevance_scores = [r.get("relevance", 0.0) for r in successful_results]
        completeness_scores = [r.get("completeness", 0.0) for r in successful_results]
        usability_scores = [r.get("usability", 0.0) for r in successful_results]
        
        return {
            "new_framework_performance": {
                "avg_total_score": sum(total_scores) / len(total_scores) if total_scores else 0.0,
                "avg_relevance": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0,
                "avg_completeness": sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0,
                "avg_usability": sum(usability_scores) / len(usability_scores) if usability_scores else 0.0
            },
            "evaluation_statistics": {
                "total_queries": len(self.evaluation_results),
                "successful_queries": len(successful_results),
                "success_rate": len(successful_results) / len(self.evaluation_results) if self.evaluation_results else 0.0
            }
        }
    
    def save_results(self, results: Dict[str, Any], output_path: str) -> None:
        """
        保存评估结果到文件
        
        Args:
            results: 评估结果
            output_path: 输出文件路径
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 保存结果
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"评估结果已保存到: {output_path}")
            
        except Exception as e:
            self.logger.error(f"保存评估结果时出错: {str(e)}")
            raise
    