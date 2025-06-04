# -*- coding: utf-8 -*-
"""
代码检索评估系统配置文件
"""

# ============================================================================
# API配置 - 配置您的代码检索模型接口
# ============================================================================
API_CONFIG = {
    # 您的代码检索模型服务地址 (示例: localhost)
    # 请根据您的实际服务地址修改，例如:
    # - "http://your-model-server.com:8080"  
    # - "https://api.your-service.com"
    "base_url": "http://localhost:8000",
    
    # 您的API端点路径 (示例: HyDE搜索端点)
    # 请根据您的模型API修改，例如:
    # - "/api/v1/search"
    # - "/search/semantic"
    "endpoint": "/api/search/code_by_hybrid",
    
    # 您要评估的项目ID (示例: "5")
    # 这应该是您在检索系统中的项目标识符
    # 不同项目ID对应不同的代码库
    "project_id": "17",
    
    # 每次请求返回的结果数量
    # 建议设置为10-20，用于评估前K个结果的质量
    "limit": 10,
    
    # 请求超时时间（秒）
    "timeout": 30
}

# 评估配置
EVALUATION_CONFIG = {
    "default_k": 10,  # 默认评估前k个结果
    "top_k_values": [1, 3, 5, 10],  # 评估的K值列表
    "path_matching": {
        "exact_match": 1.0,
        "partial_match": 0.7,
        "extension_match": 0.3
    }
}

# 文件路径配置
PATH_CONFIG = {
    "test_dataset": "test_dataset.json",
    "results_dir": "results",
    "reports_dir": "reports",
    "history_dir": "results/history",
    "latest_result": "results/latest_result.json"
}

# 报告配置
REPORT_CONFIG = {
    "generate_html": True,      # 是否生成HTML报告
    "generate_charts": True,    # 是否生成图表
    "save_detailed_logs": True, # 是否保存详细日志
    "include_snippets": True,   # 是否在报告中包含代码片段
    
    # 图表配置
    "chart_config": {
        "figure_size": (12, 8),
        "dpi": 300,
        "style": "seaborn-v0_8",  # matplotlib样式
        "color_palette": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    }
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "evaluation.log",
    "console_output": True
}

# 类别配置
CATEGORY_CONFIG = {
    "frontend": {
        "name": "前端开发",
        "description": "前端相关的代码搜索"
    },
    "backend": {
        "name": "后端开发",
        "description": "后端相关的代码搜索"
    },
    "database": {
        "name": "数据库",
        "description": "数据库相关的代码搜索"
    }
}

# 性能配置
PERFORMANCE_CONFIG = {
    "batch_size": 5,           # 批量处理大小
    "retry_attempts": 3,       # 重试次数
    "retry_delay": 1,          # 重试间隔（秒）
    "concurrent_requests": 1,  # 并发请求数（建议为1避免服务器压力）
}

# 验证配置的函数
def validate_config():
    """验证配置的有效性"""
    errors = []
    
    # 验证API配置
    if not API_CONFIG.get("base_url"):
        errors.append("API_CONFIG.base_url 不能为空")
    
    if not API_CONFIG.get("project_id"):
        errors.append("API_CONFIG.project_id 不能为空")
    
    # 验证文件路径
    required_paths = ["test_dataset", "results_dir", "reports_dir"]
    for path_key in required_paths:
        if not PATH_CONFIG.get(path_key):
            errors.append(f"PATH_CONFIG.{path_key} 不能为空")
    
    # 验证评估参数
    if not EVALUATION_CONFIG.get("top_k_values"):
        errors.append("EVALUATION_CONFIG.top_k_values 不能为空")
    
    if errors:
        raise ValueError("配置验证失败:\n" + "\n".join(errors))
    
    return True

# 获取完整的API URL
def get_api_url():
    """获取完整的API URL"""
    return f"{API_CONFIG['base_url']}{API_CONFIG['endpoint']}"

# 获取API请求参数模板
def get_api_params_template():
    """获取API请求参数模板"""
    return {
        "limit": API_CONFIG["limit"],
        "project_id": API_CONFIG["project_id"]
    }

if __name__ == "__main__":
    # 测试配置
    try:
        validate_config()
        print("配置验证通过!")
        print(f"API URL: {get_api_url()}")
        print(f"项目ID: {API_CONFIG['project_id']}")
    except ValueError as e:
        print(f"配置错误: {e}") 