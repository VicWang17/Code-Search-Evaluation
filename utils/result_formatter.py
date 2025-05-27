# -*- coding: utf-8 -*-
"""
评估结果格式化工具
用于为评估结果添加详细的注释和说明
"""

def format_evaluation_result(result):
    """
    格式化单个评估结果，添加详细注释
    
    Args:
        result: 评估结果字典
        
    Returns:
        dict: 包含注释的格式化结果
    """
    if not result.get("success", False):
        return result
    
    # 添加指标解释
    formatted_result = result.copy()
    
    # 新评估框架指标注释
    formatted_result["framework_explanation"] = {
        "total_score": {
            "value": result.get("total_score", 0.0),
            "description": "综合评分 - 相关性×0.5 + 全面性×0.3 + 可用性×0.2",
            "formula": "相关性×0.5 + 全面性×0.3 + 可用性×0.2",
            "range": "0.0-1.0 (越高越好)",
            "interpretation": get_total_score_interpretation(result.get("total_score", 0.0))
        },
        "relevance": {
            "value": result.get("relevance", 0.0),
            "description": "相关性 (50%) - 前k个结果中相关数/k",
            "formula": "前k个结果中相关数 / k",
            "range": "0.0-1.0 (越高越好)",
            "interpretation": get_score_interpretation(result.get("relevance", 0.0))
        },
        "completeness": {
            "value": result.get("completeness", 0.0),
            "description": "全面性 (30%) - 前k个结果中的相关数/总相关数",
            "formula": "前k个结果中的相关数 / 总相关数",
            "range": "0.0-1.0 (越高越好)",
            "interpretation": get_score_interpretation(result.get("completeness", 0.0))
        },
        "usability": {
            "value": result.get("usability", 0.0),
            "description": "可用性 (20%) - 平均倒数排名 (MRR)",
            "formula": "第一个相关结果排名的倒数",
            "range": "0.0-1.0 (越高越好)",
            "interpretation": get_mrr_interpretation(result.get("usability", 0.0))
        }
    }
    
    # 传统指标注释 (保留用于对比)
    formatted_result["traditional_metrics_explanation"] = {
        "precision": {
            "value": result.get("precision", 0.0),
            "description": "传统精确率 - 检索到的结果中相关结果的比例",
            "formula": "相关且检索到的结果数 / 总检索到的结果数",
            "range": "0.0-1.0 (越高越好)",
            "interpretation": get_score_interpretation(result.get("precision", 0.0))
        },
        "recall": {
            "value": result.get("recall", 0.0),
            "description": "传统召回率 - 所有相关结果中被检索到的比例",
            "formula": "相关且检索到的结果数 / 总相关结果数",
            "range": "0.0-1.0 (越高越好)",
            "interpretation": get_score_interpretation(result.get("recall", 0.0))
        },
        "f1_score": {
            "value": result.get("f1_score", 0.0),
            "description": "传统F1分数 - 精确率和召回率的调和平均数",
            "formula": "2 × (精确率 × 召回率) / (精确率 + 召回率)",
            "range": "0.0-1.0 (越高越好)",
            "interpretation": get_f1_interpretation(result.get("f1_score", 0.0))
        }
    }
    
    # 路径匹配注释
    if "path_matching" in result:
        path_matching = result["path_matching"]
        formatted_result["path_matching_explanation"] = {
            "total_score": {
                "value": path_matching.get("total_score", 0.0),
                "description": "路径匹配总分 - 综合考虑精确、部分和扩展名匹配",
                "formula": "(精确匹配×1.0 + 部分匹配×0.7 + 扩展名匹配×0.3) / 期望结果数",
                "interpretation": get_score_interpretation(path_matching.get("total_score", 0.0))
            },
            "match_details": {
                "exact_matches": {
                    "count": path_matching.get("exact_matches", 0),
                    "description": "文件路径完全相同的匹配数",
                    "weight": "1.0 (最高权重)"
                },
                "partial_matches": {
                    "count": path_matching.get("partial_matches", 0),
                    "description": "文件名相同或路径有重叠的匹配数",
                    "weight": "0.7"
                },
                "extension_matches": {
                    "count": path_matching.get("extension_matches", 0),
                    "description": "文件扩展名相同的匹配数",
                    "weight": "0.3"
                }
            }
        }
    
    # Top-K准确率注释
    if "top_k_accuracy" in result:
        top_k = result["top_k_accuracy"]
        formatted_result["top_k_explanation"] = {}
        for k, accuracy in top_k.items():
            formatted_result["top_k_explanation"][f"top_{k}"] = {
                "value": accuracy,
                "description": f"前{k}个结果中相关结果的比例",
                "interpretation": get_score_interpretation(accuracy)
            }
    
    # 分数分析注释
    if "score_analysis" in result:
        score_analysis = result["score_analysis"]
        formatted_result["score_analysis_explanation"] = {
            "avg_score": {
                "value": score_analysis.get("avg_score", 0.0),
                "description": "检索结果的平均分数",
                "interpretation": get_retrieval_score_interpretation(score_analysis.get("avg_score", 0.0))
            },
            "max_score": {
                "value": score_analysis.get("max_score", 0.0),
                "description": "检索结果的最高分数",
                "interpretation": "反映最相关结果的匹配程度"
            },
            "score_gap": {
                "value": score_analysis.get("score_gap", 0.0),
                "description": "最高分和最低分的差距",
                "interpretation": "差距大说明结果质量差异明显"
            }
        }
    
    # 高级指标注释
    if "mrr" in result:
        formatted_result["advanced_metrics_explanation"] = {
            "mrr": {
                "value": result.get("mrr", 0.0),
                "description": "平均倒数排名 - 第一个相关结果排名的倒数",
                "interpretation": get_mrr_interpretation(result.get("mrr", 0.0))
            },
            "ndcg": {
                "value": result.get("ndcg", 0.0),
                "description": "归一化折损累积增益 - 考虑结果排序质量的指标",
                "interpretation": get_score_interpretation(result.get("ndcg", 0.0))
            },
            "diversity": {
                "value": result.get("diversity", 0.0),
                "description": "结果多样性分数 - 基于文件类型和目录的多样性",
                "interpretation": get_diversity_interpretation(result.get("diversity", 0.0))
            }
        }
    
    return formatted_result

