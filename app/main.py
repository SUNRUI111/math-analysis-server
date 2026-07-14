from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import uvicorn
from openai import AsyncOpenAI 
import os
import yaml
import random
from typing import List, Optional, Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

app = FastAPI(title="AI 数学智慧树后端引擎")

# 允许前端 Vue 跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 生产环境建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1-核心知识点树状数据
KNOWLEDGE_TREE_DATA = {
    "id": "root_math_mind",
    "name": "数学核心思维图谱",
    "type": "root",
    "children": [
        {
            "id": "branch_num_sense",
            "name": "代数基础",
            "status": "",
            "children": [
                { "id": "NUM_FRACTION_CORE", "name": "分数与百分数", "status": "" },
                { "id": "NUM_RATIO_MIND", "name": "比与比例", "status": "" },
                { "id": "NUM_SYMBOL_VAR", "name": "方程", "status": "" }
            ]
        },
        {
            "id": "branch_spatial_geometry",
            "name": "几何空间",
            "status": "",
            "children": [
                { "id": "GEO_DIM_TRANS", "name": "平面与立体", "status": "" },
                { "id": "GEO_CUT_COMBINE", "name": "图形转化", "status": "" },
                { "id": "GEO_MEASURE_MIND", "name": "圆的公式", "status": "" }
            ]
        },
        {
            "id": "branch_modeling_app",
            "name": "应用题",
            "status": "",
            "children": [
                { "id": "APP_WHOLE_PART", "name": "局部求整体", "status": "" },
                { "id": "APP_FORWARD_REVERSE", "name": "工程问题", "status": "" },
                { "id": "APP_OPTIMIZATION", "name": "统筹规划", "status": "" }
            ]
        },
        {
            "id": "branch_logical_reasoning",
            "name": "逻辑推理",
            "status": "",
            "children": [
                { "id": "LOG_PIGEONHOLE", "name": "抽屉原理", "status": "" },
                { "id": "LOG_INDUCTION", "name": "规律找寻", "status": "" },
                { "id": "LOG_CLASSIFY", "name": "分类讨论", "status": "" }
            ]
        },
        {
            "id": "branch_data_probability",
            "name": "统计概率",
            "status": "",
            "children": [
                { "id": "STAT_TREND_ANALYSIS", "name": "图表分析", "status": "" },
                { "id": "STAT_PROB_MIND", "name": "可能性与概率", "status": "" }
            ]
        }
    ]
}

# 接口 1: 获取整棵知识树
@app.get("/api/knowledge-tree")
async def get_knowledge_tree():
    return KNOWLEDGE_TREE_DATA

