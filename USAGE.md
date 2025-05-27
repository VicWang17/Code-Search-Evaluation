# 代码检索评估迷你系统

## 📋 系统概述

这是一个专门为fuint-uniapp项目设计的代码检索评估系统，用于测试自然语言查询与代码片段匹配的精确度。系统通过调用您的代码检索API来获取结果，然后与预期结果进行比较，计算各种评估指标。

## 🚀 快速开始

### 1. 环境准备

确保您的环境满足以下要求：
- Python 3.7+
- 代码检索服务运行在 `http://localhost:8000`
- 安装依赖包

```bash
pip install requests numpy
```

### 2. 快速测试

运行快速测试脚本确认系统正常工作：

```bash
cd code_search_evaluation
python quick_start.py
```

这个脚本会：
- 检查依赖项
- 测试API连接
- 运行单个查询测试
- 可选择运行迷你评估

### 3. 配置您的代码检索模型

在运行评估之前，您需要在 `config.py` 中配置您的代码检索模型参数：

```python
API_CONFIG = {
    # 修改为您的代码检索服务地址
    "base_url": "http://localhost:8000",      # 示例: 本地服务
    
    # 修改为您的API端点路径  
    "endpoint": "/api/search/code_by_hyde",   # 示例: HyDE搜索
    
    # 设置您要评估的项目ID
    "project_id": "5",                        # 示例: 项目5
    
    # 设置返回结果数量
    "limit": 10,                              # 建议10-20个结果
    
    "timeout": 30
}
```

**重要说明**:
- `localhost:8000` 和 `project_id: "5"` 是示例配置
- 请根据您的实际服务地址和项目ID进行修改  
- `project_id` 应该对应您要评估的具体代码库
- 评估系统会向您的模型发送20个测试查询

## 📊 运行完整评估

### 基本用法

```bash
# 运行完整评估
python run_evaluation.py

# 运行评估并生成详细报告
python run_evaluation.py --generate-report

# 运行评估并显示问题查询
python run_evaluation.py --show-problems

# 保存历史结果
python run_evaluation.py --save-history
```

### 高级用法

```bash
# 只测试前5个案例
python run_evaluation.py --limit 5

# 只测试样式相关查询
python run_evaluation.py --category style

# 使用自定义数据集
python run_evaluation.py --dataset my_test_data.json

# 启用调试模式
python run_evaluation.py --debug

# 组合使用
python run_evaluation.py --limit 10 --category function --generate-report --show-problems
```

## 📁 文件结构说明

```
code_search_evaluation/
├── README.md              # 项目说明
├── USAGE.md              # 使用说明（本文件）
├── config.py             # 配置文件
├── run_evaluation.py     # 主运行脚本
├── quick_start.py        # 快速测试脚本
├── evaluator.py          # 评估器核心逻辑
├── test_dataset.json     # 测试数据集
├── utils/                # 工具模块
│   ├── api_client.py     # API客户端
│   ├── metrics.py        # 评估指标计算
│   └── visualizer.py     # 结果可视化
├── results/              # 评估结果
│   ├── latest_result.json
│   └── history/
└── reports/              # 生成的报告
    ├── evaluation_report_*.md
    └── summary_*.txt
```

## 🔧 自定义配置

### API配置

修改 `config.py` 中的 `API_CONFIG`：

```python
API_CONFIG = {
    "base_url": "http://your-server:port",
    "endpoint": "/your/api/endpoint", 
    "project_id": "your_project_id",
    "limit": 10,
    "timeout": 30
}
```

### 评估参数

调整评估相关参数：

```python
EVALUATION_CONFIG = {
    "relevance_thresholds": {
        "PERFECT": 0.9,
        "HIGH": 0.7,
        "MEDIUM": 0.5,
        "LOW": 0.3,
        "IRRELEVANT": 0.0
    },
    "top_k_values": [1, 3, 5, 10],
    # ...
}
```

### 类别权重

设置不同查询类别的权重：

```python
CATEGORY_CONFIG = {
    "style": {"weight": 1.0},
    "function": {"weight": 1.2},  # 功能查询权重更高
    "layout": {"weight": 1.0},
    "api": {"weight": 1.1}
}
```

## 📝 自定义测试数据

### 数据格式

编辑 `test_dataset.json` 添加新的测试案例：

