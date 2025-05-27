# 代码检索迷你评估系统

## 📖 项目简介
这是一个用于评估代码检索系统性能的工具。它可以帮助你测试自然语言查询与代码片段匹配的准确性和相关性。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install requests numpy matplotlib pandas
```

### 2. 配置系统
编辑 `config.py` 文件，设置以下参数：
```python
API_CONFIG = {
    "base_url": "http://localhost:8000",    # 你的模型服务地址
    "endpoint": "/api/search/code_by_hyde", # API端点
    "project_id": "5",                      # 项目ID
    "limit": 10                             # 返回结果数量
}
```

### 3. 运行评估
```bash
python run_evaluation.py
```

## 📊 评估指标

系统会评估以下指标：
- 精确率 (Precision)
- 召回率 (Recall)
- F1-Score
- 路径匹配率
- Top-K准确率

## 📝 测试数据集

测试数据集包含三类查询：
1. 样式相关查询（如：按钮样式、列表样式等）
2. 功能相关查询（如：登录逻辑、支付流程等）
3. 布局相关查询（如：页面布局、响应式设计等）

## 📁 项目结构
```
code_search_evaluation/
├── run_evaluation.py    # 主评估脚本
├── config.py           # 配置文件
├── evaluator.py        # 评估器核心逻辑
├── test_dataset.json   # 测试数据集
├── utils/             # 工具函数
├── results/           # 评估结果
└── reports/           # 评估报告
```

## 🔍 查看结果
评估完成后，可以在 `reports/` 目录下查看：
- `summary_report.html`：汇总报告
- `detailed_analysis.md`：详细分析

## 🐛 常见问题

1. API连接失败
   - 检查服务是否启动
   - 确认端口是否正确

2. 结果为空
   - 检查 project_id 是否正确
   - 确认测试数据集格式

3. 启用调试模式
```bash
python run_evaluation.py --debug
```

## 📜 许可证
MIT License 