# 2-各叶子节点的初始问题
NODE_INIT_QUESTIONS = {
    "NUM_FRACTION_CORE": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>分数与百分数</span>吧！",
        "question": "一根绳子，剪去了它的 <span style='color: #e67e22; font-weight: bold;'>1/3</span>，还剩下 <span style='color: #2ecc71; font-weight: bold;'>1/3米</span>。你觉得‘剪去的 <span style='color: #e67e22; font-weight: bold;'>1/3</span>’和‘剩下的 <span style='color: #2ecc71; font-weight: bold;'>1/3米</span>’意思一样吗？它们分别表示什么呢？"
    },
    "NUM_RATIO_MIND": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>比与比例</span>吧！",
        "question": "一杯可口蜂蜜水的配方是‘蜂蜜和水的比是 <span style='color: #e67e22; font-weight: bold;'>1:5</span>’。如果现在杯子里有 <span style='color: #2ecc71; font-weight: bold;'>20毫升</span> 的蜂蜜，你打算加多少毫升的水来保持美味呢？你是怎么算出来的？"
    },
    "NUM_SYMBOL_VAR": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>方程</span>吧！",
        "question": "如果小明今年的年龄是 a 岁，小红比小明大 <span style='color: #2ecc71; font-weight: bold;'>3岁</span>。那 <span style='color: #2ecc71; font-weight: bold;'>5年后</span>，小红比小明大几岁呢？你能用含有字母的式子表示 <span style='color: #2ecc71; font-weight: bold;'>5年后</span> 小红的年龄吗？"
    },
    "GEO_DIM_TRANS": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>平面与立体</span>吧！",
        "question": "想象一下，把一个标准的<span style='color: #e67e22; font-weight: bold;'>正方体</span>纸盒沿着几条棱剪开，平铺在桌子上。它会变成一个由 <span style='color: #2ecc71; font-weight: bold;'>6个</span> 正方形组成的平面图形。反过来，是不是任意 <span style='color: #2ecc71; font-weight: bold;'>6个</span> 正方形连在一起的图形，都能折成正方体呢？你觉得哪种形状肯定不行？"
    },
    "GEO_CUT_COMBINE": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>图形转化</span>吧！",
        "question": "有一个<span style='color: #2ecc71; font-weight: bold;'>平行四边形</span>，我们如果在它的一侧切下一个<span style='color: #e67e22; font-weight: bold;'>直角三角形</span>，平移到另一侧拼上去，它就变成了一个<span style='color: #2ecc71; font-weight: bold;'>长方形</span>。这时候，它的‘面积’和‘周长’和原来相比，分别发生变化了吗？为什么？"
    },
    "GEO_MEASURE_MIND": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>圆的公式</span>吧！",
        "question": "在推导圆的面积时，课本上把<span style='color: #e67e22; font-weight: bold;'>圆</span>切成许多个<span style='color: #2ecc71; font-weight: bold;'>小扇形</span>，然后拼成一个近似的<span style='color: #e67e22; font-weight: bold;'>长方形</span>。你想过没有，如果把圆切得‘无限碎’，拼成的图形会发生什么奇妙的变化？长方形的长和宽又分别对应圆的什么部分呢？"
    },
    "APP_WHOLE_PART": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>局部求整体</span>吧！",
        "question": "修路队修一条路，第一天修了全长的 <span style='color: #e67e22; font-weight: bold;'>1/4</span>，正好是 <span style='color: #2ecc71; font-weight: bold;'>200米</span>。第二天他们又修了剩下的 <span style='color: #e67e22; font-weight: bold;'>1/2</span>。这条路一共长多少米？你能试着画一个线段图，或者说说你的第一步是怎么思考的吗？"
    },
    "APP_FORWARD_REVERSE": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>工程问题</span>吧！",
        "question": "甲乙两辆汽车同时从相距 <span style='color: #2ecc71; font-weight: bold;'>300千米</span> 的两地相对开出，<span style='color: #2ecc71; font-weight: bold;'>3小时后</span> 相遇。如果甲车每小时行 <span style='color: #2ecc71; font-weight: bold;'>45千米</span>，你打算怎么求出乙车的速度呢？可以用几种不同的思路来解释吗？"
    },
    "APP_OPTIMIZATION": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>统筹规划</span>吧！",
        "question": "有 <span style='color: #2ecc71; font-weight: bold;'>40个</span> 同学去划船，大船每条坐 <span style='color: #2ecc71; font-weight: bold;'>6人</span>，租金 <span style='color: #2ecc71; font-weight: bold;'>30元</span>；小船每条坐 <span style='color: #2ecc71; font-weight: bold;'>4人</span>，租金 <span style='color: #2ecc71; font-weight: bold;'>24元</span>。怎样租船最省钱，而且所有人都能坐上船不留空位？你的核心设计原则是什么？"
    },
    "LOG_PIGEONHOLE": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>抽屉原理</span>吧！",
        "question": "把 <span style='color: #2ecc71; font-weight: bold;'>5个</span> 苹果放进 <span style='color: #2ecc71; font-weight: bold;'>4个</span> 抽屉里，不管怎么放，总有一个抽屉里至少放进了 <span style='color: #2ecc71; font-weight: bold;'>2个</span> 苹果。你觉得这句话说得对吗？如果换成 <span style='color: #2ecc71; font-weight: bold;'>11个</span> 苹果放进 <span style='color: #2ecc71; font-weight: bold;'>5个</span> 抽屉，又会发生什么好玩的事？"
    },
    "LOG_INDUCTION": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>规律找寻</span>吧！",
        "question": "用火柴棒摆正方形：摆 <span style='color: #2ecc71; font-weight: bold;'>1个</span> 用 <span style='color: #2ecc71; font-weight: bold;'>4根</span>，摆 <span style='color: #2ecc71; font-weight: bold;'>2个</span> 用 <span style='color: #2ecc71; font-weight: bold;'>7根</span>，摆 <span style='color: #2ecc71; font-weight: bold;'>3个</span> 用 <span style='color: #2ecc71; font-weight: bold;'>10根</span>……如果我们要一口气摆 n 个这样连续的正方形，需要多少根火柴棒？你是怎么从前几个特例里发现火柴棒增加的节奏的？"
    },
    "LOG_CLASSIFY": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>分类讨论</span>吧！",
        "question": "用数字卡片 <span style='color: #2ecc71; font-weight: bold;'>0、1、2 </span> 可以组成多少个没有重复数字的三位数？在组合的过程中，百位数字有什么特殊的要求吗？你是按照什么顺序数才保证不会数漏的？"
    },
    "STAT_TREND_ANALYSIS": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>图表分析</span>吧！",
        "question": "一个班有 <span style='color: #2ecc71; font-weight: bold;'>5个</span> 学生，其中 <span style='color: #2ecc71; font-weight: bold;'>4个人</span> 的数学成绩都是 <span style='color: #2ecc71; font-weight: bold;'>60分</span>，只有 <span style='color: #2ecc71; font-weight: bold;'>1个人</span> 得了 <span style='color: #2ecc71; font-weight: bold;'>100分</span>。老师说‘我们班的平均分是 <span style='color: #2ecc71; font-weight: bold;'>68分</span>，大家都及格且考得不错’，你觉得这个平均数能代表大家的真实水平吗？为什么？"
    },
    "STAT_PROB_MIND": {
        "welcome": "哈喽！一起试试<span style='color: #e67e22; font-weight: bold;'>可能性与概率</span>吧！",
        "question": "一枚均匀的硬币，抛掷了 <span style='color: #2ecc71; font-weight: bold;'>5次</span>，结果全都是‘正面朝上’。现在准备抛掷第 <span style='color: #2ecc71; font-weight: bold;'>6次</span>，你觉得第 <span style='color: #2ecc71; font-weight: bold;'>6次</span> 正面朝上的可能性，会比反面朝上的可能性大吗？为什么？"
    }
}

