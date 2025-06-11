# -*- coding: utf-8 -*-
"""
代码检索评估指标计算模块
"""

import math
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
import logging

class EvaluationMetrics:
    """代码检索评估指标计算器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化评估指标
        
        Args:
            config: 评估配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.default_k = self.config.get("default_k", 10)
    
    def calculate_new_framework_metrics(self, actual_results: List[Dict], 
                                      expected_results: List[Dict],
                                      k: int = None) -> Dict[str, float]:
        """
        计算新评估框架的指标
        
        Args:
            actual_results: 实际检索结果
            expected_results: 期望结果
            k: 评估前k个结果，默认使用配置中的default_k
            
        Returns:
            Dict: 包含相关性、全面性、可用性和总分的字典
        """
        if k is None:
            k = self.default_k
            
        if not actual_results or not expected_results:
            return {
                "relevance": 0.0,
                "completeness": 0.0, 
                "usability": 0.0,
                "total_score": 0.0,
                "details": {
                    "relevant_in_top_k": 0,
                    "total_relevant": 0,
                    "k": k,
                    "mrr": 0.0
                }
            }
        
        # 获取期望结果的路径列表（保留重复）
        expected_paths = [self._normalize_path(r.get("path", "")) for r in expected_results]
        actual_paths = [self._normalize_path(r.get("path", "")) for r in actual_results]
        
        # 限制到前N个结果（N为期望结果数量）
        N = len(expected_results)
        top_k_paths = actual_paths[:min(k,len(actual_paths))]
        
        # 计算前k个结果中的相关数量（考虑重复）
        relevant_in_top_k = 0
        expected_paths_copy = expected_paths.copy()
        for path in top_k_paths:
            if path in expected_paths_copy:
                relevant_in_top_k += 1
                expected_paths_copy.remove(path)
        
        total_relevant = len(expected_results)
        
        # 1. 相关性 (基于位置的评分)
        # 首先检查是否所有expected paths都在前N位
        actual_top_n = actual_paths[:N]
        if all(path in actual_top_n for path in expected_paths):
            relevance = 1.0
        else:
            # 计算每个expected path的位置分数
            scores = []
            for exp_path in expected_paths:
                try:
                    pos = actual_paths.index(exp_path) + 1  # 1-based position
                    score = 1 / (1 + (math.log2(pos) ** 2))
                    scores.append(score)
                except ValueError:  # 如果路径没找到
                    scores.append(0)
            relevance = sum(scores) / len(expected_paths)

        # 2. 全面性 (召回率): 前k个结果中的相关数/总相关数
        completeness = relevant_in_top_k / total_relevant if total_relevant > 0 else 0.0
        
        # 3. 可用性 (MRR): 第一个相关结果排名的倒数
        usability = self.calculate_mrr(actual_results, expected_results)
        
        # 4. 总分: 相关性*0.3 + 全面性*0.3 + 可用性*0.4
        total_score = (
            relevance * 0.3 +
            completeness * 0.3 +
            usability * 0.4
        )
        
        return {
            "relevance": relevance,
            "completeness": completeness,
            "usability": usability, 
            "total_score": total_score,
            "details": {
                "relevant_in_top_k": relevant_in_top_k,
                "total_relevant": total_relevant,
                "k": k,
                "mrr": usability
            }
        }
    
    def calculate_path_matching_score(self, actual_results: List[Dict], 
                                    expected_results: List[Dict]) -> Dict[str, float]:
        """
        计算路径匹配评分
        
        Args:
            actual_results: 实际检索结果
            expected_results: 期望结果
            
        Returns:
            Dict: 路径匹配评分详情
        """
        if not actual_results or not expected_results:
            return {"total_score": 0.0, "exact_matches": 0, "partial_matches": 0, "extension_matches": 0}
        
        # 统计各种匹配类型
        exact_matches = 0
        partial_matches = 0
        extension_matches = 0
        
        actual_paths = [self._normalize_path(r.get("path", "")) for r in actual_results]
        expected_paths = [self._normalize_path(r.get("path", "")) for r in expected_results]
        
        for actual_path in actual_paths:
            for expected_path in expected_paths:
                if actual_path == expected_path:
                    exact_matches += 1
                    break
                elif self._is_partial_match(actual_path, expected_path):
                    partial_matches += 1
                    break
                elif self._is_extension_match(actual_path, expected_path):
                    extension_matches += 1
                    break
        
        # 计算总分
        total_score = (
            exact_matches * 1.0 +
            partial_matches * 0.7 +
            extension_matches * 0.3
        ) / len(expected_paths)
        
        return {
            "total_score": total_score,
            "exact_matches": exact_matches,
            "partial_matches": partial_matches,
            "extension_matches": extension_matches,
            "total_expected": len(expected_paths)
        }
    
    def calculate_top_k_accuracy(self, actual_results: List[Dict], 
                                expected_results: List[Dict],
                                k_values: List[int] = None) -> Dict[int, float]:
        """
        计算Top-K准确率
        
        Args:
            actual_results: 实际检索结果
            expected_results: 期望结果
            k_values: K值列表
            
        Returns:
            Dict[int, float]: 各K值对应的准确率
        """
        if k_values is None:
            k_values = [1, 3, 5, 10]
        
        if not actual_results or not expected_results:
            return {k: 0.0 for k in k_values}
        
        expected_paths = set(self._normalize_path(r.get("path", "")) for r in expected_results)
        actual_paths = [self._normalize_path(r.get("path", "")) for r in actual_results]
        
        top_k_accuracy = {}
        for k in k_values:
            top_k_paths = set(actual_paths[:min(k, len(actual_paths))])
            relevant_in_top_k = len(top_k_paths.intersection(expected_paths))
            accuracy = relevant_in_top_k / len(expected_paths) if expected_paths else 0.0
            top_k_accuracy[k] = accuracy
        
        return top_k_accuracy
    
    def calculate_score_analysis(self, actual_results: List[Dict]) -> Dict[str, float]:
        """
        分析检索结果的分数分布
        
        Args:
            actual_results: 实际检索结果
            
        Returns:
            Dict: 分数分析结果
        """
        if not actual_results:
            return {"max_score": 0.0, "min_score": 0.0, "avg_score": 0.0, "std_score": 0.0}
        
        scores = [r.get("score", 0.0) for r in actual_results if "score" in r]
        
        if not scores:
            return {"max_score": 0.0, "min_score": 0.0, "avg_score": 0.0, "std_score": 0.0}
        
        return {
            "max_score": max(scores),
            "min_score": min(scores),
            "avg_score": np.mean(scores),
            "std_score": np.std(scores),
            "score_gap": max(scores) - min(scores),
            "top_3_avg": np.mean(scores[:3]) if len(scores) >= 3 else np.mean(scores)
        }
    
    def calculate_mrr(self, actual_results: List[Dict], 
                     expected_results: List[Dict]) -> float:
        """
        计算平均倒数排名(Mean Reciprocal Rank)
        
        Args:
            actual_results: 实际检索结果
            expected_results: 期望结果
            
        Returns:
            float: MRR值
        """
        if not actual_results or not expected_results:
            return 0.0
        
        expected_paths = set(self._normalize_path(r.get("path", "")) for r in expected_results)
        actual_paths = [self._normalize_path(r.get("path", "")) for r in actual_results]
        
        # 找到第一个相关结果的位置
        for i, path in enumerate(actual_paths):
            if path in expected_paths:
                return 1.0 / (i + 1)
        
        return 0.0
    
    def calculate_ndcg(self, actual_results: List[Dict], 
                      expected_results: List[Dict], k: int = 10) -> float:
        """
        计算归一化折损累积增益(NDCG)
        
        Args:
            actual_results: 实际检索结果
            expected_results: 期望结果
            k: 计算前k个结果
            
        Returns:
            float: NDCG值
        """
        if not actual_results or not expected_results:
            return 0.0
        
        # 构建相关性字典
        relevance_dict = {}
        for exp_result in expected_results:
            path = self._normalize_path(exp_result.get("path", ""))
            relevance_dict[path] = exp_result.get("relevance_score", 1.0)
        
        # 计算DCG
        dcg = 0.0
        for i, result in enumerate(actual_results[:k]):
            path = self._normalize_path(result.get("path", ""))
            relevance = relevance_dict.get(path, 0.0)
            if i == 0:
                dcg += relevance
            else:
                dcg += relevance / math.log2(i + 1)
        
        # 计算IDCG (理想情况下的DCG)
        ideal_relevances = sorted(relevance_dict.values(), reverse=True)[:k]
        idcg = 0.0
        for i, relevance in enumerate(ideal_relevances):
            if i == 0:
                idcg += relevance
            else:
                idcg += relevance / math.log2(i + 1)
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def calculate_diversity_score(self, actual_results: List[Dict]) -> float:
        """
        计算结果多样性分数
        
        Args:
            actual_results: 实际检索结果
            
        Returns:
            float: 多样性分数
        """
        if not actual_results:
            return 0.0
        
        # 基于文件扩展名的多样性
        extensions = set()
        for result in actual_results:
            path = result.get("path", "")
            if "." in path:
                ext = path.split(".")[-1].lower()
                extensions.add(ext)
        
        # 基于目录的多样性
        directories = set()
        for result in actual_results:
            path = result.get("path", "")
            if "\\" in path or "/" in path:
                dir_path = "/".join(path.replace("\\", "/").split("/")[:-1])
                directories.add(dir_path)
        
        # 综合多样性分数
        ext_diversity = len(extensions) / len(actual_results) if actual_results else 0
        dir_diversity = len(directories) / len(actual_results) if actual_results else 0
        
        return (ext_diversity + dir_diversity) / 2
    
    def _normalize_path(self, path: str) -> str:
        """规范化文件路径"""
        # 统一路径分隔符和大小写
        path = path.replace("\\", "/").lower().strip()
        
        # 移除项目根目录前缀（如果存在）
        root_dirs = ["fuint-uniapp-master/", "src/", "app/"]
        for root_dir in root_dirs:
            if path.startswith(root_dir):
                path = path[len(root_dir):]
                break
                
        return path
    
    def _is_partial_match(self, path1: str, path2: str) -> bool:
        """判断是否为部分匹配"""
        parts1 = path1.split("/")
        parts2 = path2.split("/")
        
        # 如果文件名相同但路径不同
        if parts1[-1] == parts2[-1] and path1 != path2:
            return True
        
        # 如果路径有重叠部分
        common_parts = set(parts1).intersection(set(parts2))
        return len(common_parts) >= 2
    
    def _is_extension_match(self, path1: str, path2: str) -> bool:
        """判断是否为扩展名匹配"""
        if "." not in path1 or "." not in path2:
            return False
        
        ext1 = path1.split(".")[-1]
        ext2 = path2.split(".")[-1]
        
        return ext1 == ext2 and path1 != path2

class CategoryEvaluator:
    """分类别评估器"""
    
    def __init__(self):
        # 使用默认配置初始化EvaluationMetrics
        default_config = {
            "default_k": 10
        }
        self.metrics = EvaluationMetrics(default_config)
    
    def evaluate_by_category(self, results: List[Dict], 
                           category_config: Dict[str, Any]) -> Dict[str, Dict]:
        """
        按类别评估结果
        
        Args:
            results: 评估结果列表
            category_config: 类别配置
            
        Returns:
            Dict: 按类别的评估结果
        """
        category_results = defaultdict(list)
        
        # 按类别分组
        for result in results:
            category = result.get("category", "unknown")
            category_results[category].append(result)
        
        # 计算各类别指标
        category_metrics = {}
        for category, cat_results in category_results.items():
            if category in category_config:
                # 计算该类别的新框架指标
                total_scores = [r.get("total_score", 0.0) for r in cat_results]
                relevance_scores = [r.get("relevance", 0.0) for r in cat_results]
                completeness_scores = [r.get("completeness", 0.0) for r in cat_results]
                usability_scores = [r.get("usability", 0.0) for r in cat_results]
                
                category_metrics[category] = {
                    "name": category_config[category].get("name", category),
                    "count": len(cat_results),
                    # 新框架指标
                    "avg_total_score": np.mean(total_scores) if total_scores else 0.0,
                    "avg_relevance": np.mean(relevance_scores) if relevance_scores else 0.0,
                    "avg_completeness": np.mean(completeness_scores) if completeness_scores else 0.0,
                    "avg_usability": np.mean(usability_scores) if usability_scores else 0.0
                }
        
        return category_metrics

if __name__ == "__main__":
    # 测试代码
    default_config = {
        "default_k": 10
    }
    metrics = EvaluationMetrics(default_config)
    
    # 模拟数据
    actual = [
        {"path": "pages\\points\\exchange.vue", "score": 0.8},
        {"path": "pages\\coupon\\list.vue", "score": 0.6},
        {"path": "api\\goods.js", "score": 0.4}
    ]
    
    expected = [
        {"path": "pages\\points\\exchange.vue", "relevance_score": 1.0},
        {"path": "pages\\settlement\\style.scss", "relevance_score": 0.5}
    ]
    
    # 测试新框架指标
    framework_metrics = metrics.calculate_new_framework_metrics(actual, expected)
    print(f"新框架指标: {framework_metrics}")
    
    # 测试Top-K准确率
    top_k = metrics.calculate_top_k_accuracy(actual, expected, [1, 3, 5])
    print(f"Top-K准确率: {top_k}")
    
    # 测试分数分析
    score_analysis = metrics.calculate_score_analysis(actual)
    print(f"分数分析: {score_analysis}") 