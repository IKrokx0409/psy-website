import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AIEngineConfig:
    # LLM — 可替换供应商，不绑定单一服务
    llm_provider: str = field(default_factory=lambda: os.getenv("AI_LLM_PROVIDER", "deepseek"))
    llm_api_key: str = field(default_factory=lambda: os.getenv("AI_LLM_API_KEY", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("AI_LLM_MODEL", "deepseek-chat"))
    llm_base_url: str = field(default_factory=lambda: os.getenv("AI_LLM_BASE_URL", "https://api.deepseek.com"))

    # Embedding — 默认使用本地中文模型，无需 API
    embedding_model: str = field(default_factory=lambda: os.getenv("AI_EMBEDDING_MODEL", "BAAI/bge-base-zh-v1.5"))
    embedding_dim: int = 768  # bge-base-zh 输出维度

    # 检索参数
    top_k: int = 10                      # 初始召回数量
    rerank_top_k: int = 3                # 重排序后保留数量
    retrieval_score_threshold: float = 0.4  # 质量门控阈值
    hybrid_alpha: float = 0.7            # 语义检索权重（1-alpha 为 BM25 权重）

    # 对话记忆
    max_history_turns: int = 10          # 滑动窗口大小

    # 危机检测关键词（规则层，语义层在 CrisisTool 内实现）
    crisis_keywords: list = field(default_factory=lambda: [
        "自杀", "自残", "不想活", "活不下去", "去死", "结束生命",
        "割腕", "跳楼", "轻生", "了结", "活着没意思",
    ])

    # Database — 复用已有环境变量
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