class StartDiagnoseRequest(BaseModel):
    node_id: str

# 接口 2: 获取某个叶子节点的初始问题
@app.post("/api/diagnose/start")
async def get_start_question(req: StartDiagnoseRequest):
    node_info = NODE_INIT_QUESTIONS.get(req.node_id, {
        "welcome": "你好！欢迎来到数学思维训练营。",
        "question": "准备好开始今天的数学思维挑战了吗？请告诉我你的想法。"
    })
    full_open = f"{node_info['welcome']}\n\n{node_info['question']}"
    return {
        "node_id": req.node_id,
        "first_message": full_open
    }

# 3- 交互询问
client = AsyncOpenAI(
    base_url=config["llm"]["deepseek_url"], 
    api_key=config["llm"]["deepseek_api_key"]
)

class DiagnoseRequest(BaseModel):
    node_id: str
    user_input: str
    history: list

# 接口 3: AI 诊断流式传输
@app.post("/api/diagnose/stream")
async def diagnose_stream(req: DiagnoseRequest):
    system_prompt = (
        "你是一位严谨、精炼的小学数学启发式诊断专家。你的唯一任务是通过苏格拉底式追问，摸清学生对当前知识点的真实掌握情况。\n"
        f"当前诊断的知识点ID是: {req.node_id}\n\n"
        "【沟通与语言控制（核心）】\n"
        "1. 严禁使用任何铺垫型废话。禁止说“你这个问题问得好”、“算得对”、“太棒了”、“来我们一起想想”等毫无意义的夸奖和客套话。\n"
        "2. 直奔主题：直接针对学生的回答进行反问、追问或指出矛盾。每轮发言绝不能超过 2 句话，总字数严格控制在 60 字以内。\n"
        "3. 严禁直接给出题目答案或解题步骤，继续保持苏格拉底式追问。\n\n"
        "【数据高亮规范】\n"
        "为了帮学生区分“量（带单位）”与“率（不带单位）”，你必须对文本中出现的数字应用以下 Markdown 颜色样式：\n"
        "- 对于【带单位的具体数量】（如 2/3米、2/9米），必须使用绿色高亮，格式为：<span style='color: #2ecc71; font-weight: bold;'>2/3米</span>\n"
        "- 对于【不带单位的分率/比例】（如 1/3、1/4），必须使用橙色高亮，格式为：<span style='color: #e67e22; font-weight: bold;'>1/3</span>\n\n"
        "【量化诊断与暗号触发标准（严格遵循）】\n"
        "你必须通过以下三个量化梯级来判断学生的掌握情况，并在满足条件时在发言最后一行单独输出判定暗号：\n\n"
        "1. [STATUS_CHANGE]:green (彻底掌握) 触发硬性标准：\n"
        "   - 学生不仅给出了正确的最终计算结果，且在后续追问中，能够准确用语言说出底层的核心概念（如能分清什么是比例、什么是具体长度，或清晰说出年龄差不变的道理）。\n"
        "   - 必须经历过至少一次你的‘反问/故意设陷阱挑战’且立场坚定、逻辑自洽。\n\n"
        "2. [STATUS_CHANGE]:yellow (概念模糊/不稳定) 触发硬性标准：\n"
        "   - 学生的最终答案算对了，但在你的进一步追问中，表现出犹豫、似懂非懂，或者无法解释清楚为什么这么算。\n"
        "   - 或者，学生在面对你的反问或陷阱时，立刻动摇，表现出逻辑前后矛盾。\n\n"
        "3. [STATUS_CHANGE]:red (存在严重漏洞/完全不会) 触发硬性标准：\n"
        "   - 面对初始问题或第一次追问，学生直接回答“不知道”、“不会”，或者给出了完全风马牛不相及的低级逻辑错误（如把 1:5 的比例直接当成除以 5 计算）。\n"
        "   - 连续两轮高难度追问均无法切入正题。\n\n"
        "【输出行为与终止判定约束（严格执行）】\n"
        "1. 判定暗号的状态值【只能】从 green、yellow、red 中三选一。受高亮规范干扰而输出 orange 或其他任何颜色均属严重违规。\n"
        "2. ⚠️一旦你决定在最后一行输出 [STATUS_CHANGE] 暗号，代表本轮诊断正式结束。在此次回复的正文中，【绝对禁止抛出任何新问题或追问】。你只需直接说出最终的掌握结果判定即可（例如：‘本轮思维摸底已完成。’），然后立即附上暗号结束对话。"
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in req.history:
        content_text = msg.get("content") or msg.get("text") or ""
        messages.append({
            "role": msg["role"], 
            "content": content_text
        })
    
    if req.user_input:
        messages.append({"role": "user", "content": req.user_input})

    async def stream_generator():
        try:
            response = await client.chat.completions.create(
                model=config["llm"]["deepseek_model"],
                messages=messages,
                stream=True,
                temperature=0.3
            )
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield f"data: {content}\n\n"
        except Exception as e:
            yield f"data: [错误] 诊断引擎通信异常: {str(e)}\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")