```json
{
  "idx": "custom-001",
  "query": "您的查询语句",
  "category": "style|function|layout|api",
  "description": "查询描述",
  "expected_results": [
    {
      "path": "期望的文件路径",
      "relevance_score": 1.0,
      "reason": "相关性说明",
      "expected_keywords": ["关键词1", "关键词2"]
    }
  ],
  "weight": 1.0
}
```

### 查询类别

系统支持四种查询类别：

1. **style**: CSS样式、UI设计相关
2. **function**: 业务逻辑、功能实现相关  
3. **layout**: 页面布局、组件排列相关
4. **api**: API调用、数据交互相关

### 相关性评分

- `1.0`: 完全匹配，这正是用户要找的
- `0.8-0.9`: 高度相关，很有帮助
- `0.5-0.7`: 中等相关，有一定帮助
- `0.3-0.4`: 低度相关，略有帮助
- `0.0-0.2`: 不相关

## 📈 评估指标说明

### 基础指标

- **精确率 (Precision)**: 检索到的相关结果 / 检索到的总结果
- **召回率 (Recall)**: 检索到的相关结果 / 实际相关的总结果  
- **F1分数**: 精确率和召回率的调和平均数

### 高级指标

- **MRR (Mean Reciprocal Rank)**: 第一个相关结果排名的倒数
- **NDCG**: 归一化折损累积增益，考虑结果排序质量
- **Top-K准确率**: 前K个结果中相关结果的比例

### 针对性指标

- **路径匹配率**: 预期文件路径的匹配程度
- **分数分布分析**: 检索结果分数的分布情况
- **多样性分数**: 结果的多样性评估

## 📊 结果分析

### 查看结果

1. **控制台输出**: 运行时会显示简要结果
2. **JSON结果**: `results/latest_result.json`
3. **详细报告**: `reports/evaluation_report_*.md`
4. **简要报告**: `reports/summary_*.txt`

### 理解分数

- **F1 > 0.7**: 优秀，检索效果很好
- **F1 = 0.5-0.7**: 良好，有改进空间
- **F1 = 0.3-0.5**: 一般，需要优化
- **F1 < 0.3**: 较差，需要重点改进

### 问题诊断

使用 `--show-problems` 查看表现较差的查询：

```bash
python run_evaluation.py --show-problems
```

常见问题类型：
- 精确率过低：返回太多不相关结果
- 召回率过低：遗漏相关结果
- 路径匹配失败：没有找到期望文件
- 检索分数过低：可能存在匹配问题

## 🔍 高级用法

### 批量测试

```bash
# 按类别分别测试
for category in style function layout api; do
    python run_evaluation.py --category $category --generate-report
done
```

### 性能测试

```bash
# 测试不同limit值的影响
for limit in 5 10 20; do
    echo "Testing with limit $limit"
    python run_evaluation.py --limit 3 --debug
done
```

### 历史对比

```bash
# 保存多个版本的结果进行对比
python run_evaluation.py --save-history
# 结果保存在 results/history/ 目录
```

## ❓ 常见问题

### Q: API连接失败怎么办？

A: 检查以下几点：
1. 代码检索服务是否启动
2. URL和端口是否正确
3. project_id是否存在
4. 网络连接是否正常

### Q: 评估结果都是0怎么办？

A: 可能的原因：
1. 期望结果路径格式不匹配（注意斜杠方向）
2. project_id对应的项目没有相关代码
3. 查询语句与实际代码内容差异较大

### Q: 如何提高评估准确性？

A: 建议：
1. 完善测试数据集，增加更多样的查询
2. 调整相关性阈值和权重
3. 检查期望结果是否realistic
4. 考虑添加同义词或近义词测试

### Q: 如何添加新的评估指标？

A: 修改 `utils/metrics.py`：
1. 在 `EvaluationMetrics` 类中添加新方法
2. 在 `evaluator.py` 中调用新指标
3. 在报告生成中展示新指标

## 🤝 贡献指南

欢迎提交改进建议：

1. **测试案例**: 添加更多有代表性的查询
2. **评估指标**: 提出新的评估维度
3. **可视化**: 改进结果展示方式
4. **性能优化**: 提升评估效率

## 📞 技术支持

如果遇到问题，请：

1. 首先运行 `python quick_start.py` 进行基础检查
2. 查看日志文件 `evaluation.log`  
3. 使用 `--debug` 模式获取详细信息
4. 检查配置文件设置是否正确

---

*祝您使用愉快！如果这个评估系统帮助您改进了代码检索效果，那就太棒了！* 🎉 