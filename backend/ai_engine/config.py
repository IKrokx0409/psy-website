# ============================================================
# 【学习顺序 ①】config.py — 全局配置中心
#
# 学习目标：
#   理解一个 AI 系统有哪些"旋钮"可以调，以及为什么要把配置
#   集中管理而不是散落在各个文件里。
#
# 核心概念：
#   "配置驱动设计" —— 所有可变参数集中在一处，通过 .env 文件
#   注入，修改行为不需要改代码，只改配置文件即可。
# ============================================================

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()  # 从项目根目录的 .env 文件读取环境变量


@dataclass
class AIEngineConfig:
    """AI 引擎的全局配置。

    【为什么用 dataclass？】
    dataclass 是 Python 的语法糖，自动生成 __init__ 等方法。
    这里每个字段都有默认值（从环境变量读取），创建实例时直接
    AIEngineConfig() 即可，不需要传任何参数。

    【为什么用环境变量而不是直接写死？】
    API Key 等敏感信息不能写进代码（会被 git 记录），
    本地开发和服务器部署用不同配置（不同的数据库地址等），
    改配置不需要改代码、不需要重新部署。
    """

    # ── LLM（大语言模型）配置 ──────────────────────────────────────────────
    # LLM 就是 GPT/DeepSeek 这类"会说话的模型"，负责理解问题和生成回复。
    # 通过 base_url 可以切换到任何兼容 OpenAI 协议的服务（DeepSeek/通义千问等）。
    llm_provider: str = field(default_factory=lambda: os.getenv("AI_LLM_PROVIDER", "deepseek"))
    llm_api_key: str = field(default_factory=lambda: os.getenv("AI_LLM_API_KEY", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("AI_LLM_MODEL", "deepseek-chat"))
    llm_base_url: str = field(default_factory=lambda: os.getenv("AI_LLM_BASE_URL", "https://api.deepseek.com"))

    # ── Embedding（向量化）配置 ────────────────────────────────────────────
    # Embedding 模型把文字转成数字向量，用于"语义搜索"（见 rag/embedder.py）。
    # 这里用的是本地中文模型，不需要调外部 API，断网也能用。
    # dim=768 表示每段文字被压缩成 768 个数字组成的向量。
    embedding_model: str = field(default_factory=lambda: os.getenv("AI_EMBEDDING_MODEL", "BAAI/bge-base-zh-v1.5"))
    embedding_dim: int = 768

    # ── 检索参数 ───────────────────────────────────────────────────────────
    # 这三个参数控制"从知识库里找多少内容、保留多少、质量要多好"。
    #
    # top_k=10：第一步粗筛，从知识库召回 10 条候选
    # rerank_top_k=3：第二步精排，从 10 条里挑出最好的 3 条给 LLM 参考
    # retrieval_score_threshold=0.4：质量门控，低于 0.4 说明知识库里没有
    #                                相关内容，Agent 会重新改写问题再搜一次
    # hybrid_alpha=0.7：混合检索的权重比例
    #   0.7 × 语义相似度（向量）+ 0.3 × 关键词匹配（BM25）
    #   纯语义有时会"词不达意"，加入关键词权重让结果更稳定
    top_k: int = 10
    rerank_top_k: int = 3
    retrieval_score_threshold: float = 0.4
    hybrid_alpha: float = 0.7

    # ── 对话记忆参数 ────────────────────────────────────────────────────────
    # LLM 本身是"无状态"的，每次调用都不记得上次说了什么。
    # 解决方法：把历史对话拼接到 prompt 里一起发给 LLM。
    # max_history_turns=10 表示最多携带最近 10 轮（用滑动窗口，太长会超出 token 限制）。
    max_history_turns: int = 10

    # ── 危机检测关键词（规则层） ────────────────────────────────────────────
    # 危机检测的第一道防线：简单字符串匹配，速度极快（毫秒级）。
    # 命中任意一个词就直接判定为 HIGH 危机，跳过后续所有 AI 处理。
    # 【为什么要有规则层？】假阴性（漏检）的代价在心理场景中极高，
    # 规则层确保这些明显的词一定被捕获，不依赖模型的"理解"。
    crisis_keywords: list = field(default_factory=lambda: [
        "自杀", "自残", "不想活", "活不下去", "去死", "结束生命",
        "割腕", "跳楼", "轻生", "了结", "活着没意思",
    ])

    # ── 数据库连接 ────────────────────────────────────────────────────────
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