# 4- 训练模块：导航树结构
TRAIN_TREE_DATA = {
    "id": "root_training_mind",
    "name": "数学实操训练图谱",
    "type": "root",
    "children": [
        {
            "id": "branch_num_sense",
            "name": "代数基础",
            "status": "",
            "children": [
                { "id": "TRAIN_NUM_FRACTION_VISUAL", "name": "分数的动态切割", "resource_id": "RES_NUM_FRACTION_VISUAL" },
                { "id": "TRAIN_NUM_RATIO_BALANCE", "name": "方程与比例平衡", "resource_id": "RES_NUM_RATIO_BALANCE" }
            ]
        },
        {
            "id": "branch_spatial_geometry",
            "name": "几何空间",
            "status": "",
            "children": [
                { "id": "TRAIN_GEO_BASE_PERCEIVE", "name": "基础图形感知", "resource_id": "RES_GEO_BASE_PERCEIVE" },
                { "id": "TRAIN_GEO_COMPREHENSIVE_QUIZ", "name": "复合图形练习", "resource_id": "RES_GEO_COMPREHENSIVE_QUIZ" }
            ]
        },
        {
            "id": "branch_modeling_app",
            "name": "应用题",
            "status": "",
            "children": [
                { "id": "TRAIN_APP_WATER_FLOW", "name": "流水与注水问题", "resource_id": "RES_APP_WATER_FLOW" },
                { "id": "TRAIN_APP_LINE_SCENE", "name": "行程与相遇问题", "resource_id": "RES_APP_LINE_SCENE" }
            ]
        },
        {
            "id": "branch_logical_reasoning",
            "name": "逻辑推理",
            "status": "",
            "children": [
                { "id": "TRAIN_LOG_BOX_DROP", "name": "抽屉原理可视化", "resource_id": "RES_LOG_BOX_DROP" },
                { "id": "TRAIN_LOG_MATRIX_ELIMINATE", "name": "排除法解谜题", "resource_id": "RES_LOG_MATRIX_ELIMINATE" }
            ]
        },
        {
            "id": "branch_data_probability",
            "name": "统计概率",
            "status": "",
            "children": [
                { "id": "TRAIN_STAT_DICE_SIM", "name": "抛硬币与掷骰子", "resource_id": "RES_STAT_DICE_SIM" },
                { "id": "TRAIN_STAT_CHART_DYNAMIC", "name": "折线与条形统计图", "resource_id": "RES_STAT_CHART_DYNAMIC" }
            ]
        }
    ]
}

