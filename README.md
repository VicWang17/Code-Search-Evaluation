# 代码检索评估测试系统

## 项目简介

基于fuint-uniapp项目的代码检索自动化评估系统，用于测试自然语言查询与代码片段匹配的精确度和相关性。

## 系统架构

```
code_search_evaluation/
├── README.md                 # 项目说明文档
├── run_evaluation.py         # 主评估脚本
├── config.py                 # 配置文件
├── evaluator.py              # 评估器核心逻辑
├── test_dataset.json         # 测试数据集
├── utils/                    # 工具函数
│   ├── api_client.py         # API调用客户端
│   ├── metrics.py            # 评估指标计算
│   └── visualizer.py         # 结果可视化
├── results/                  # 评估结果存储
│   ├── latest_result.json    # 最新测试结果
│   └── history/              # 历史测试结果
└── reports/                  # 生成的评估报告
    ├── summary_report.html   # 汇总报告
    └── detailed_analysis.md  # 详细分析
```

## 快速开始

### 1. 安装依赖
```bash
pip install requests numpy matplotlib pandas
```

### 2. 配置设置
编辑 `config.py` 文件，设置API端点和项目参数。

### 3. 运行评估
```bash
python run_evaluation.py
```

### 4. 查看结果
评估完成后，查看 `reports/` 目录下的报告文件。

## 评估指标说明

### 传统指标
- **精确率 (Precision)**: 检索到的相关结果数 / 检索到的总结果数
- **召回率 (Recall)**: 检索到的相关结果数 / 实际相关的总结果数
- **F1-Score**: 精确率和召回率的调和平均数

### 针对性指标
- **路径匹配率**: 预期文件路径的匹配程度
- **分数分布分析**: 检索结果分数的分布情况
- **代码片段质量**: 返回代码片段的相关性评估
- **Top-K准确率**: 前K个结果中相关结果的比例

## 测试数据集

测试数据集包含三大类查询：

### 样式相关查询
- 积分商品列表样式
- 优惠券卡片设计
- 按钮渐变效果
- 无数据展示样式

### 功能相关查询
- 用户登录逻辑
- 积分兑换功能
- 商品列表加载
- 订单提交流程

### 布局相关查询
- 商品卡片布局
- 页面响应式设计
- 弹性布局实现
- 组件排列方式

## 使用说明

### 自定义测试案例
编辑 `test_dataset.json` 添加新的测试案例：

```json
{
  "idx": "custom-001",
  "query": "您的查询语句",
  "category": "style|function|layout",
  "expected_results": [
    {
      "path": "期望的文件路径",
      "relevance_score": 1.0,
      "reason": "相关性说明"
    }
  ]
}
```

### 配置API参数
在 `config.py` 中修改API调用参数：

```python
API_CONFIG = {
    "base_url": "http://localhost:8000",
    "endpoint": "/api/search/code_by_hyde",
    "project_id": "5",
    "limit": 10
}
```

## 报告解读

### 汇总报告
- 整体性能指标
- 各类别查询表现
- 问题区域识别
- 改进建议

### 详细分析
- 每个查询的具体结果
- 分数分布图表
- 错误案例分析
- 优化方向建议

## 故障排除

### 常见问题
1. **API连接失败**: 检查服务是否启动，端口是否正确
2. **结果为空**: 检查project_id是否正确
3. **评估指标异常**: 检查测试数据集格式是否正确

### 调试模式
启用调试模式查看详细日志：
```bash
python run_evaluation.py --debug
```

## 贡献指南

欢迎提交改进建议和新的测试案例：
1. 添加新的查询类别
2. 改进评估指标算法
3. 优化可视化展示
4. 增强错误处理

## 更新日志

- v1.0.0: 基础评估功能实现
- v1.1.0: 增加可视化报告
- v1.2.0: 支持批量测试和历史对比 

### 🆕 新评估框架特性
- 🏆 **三维评估体系** - 相关性(50%) + 全面性(30%) + 可用性(20%)
- 📊 **科学权重分配** - 基于实际使用场景的权重设计
- 🎯 **前k结果评估** - 专注于最重要的前k个检索结果
- 💡 **详细结果注释** - 每个指标都有清晰的解释和改进建议
- 🎨 **颜色等级标识** - 根据分数自动显示优秀/良好/一般/较差等级