def get_score_interpretation(score):
    """获取分数解释"""
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

def get_total_score_interpretation(total_score):
    """获取总分的特殊解释"""
    interpretation = get_score_interpretation(total_score)
    
    if total_score >= 0.8:
        interpretation["advice"] = "综合表现优秀，检索系统可以投入使用"
        interpretation["level_detail"] = "在相关性、全面性和可用性方面都表现出色"
    elif total_score >= 0.6:
        interpretation["advice"] = "综合表现良好，建议针对薄弱环节进一步优化"
        interpretation["level_detail"] = "整体表现不错，但仍有改进空间"
    elif total_score >= 0.4:
        interpretation["advice"] = "综合表现一般，需要重点改进相关性和全面性"
        interpretation["level_detail"] = "需要在多个维度上进行优化"
    elif total_score >= 0.2:
        interpretation["advice"] = "综合表现较差，建议重新审视检索策略"
        interpretation["level_detail"] = "在相关性、全面性或可用性方面存在明显问题"
    else:
        interpretation["advice"] = "综合表现很差，需要重新设计检索系统"
        interpretation["level_detail"] = "各项指标都需要大幅改进"
    
    return interpretation

def get_f1_interpretation(f1_score):
    """获取F1分数的特殊解释"""
    interpretation = get_score_interpretation(f1_score)
    
    if f1_score >= 0.7:
        interpretation["advice"] = "传统F1指标优秀，可以投入使用"
    elif f1_score >= 0.5:
        interpretation["advice"] = "传统F1指标可以接受，建议进一步优化"
    elif f1_score >= 0.3:
        interpretation["advice"] = "传统F1指标需要改进，检查算法和数据"
    else:
        interpretation["advice"] = "传统F1指标很差，需要重新设计检索策略"
    
    return interpretation

def get_mrr_interpretation(mrr):
    """获取MRR的解释"""
    if mrr >= 0.8:
        return {"level": "优秀", "color": "🟢", "description": "第一个结果通常就是相关的"}
    elif mrr >= 0.5:
        return {"level": "良好", "color": "🟡", "description": "相关结果通常在前几位"}
    elif mrr >= 0.3:
        return {"level": "一般", "color": "🟠", "description": "相关结果排名较靠后"}
    else:
        return {"level": "较差", "color": "🔴", "description": "很难找到相关结果或排名很靠后"}

def get_diversity_interpretation(diversity):
    """获取多样性的解释"""
    if diversity >= 0.7:
        return {"level": "高", "description": "结果涵盖多种文件类型和目录"}
    elif diversity >= 0.4:
        return {"level": "中等", "description": "结果有一定多样性"}
    else:
        return {"level": "低", "description": "结果比较单一，可能过于集中"}

