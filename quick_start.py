# -*- coding: utf-8 -*-
"""
代码检索评估系统快速启动脚本
用于快速测试系统是否正常工作
"""

import os
import sys
import logging
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from config import API_CONFIG, validate_config
from utils.api_client import create_api_client

def test_api_connection():
    """测试API连接"""
    print("🔄 正在测试API连接...")
    
    try:
        # 验证配置
        validate_config()
        print("✅ 配置验证通过")
        
        # 创建API客户端
        client = create_api_client(API_CONFIG)
        
        # 测试连接
        if client.test_connection():
            print("✅ API连接成功")
            
            # 获取API信息
            api_info = client.get_api_info()
            print("\n📋 当前API配置信息:")
            for key, value in api_info.items():
                print(f"  {key}: {value}")
            
            print("\n💡 配置说明:")
            print(f"  - 服务地址: {API_CONFIG['base_url']} (示例配置)")
            print(f"  - 项目ID: {API_CONFIG['project_id']} (示例配置)")
            print(f"  - 如需修改，请编辑 config.py 文件")
            
            return True
        else:
            print("❌ API连接失败")
            print("\n🔧 请检查:")
            print(f"  1. 确认您的服务运行在: {API_CONFIG['base_url']}")
            print(f"  2. 确认项目ID '{API_CONFIG['project_id']}' 正确")
            print(f"  3. 如需修改配置，请编辑 config.py 文件")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("\n🔧 请检查:")
        print(f"  1. 确认您的模型服务正在运行")
        print(f"  2. 确认 config.py 中的配置正确")
        return False

def test_single_query():
    """测试单个查询"""
    print("\n🔄 正在测试单个查询...")
    
    try:
        # 创建API客户端
        client = create_api_client(API_CONFIG)
        
        # 测试查询
        test_query = "积分商品列表样式"
        print(f"🔍 测试查询: {test_query}")
        
        result = client.search_code(test_query)
        
        if "error" in result:
            print(f"❌ 查询失败: {result['error']}")
            return False
        
        results = result.get("results", [])
        print(f"✅ 查询成功，返回 {len(results)} 个结果")
        
        # 显示前3个结果
        if results:
            print("\n📋 前3个结果:")
            for i, res in enumerate(results[:3]):
                print(f"  {i+1}. {res.get('path', 'N/A')} (分数: {res.get('score', 0):.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ 查询测试失败: {e}")
        return False

def run_mini_evaluation():
    """运行迷你评估（只测试前3个案例）"""
    print("\n🔄 正在运行迷你评估...")
    
    try:
        from evaluator import CodeSearchEvaluator
        from config import EVALUATION_CONFIG, CATEGORY_CONFIG, PERFORMANCE_CONFIG
        
        # 构建配置
        config = {
            "api": API_CONFIG,
            "evaluation": EVALUATION_CONFIG,
            "categories": CATEGORY_CONFIG,
            "performance": PERFORMANCE_CONFIG
        }
        
        # 创建评估器
        evaluator = CodeSearchEvaluator(config)
        
        # 创建迷你测试数据集
        mini_dataset = {
            "meta": {
                "version": "1.0.0",
                "description": "迷你测试数据集",
                "total_cases": 3
            },
            "test_cases": [
                {
                    "idx": "mini-test-001",
                    "query": "积分商品列表样式",
                    "category": "style",
                    "description": "测试样式相关查询",
                    "expected_results": [
                        {"path": "pages\\points\\exchange.vue", "relevance_score": 1.0}
                    ],
                    "weight": 1.0
                },
                {
                    "idx": "mini-test-002", 
                    "query": "用户登录接口",
                    "category": "api",
                    "description": "测试API相关查询",
                    "expected_results": [
                        {"path": "api\\login\\login.js", "relevance_score": 1.0}
                    ],
                    "weight": 1.2
                },
                {
                    "idx": "mini-test-003",
                    "query": "商品卡片布局",
                    "category": "layout", 
                    "description": "测试布局相关查询",
                    "expected_results": [
                        {"path": "pages\\goods\\list.vue", "relevance_score": 1.0}
                    ],
                    "weight": 1.0
                }
            ]
        }
        
        # 执行评估
        print("📊 开始迷你评估...")
        results = evaluator.evaluate_dataset(mini_dataset)
        
        # 显示结果
        summary = results["summary_metrics"]
        print("✅ 迷你评估完成!")
        
        print("\n📈 新评估框架结果:")
        if "new_framework_performance" in summary:
            new_framework = summary["new_framework_performance"]
            print(f"  🏆 平均综合评分: {new_framework['avg_total_score']:.3f}")
            print(f"  📊 平均相关性: {new_framework['avg_relevance']:.3f} (权重50%)")
            print(f"  📈 平均全面性: {new_framework['avg_completeness']:.3f} (权重30%)")
            print(f"  🎯 平均可用性: {new_framework['avg_usability']:.3f} (权重20%)")
        
        print("\n📊 传统指标对比:")
        if "traditional_performance" in summary:
            traditional = summary["traditional_performance"]
            print(f"  📐 平均精确率: {traditional['avg_precision']:.3f}")
            print(f"  🎪 平均召回率: {traditional['avg_recall']:.3f}")
            print(f"  ⚖️ 平均F1分数: {traditional['avg_f1_score']:.3f}")
        
        # 保存迷你结果
        mini_result_path = "results/mini_evaluation_result.json"
        evaluator.save_results(results, mini_result_path)
        print(f"📁 结果已保存到: {mini_result_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 迷你评估失败: {e}")
        return False

def check_dependencies():
    """检查依赖项"""
    print("🔄 正在检查依赖项...")
    
    required_packages = [
        "requests",
        "numpy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (未安装)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  请安装缺失的依赖项:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖项已安装")
    return True

def main():
    """主函数"""
    print("🚀 代码检索评估系统快速测试")
    print("=" * 50)
    
    # 设置简单日志
    logging.basicConfig(level=logging.WARNING)
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖项检查失败，请先安装缺失的包")
        return False
    
    # 测试API连接
    if not test_api_connection():
        print("\n❌ API连接失败，请检查:")
        print("  1. 代码检索服务是否启动 (http://localhost:8000)")
        print("  2. project_id 是否正确配置")
        print("  3. 网络连接是否正常")
        return False
    
    # 测试单个查询
    if not test_single_query():
        print("\n❌ 单个查询测试失败")
        return False
    
    # 询问是否运行迷你评估
    print("\n🤔 是否运行迷你评估? (y/n): ", end="")
    try:
        choice = input().strip().lower()
        if choice in ['y', 'yes', '是']:
            if run_mini_evaluation():
                print("\n🎉 所有测试通过! 系统运行正常")
                print("\n📚 接下来您可以:")
                print("  1. 运行完整评估: python run_evaluation.py")
                print("  2. 查看测试数据集: test_dataset.json")
                print("  3. 修改配置: config.py")
                print("  4. 查看结果: results/mini_evaluation_result.json")
            else:
                print("\n❌ 迷你评估失败")
                return False
        else:
            print("\n✅ 基础测试通过! 您可以运行完整评估")
    except KeyboardInterrupt:
        print("\n\n👋 测试中断")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 再见!")
        sys.exit(0) 