# 从 JSON 文件动态加载资源库数据
JSON_PATH = os.path.join(BASE_DIR, "train_resources.json")
def load_train_resources() -> dict:
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 接口4:训练导航树结构
@app.get("/api/train/tree")
async def get_train_tree():
    return {
        "status": "success",
        "data": TRAIN_TREE_DATA
    }

# 修改后端的请求模型
class TrainStartRequest(BaseModel):
    parent_node_id: str
    leaf_node_id: str
    resource_id: str  # 对应前端传来的 RES_XXX


@app.post("/api/train/start")
async def start_train(request: TrainStartRequest):
    res_id = request.resource_id

    # 直接读取 JSON 资源库
    json_path = os.path.join(os.path.dirname(__file__), "train_resources.json")
    if not os.path.exists(json_path):
        raise HTTPException(status_code=500, detail="本地资源库未找到")

    with open(json_path, "r", encoding="utf-8") as f:
        resources_data = json.load(f)

    if res_id not in resources_data:
        raise HTTPException(
            status_code=404, detail="该知识点的 3D 渲染模板尚未录入资源库"
        )

    node_template = json.loads(json.dumps(resources_data[res_id]))

    # 包含题库池则动态随机抽题
    if "quizzes_pool" in node_template and isinstance(
        node_template["quizzes_pool"], list
    ):
        pool = node_template["quizzes_pool"]
        if pool:
            node_template["quiz_data"] = random.choice(pool)
        node_template.pop("quizzes_pool", None)

    return node_template


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)