def get_retrieval_score_interpretation(avg_score):
    """获取检索分数的解释"""
    if avg_score >= 0.7:
        return {"level": "高", "description": "检索算法匹配度很高"}
    elif avg_score >= 0.5:
        return {"level": "中等", "description": "检索算法匹配度一般"}
    else:
        return {"level": "低", "description": "检索算法匹配度较低，可能需要调整"}

def print_formatted_result(result, show_details=True):
    """
    打印格式化的评估结果
    
    Args:
        result: 评估结果
        show_details: 是否显示详细信息
    """
    if not result.get("success", False):
        print(f"❌ 查询失败: {result.get('query', 'Unknown')} - {result.get('error', 'Unknown error')}")
        return
    
    print(f"\n📊 查询: {result.get('query', 'Unknown')}")
    print(f"🏷️  类别: {result.get('category', 'Unknown')}")
    
    # 显示新评估框架指标
    if "framework_explanation" in result:
        framework = result["framework_explanation"]
        
        print("\n🎯 新评估框架指标:")
        
        # 总分
        total_info = framework["total_score"]
        total_interp = total_info["interpretation"]
        print(f"  {total_interp['color']} 综合评分: {total_info['value']:.3f} ({total_interp['level']})")
        if show_details:
            print(f"     └─ {total_info['description']}")
            print(f"     💡 {total_interp.get('advice', '')}")
        
        # 三个维度
        dimensions = ["relevance", "completeness", "usability"]
        dimension_names = {"relevance": "相关性", "completeness": "全面性", "usability": "可用性"}
        
        for dim in dimensions:
            if dim in framework:
                dim_info = framework[dim]
                dim_interp = dim_info["interpretation"]
                print(f"  {dim_interp['color']} {dimension_names[dim]}: {dim_info['value']:.3f} ({dim_interp['level']})")
                if show_details:
                    print(f"     └─ {dim_info['description']}")
    
    # 显示传统指标 (折叠显示)
    if show_details and "traditional_metrics_explanation" in result:
        traditional = result["traditional_metrics_explanation"]
        
        print("\n📈 传统指标 (对比参考):")
        for metric_name, metric_info in traditional.items():
            value = metric_info["value"]
            interp = metric_info["interpretation"]
            print(f"  {interp['color']} {metric_name.replace('_', ' ').title()}: {value:.3f} ({interp['level']})")
            print(f"     └─ {metric_info['description']}")
    
    if show_details and "path_matching_explanation" in result:
        path_exp = result["path_matching_explanation"]
        print(f"\n🔍 路径匹配分析:")
        print(f"  📈 总分: {path_exp['total_score']['value']:.3f}")
        
        match_details = path_exp["match_details"]
        print(f"  ✅ 精确匹配: {match_details['exact_matches']['count']} 个")
        print(f"  🎯 部分匹配: {match_details['partial_matches']['count']} 个")
        print(f"  📄 扩展名匹配: {match_details['extension_matches']['count']} 个")
    
    if show_details and "advanced_metrics_explanation" in result:
        adv_metrics = result["advanced_metrics_explanation"]
        print(f"\n📈 高级指标:")
        for metric_name, metric_info in adv_metrics.items():
            print(f"  • {metric_name.upper()}: {metric_info['value']:.3f} - {metric_info['description']}")

def format_summary_with_explanations(summary_metrics):
    """为汇总指标添加解释"""
    formatted_summary = summary_metrics.copy()
    
    if "overall_performance" in summary_metrics:
        overall = summary_metrics["overall_performance"]
        formatted_summary["overall_performance_explanation"] = {
            "description": "所有测试案例的平均表现",
            "metrics": {
                "avg_f1_score": {
                    "value": overall.get("avg_f1_score", 0.0),
                    "interpretation": get_f1_interpretation(overall.get("avg_f1_score", 0.0)),
                    "importance": "最重要的综合指标"
                },
                "avg_precision": {
                    "value": overall.get("avg_precision", 0.0),
                    "interpretation": get_score_interpretation(overall.get("avg_precision", 0.0)),
                    "importance": "衡量结果准确性"
                },
                "avg_recall": {
                    "value": overall.get("avg_recall", 0.0),
                    "interpretation": get_score_interpretation(overall.get("avg_recall", 0.0)),
                    "importance": "衡量结果完整性"
                }
            }
        }
    
    return formatted_summary 