# AI 数学智慧树后端引擎

基于 FastAPI 和大模型驱动的小学数学诊断与训练平台后端服务。

## 项目概述

本项目是一个面向小学数学教育的智能诊断与训练系统，核心功能包括：

- **知识图谱导航**：五大数学思维领域的知识树结构
- **AI 苏格拉底式诊断**：基于 DeepSeek 大模型的启发式追问诊断
- **3D 可视化训练**：交互式三维场景的数学概念可视化训练
- **流式响应**：实时的 AI 对话流式传输

## 技术栈

- **框架**: FastAPI 0.100+
- **服务器**: Uvicorn 0.20+
- **数据验证**: Pydantic 2.0+
- **大模型**: DeepSeek V4 Flash (OpenAI API 兼容)
- **配置**: PyYAML 6.0+

## 项目结构

```
math_analysis_server/
├── app/
│   ├── main.py                 # FastAPI 入口，路由注册与核心逻辑
│   ├── config.yaml             # LLM API 配置文件
│   ├── train_resources.json    # 3D 训练资源库
│   ├── ai/                     # AI/LLM 模块（预留扩展）
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── llm_client.py
│   │   └── prompts.py
│   ├── api/                    # 路由层（预留扩展）
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── diagnose.py
│   │   │   └── questions.py
│   │   └── router.py
│   ├── core/                   # 核心配置（预留扩展）
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── schemas/                # 数据模型（预留扩展）
│   │   ├── diagnose.py
│   │   ├── question.py
│   │   └── student.py
│   └── services/               # 业务逻辑（预留扩展）
│       ├── adaptive_engine.py
│       └── graph_service.py
├── data/                       # 结构化数据
│   ├── grade6_graph.json       # 六年级知识图谱
│   └── question_bank.json      # 题库数据
├── Dockerfile                  # Docker 部署配置
├── requirements.txt            # Python 依赖
└── README.md                   # 项目文档
```

## 快速开始

### 环境要求

- Python 3.9+
- 有效的 DeepSeek API Key（配置在 `app/config.yaml` 中）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python app/main.py
```

服务默认运行在 `http://localhost:8000`

### Docker 部署

```bash
docker build -t math-analysis-server .
docker run -p 8000:8000 math-analysis-server
```

## API 接口

### 1. 获取知识树

**GET** `/api/knowledge-tree`

返回完整的数学知识树结构，包含五大分支：

- 代数基础（分数与百分数、比与比例、方程）
- 几何空间（平面与立体、图形转化、圆的公式）
- 应用题（局部求整体、工程问题、统筹规划）
- 逻辑推理（抽屉原理、规律找寻、分类讨论）
- 统计概率（图表分析、可能性与概率）

### 2. 开始诊断

**POST** `/api/diagnose/start`

请求体：
```json
{
  "node_id": "NUM_FRACTION_CORE"
}
```

返回指定知识点的初始诊断问题。

### 3. AI 诊断流式对话

**POST** `/api/diagnose/stream`

请求体：
```json
{
  "node_id": "NUM_FRACTION_CORE",
  "user_input": "学生的回答内容",
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

返回 SSE（Server-Sent Events）流式响应，包含 AI 诊断追问和状态判定。

**状态判定标准**：
- `[STATUS_CHANGE]:green` - 彻底掌握：能准确说出核心概念，经得住反问挑战
- `[STATUS_CHANGE]:yellow` - 概念模糊：答案正确但解释不清，立场不坚定
- `[STATUS_CHANGE]:red` - 存在漏洞：直接回答不会，或逻辑错误明显

### 4. 获取训练导航树

**GET** `/api/train/tree`

返回训练模块的导航树结构。

### 5. 开始训练

**POST** `/api/train/start`

请求体：
```json
{
  "parent_node_id": "branch_num_sense",
  "leaf_node_id": "TRAIN_NUM_FRACTION_VISUAL",
  "resource_id": "RES_NUM_FRACTION_VISUAL"
}
```

返回指定训练资源的配置信息，包含 3D 场景参数和题目数据。

## 训练资源

系统内置以下交互式训练资源：

| 资源ID | 名称 | 类型 | 描述 |
|--------|------|------|------|
| RES_NUM_FRACTION_VISUAL | 分数的动态切割 | 3D沙盒 | 数轴分数可视化，可调分子分母 |
| RES_NUM_RATIO_BALANCE | 方程与比例平衡 | 3D沙盒 | 坐标系直线变化，可调斜率截距 |
| RES_GEO_BASE_PERCEIVE | 基础图形感知 | 3D沙盒 | 多种几何图形，含周长面积公式 |
| RES_GEO_COMPREHENSIVE_QUIZ | 复合图形练习 | 3D互动测验 | 5道立体几何应用题 |
| RES_APP_WATER_FLOW | 流水与注水问题 | 3D互动测验 | 水池进出水动画模拟 |
| RES_APP_LINE_SCENE | 行程与相遇问题 | 3D互动测验 | 两车相对开出动画模拟 |
| RES_LOG_BOX_DROP | 抽屉原理可视化 | 3D互动测验 | 三维抽屉与彩球分配动画 |
| RES_LOG_MATRIX_ELIMINATE | 排除法解谜题 | 3D互动测验 | 宝箱推理动画 |
| RES_STAT_DICE_SIM | 抛硬币与掷骰子 | 3D互动测验 | 双骰子抛掷概率模拟 |
| RES_STAT_CHART_DYNAMIC | 折线与条形统计图 | 3D互动测验 | 动态柱状图展示 |

## 配置说明

`app/config.yaml` 配置文件：

```yaml
llm:
  deepseek_url: "https://api.deepseek.com/v1"
  deepseek_api_key: "your-api-key"
  deepseek_model: "deepseek-v4-flash"
  siliconflow_url: "https://api.siliconflow.cn/v1"
  siliconflow_api_key: "your-api-key"
```

## 注意事项

1. **端口占用**：服务使用 8000 端口，启动前确保端口未被占用
2. **API Key**：需配置有效的 DeepSeek API Key 才能使用 AI 诊断功能
3. **CORS**：当前配置允许所有来源访问，生产环境建议限制具体域名
4. **uvicorn reload**：开发模式下会启动两个进程，结束时需彻底清理

## 许可证

MIT License
