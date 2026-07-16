math-diagnosis-server/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 入口，配置路由、CORS、中间件等
│   ├── core/                   # 核心配置与全局工具
│   │   ├── config.py           # 环境变量、LLM API Key、数据库连接配置
│   │   ├── security.py         # JWT Token 校验（如果需要小侄女登录）
│   │   └── database.py         # 数据库初始化 (SQLAlchemy 或 Motor)
│   ├── api/                    # 路由层 (Endpoints)
│   │   ├── v1/
│   │   │   ├── auth.py         # 用户/学生认证
│   │   │   ├── questions.py    # 题库获取、自适应出题
│   │   │   └── diagnose.py     # 核心：AI 诊断对话（SSE 流式接口在此）
│   │   └── router.py           # 路由总聚合
│   ├── schemas/                # Pydantic 数据验证模型
│   │   ├── student.py
│   │   ├── question.py
│   │   └── diagnose.py         # 诊断输入输出的 Schema
│   ├── services/               # 业务逻辑层 (纯粹的 Python 逻辑)
│   │   ├── adaptive_engine.py  # 自适应测试算法逻辑（根据对错计算下一题）
│   │   └── graph_service.py    # 知识图谱解析服务
│   ├── ai/                     # AI/LLM 专属层 (核心)
│   │   ├── __init__.py
│   │   ├── llm_client.py       # 封装 OpenAI/DeepSeek 的 Async 客户端
│   │   ├── prompts.py          # 统一管理苏格拉底追问、漏洞总结的 Prompt
│   │   └── agent.py            # 封装对话状态机、Tool Call、流式解析
│   └── static/                 # 静态资源（如有需要本地存储的数学几何图片）
├── data/                       # 结构化数据定义
│   ├── grade6_graph.json       # 六年级数学知识图谱（节点与依赖关系关系）
│   └── question_bank.json      # 种子题库（包含知识点 Tag、难度系数）
├── tests/                      # 单元测试（重点测试 AI 解析和算法分支）
├── .env                        # 环境变量（API_KEY, DB_URL）
├── requirements.txt            # 依赖包
└── README.md

cd /Users/rui/Documents/课程/第二学期/12、其他学习资料/math_analysis_uniapp
git add .
git commit -m "更新后台三维试题逻辑"
git push