### 功能特性
- 🚀 自动化测试执行
- 📈 可视化结果分析
- 🔄 传统指标对比 - 保留F1、精确率、召回率用于对比
- 🎯 针对uni-app项目优化的测试案例

## 🔧 配置您的代码检索模型

### API配置说明

在开始评估之前，您需要在 `config.py` 中配置您的代码检索模型参数：

```python
# API配置
API_CONFIG = {
    "base_url": "http://localhost:8000",           # 您的模型服务地址
    "endpoint": "/api/search/code_by_hyde",        # 您的API端点路径
    "project_id": "5",                             # 您的项目ID
    "limit": 10,                                   # 每次请求返回的结果数量
    "timeout": 30                                  # 请求超时时间（秒）
}
```

### 配置步骤

1. **模型服务地址**: 将 `base_url` 改为您的代码检索模型服务地址
2. **API端点**: 根据您的模型API修改 `endpoint`
3. **项目ID**: 设置您要评估的代码库项目ID
4. **返回数量**: 根据需要调整 `limit` 参数

### API接口要求

您的代码检索模型需要支持以下请求格式：

**请求方式**: POST  
**Content-Type**: application/json

**请求参数**:
```json
{
    "q": "搜索查询文本",
    "limit": 10,
    "project_id": "您的项目ID"
}
```

**返回格式**:
```json
{
    "results": [
        {
            "path": "文件路径",
            "score": 0.85,
            "snippet": "代码片段",
            "repo": "仓库信息",
            "start_line": 0,
            "end_line": 50
        }
    ]
}
```

### 使用方法
```bash
cd code_search_evaluation
python run_evaluation.py
```

### 新评估框架演示
```bash
# 查看新评估框架注释演示
python demo_results.py

# 测试新评估框架功能
python test_fix.py

# 快速测试新框架
python quick_start.py

# 运行完整的新框架评估
python run_evaluation.py
```

### 新评估框架 (现已包含详细注释)
**主要指标 (新框架)**:
- 🏆 **综合评分** - 相关性×0.5 + 全面性×0.3 + 可用性×0.2
- 📊 **相关性 (50%)** - 前k个结果中相关数/k (精确率)
- 📈 **全面性 (30%)** - 前k个结果中的相关数/总相关数 (召回率)
- 🎯 **可用性 (20%)** - 平均倒数排名 (MRR)

**传统指标 (对比参考)**:
- 📐 **精确率** - 检索到的结果中相关结果的比例
- 🎪 **召回率** - 所有相关结果中被检索到的比例  
- ⚖️ **F1-Score** - 精确率和召回率的调和平均数

**详细分析**:
- 🔍 **路径匹配率** - 综合考虑精确、部分和扩展名匹配
- 📈 **Top-K准确率** - 前K个结果中相关结果的比例
- 🎨 **多样性分析** - 基于文件类型和目录的多样性

### 测试数据
包含20个针对uni-app项目的测试案例，涵盖：
- 样式相关查询
- 功能实现查询  
- 布局设计查询
- API接口查询

### 依赖项
```bash
pip install requests numpy
```

### 项目结构
```
code_search_evaluation/
├── config.py              # 配置文件
├── run_evaluation.py      # 主评估脚本
├── quick_start.py         # 快速测试脚本
├── evaluator.py           # 评估器核心逻辑
├── test_dataset.json      # 测试数据集
├── utils/                 # 工具模块
│   ├── api_client.py      # API客户端
│   ├── metrics.py         # 评估指标计算
│   └── result_formatter.py # 结果格式化
├── results/               # 评估结果目录 (gitignore)
├── reports/               # 报告目录 (gitignore)
└── README.md
```

### 开始评估

1. 启动您的代码检索模型服务
2. 修改 `config.py` 中的API配置
3. 运行快速测试: `python quick_start.py`
4. 运行完整评估: `python run_evaluation.py`

### 许可证

本项目基于MIT许可证开源。 