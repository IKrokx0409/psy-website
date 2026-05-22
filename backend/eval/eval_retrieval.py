"""
检索质量评测脚本 — Golden Dataset Evaluation

对比三种检索策略的效果：
  A. 纯向量检索（Bi-encoder cosine similarity）
  B. 混合检索（alpha*语义 + (1-alpha)*BM25）
  C. 混合检索 + Cross-encoder 重排序

指标：
  - Hit Rate @k：top-k 结果中至少有一条命中期望类别，的比例
  - MRR（Mean Reciprocal Rank）：期望结果排在第几位的倒数均值

用法：
  conda run -n psy_agent python -m eval.eval_retrieval
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# 确保能 import backend 包
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from ai_engine.config import AIEngineConfig
from ai_engine.rag.embedder import Embedder
from ai_engine.rag.pg_retriever import PGRetriever
from ai_engine.rag.reranker import Reranker


# ── 评测指标计算 ─────────────────────────────────────────────────────────────

def hit_rate_at_k(results: list[str], expected: str, k: int) -> float:
    """top-k 内是否有命中期望类别（0 或 1）。"""
    return 1.0 if expected in results[:k] else 0.0


def reciprocal_rank(results: list[str], expected: str) -> float:
    """期望类别首次出现位置的倒数，未命中返回 0。"""
    for i, cat in enumerate(results):
        if cat == expected:
            return 1.0 / (i + 1)
    return 0.0


# ── 评测主体 ──────────────────────────────────────────────────────────────────

async def evaluate(
    dataset: list[dict],
    retriever: PGRetriever,
    reranker: Reranker,
    top_k: int = 10,
    rerank_top_k: int = 3,
) -> dict:
    """对 dataset 中每条 query 跑三种策略，收集命中情况，返回汇总指标。"""
    metrics = {
        "vector": {"hr1": [], "hr3": [], "hr5": [], "mrr": [], "latency_ms": []},
        "hybrid": {"hr1": [], "hr3": [], "hr5": [], "mrr": [], "latency_ms": []},
        "rerank": {"hr1": [], "hr3": [], "hr5": [], "mrr": [], "latency_ms": []},
    }

    total = len(dataset)
    for i, item in enumerate(dataset):
        query = item["query"]
        expected = item["expected_category"]
        print(f"  [{i+1:02d}/{total}] {query[:30]}...", end="", flush=True)

        # ── A: 纯向量检索 ─────────────────────────────────────────────────────
        t0 = time.perf_counter()
        chunks_vec = await retriever.retrieve(query, top_k=top_k)
        lat_vec = (time.perf_counter() - t0) * 1000
        cats_vec = [c.category for c in chunks_vec]
        metrics["vector"]["hr1"].append(hit_rate_at_k(cats_vec, expected, 1))
        metrics["vector"]["hr3"].append(hit_rate_at_k(cats_vec, expected, 3))
        metrics["vector"]["hr5"].append(hit_rate_at_k(cats_vec, expected, 5))
        metrics["vector"]["mrr"].append(reciprocal_rank(cats_vec, expected))
        metrics["vector"]["latency_ms"].append(lat_vec)

        # ── B: 混合检索 ───────────────────────────────────────────────────────
        t0 = time.perf_counter()
        chunks_hyb = await retriever.hybrid_retrieve(query, top_k=top_k)
        lat_hyb = (time.perf_counter() - t0) * 1000
        cats_hyb = [c.category for c in chunks_hyb]
        metrics["hybrid"]["hr1"].append(hit_rate_at_k(cats_hyb, expected, 1))
        metrics["hybrid"]["hr3"].append(hit_rate_at_k(cats_hyb, expected, 3))
        metrics["hybrid"]["hr5"].append(hit_rate_at_k(cats_hyb, expected, 5))
        metrics["hybrid"]["mrr"].append(reciprocal_rank(cats_hyb, expected))
        metrics["hybrid"]["latency_ms"].append(lat_hyb)

        # ── C: 混合检索 + 重排序 ──────────────────────────────────────────────
        t0 = time.perf_counter()
        chunks_rr = await reranker.rerank(query, chunks_hyb, top_k=rerank_top_k)
        lat_rr = (time.perf_counter() - t0) * 1000  # 仅重排阶段耗时
        cats_rr = [c.category for c in chunks_rr]
        metrics["rerank"]["hr1"].append(hit_rate_at_k(cats_rr, expected, 1))
        metrics["rerank"]["hr3"].append(hit_rate_at_k(cats_rr, expected, 3))
        metrics["rerank"]["hr5"].append(hit_rate_at_k(cats_rr, expected, 5))
        metrics["rerank"]["mrr"].append(reciprocal_rank(cats_rr, expected))
        metrics["rerank"]["latency_ms"].append(lat_hyb + lat_rr)  # 混合+重排总耗时

        print(f"  vec_hr3={metrics['vector']['hr3'][-1]:.0f} "
              f"hyb_hr3={metrics['hybrid']['hr3'][-1]:.0f} "
              f"rr_hr3={metrics['rerank']['hr3'][-1]:.0f}")

    # ── 汇总 ──────────────────────────────────────────────────────────────────
    summary = {}
    for strategy, m in metrics.items():
        n = len(m["hr1"])
        summary[strategy] = {
            "HR@1":  round(sum(m["hr1"]) / n * 100, 1),
            "HR@3":  round(sum(m["hr3"]) / n * 100, 1),
            "HR@5":  round(sum(m["hr5"]) / n * 100, 1),
            "MRR":   round(sum(m["mrr"]) / n, 3),
            "avg_latency_ms": round(sum(m["latency_ms"]) / n, 1),
        }
    return summary


# ── 结果打印 ──────────────────────────────────────────────────────────────────

def print_report(summary: dict) -> None:
    names = {"vector": "A. 纯向量检索", "hybrid": "B. 混合检索", "rerank": "C. 混合+重排序"}
    header = f"{'策略':<18} {'HR@1':>6} {'HR@3':>6} {'HR@5':>6} {'MRR':>7} {'延迟(ms)':>10}"
    print("\n" + "=" * 60)
    print("📊 检索质量评测报告")
    print("=" * 60)
    print(header)
    print("-" * 60)
    for key, label in names.items():
        m = summary[key]
        print(
            f"{label:<18} "
            f"{m['HR@1']:>5.1f}% "
            f"{m['HR@3']:>5.1f}% "
            f"{m['HR@5']:>5.1f}% "
            f"{m['MRR']:>7.3f} "
            f"{m['avg_latency_ms']:>9.1f}"
        )
    print("=" * 60)

    # 提升幅度
    v = summary["vector"]
    r = summary["rerank"]
    delta_hr3 = r["HR@3"] - v["HR@3"]
    delta_mrr = r["MRR"] - v["MRR"]
    print(f"\n✅ 完整链路（混合+重排）vs 纯向量：")
    print(f"   HR@3 提升 {delta_hr3:+.1f}%，MRR 提升 {delta_mrr:+.3f}")
    print(f"   延迟代价：{r['avg_latency_ms'] - v['avg_latency_ms']:+.0f} ms\n")


# ── 入口 ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    cfg = AIEngineConfig()
    engine = create_async_engine(cfg.database_url, echo=False)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    dataset_path = Path(__file__).parent / "golden_dataset.json"
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))

    print(f"🚀 加载评测集：{len(dataset)} 条 Query")
    print("⏳ 首次运行会加载 Embedding 和 Reranker 模型，约需 30-60 秒...\n")

    embedder = Embedder(cfg)
    reranker = Reranker(cfg)

    async with Session() as session:
        retriever = PGRetriever(session, embedder, cfg)

        print("📝 逐条评测中：")
        summary = await evaluate(dataset, retriever, reranker)

    print_report(summary)

    # 保存 JSON 结果
    out_path = Path(__file__).parent / "eval_results.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 结果已保存至 {out_path}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
