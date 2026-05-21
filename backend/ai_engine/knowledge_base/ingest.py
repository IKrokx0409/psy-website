from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ai_engine.rag.embedder import Embedder


def _vec_literal(vec: list[float]) -> str:
    return "[" + ",".join(f"{v:.8f}" for v in vec) + "]"


def _is_xlsx_bytes(path: str) -> bool:
    """通过 magic bytes 检测文件是否为 xlsx（ZIP 格式），与扩展名无关。"""
    with open(path, "rb") as f:
        return f.read(2) == b"PK"


class KnowledgeBaseIngestor:
    """知识库入库流水线：文档解析 → 分块 → 向量化 → 写入 PostgreSQL。

    支持格式：txt / md / pdf / xlsx / csv（含以 .csv 命名的 xlsx 文件）
    Q&A 格式（xlsx/csv）每行生成 2 个分块，其余格式按滑动窗口分块。

    使用方式（命令行）：
        python -m ai_engine.knowledge_base.ingest
    """

    SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".csv", ".xlsx"}

    def __init__(
        self,
        db: AsyncSession,
        embedder: Embedder,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
    ) -> None:
        self._db = db
        self._embedder = embedder
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    # ── 公开方法 ──────────────────────────────────────────────────────────────

    async def ingest_file(self, path: str, category: str = "通用") -> int:
        """入库单个文件，返回生成的分块数量。"""
        ext = Path(path).suffix.lower()
        if ext in (".csv", ".xlsx") or _is_xlsx_bytes(path):
            return await self._ingest_qa_spreadsheet(path)
        text_content = self._read_file(path)
        chunks = self._chunk_text(text_content)
        source = Path(path).name
        embeddings = await self._embedder.embed_batch(chunks)
        count = 0
        for chunk_text, emb in zip(chunks, embeddings):
            vl = _vec_literal(emb)
            sql = text(f"""
                INSERT INTO knowledge_chunks (content, embedding, source, category, metadata)
                VALUES (:content, '{vl}'::vector, :source, :category, CAST(:metadata AS jsonb))
            """)
            await self._db.execute(sql, {
                "content": chunk_text,
                "source": source,
                "category": category,
                "metadata": json.dumps({"chunk_index": count}),
            })
            count += 1
        await self._db.commit()
        return count

    async def ingest_directory(self, dir_path: str) -> int:
        """递归入库目录下所有支持格式的文件，返回总分块数。"""
        total = 0
        for ext in self.SUPPORTED_EXTENSIONS:
            for filepath in Path(dir_path).rglob(f"*{ext}"):
                category = filepath.parent.name
                n = await self.ingest_file(str(filepath), category)
                print(f"  {filepath.name}: {n} 块")
                total += n
        return total

    # ── Q&A 电子表格 ─────────────────────────────────────────────────────────

    async def _ingest_qa_spreadsheet(self, path: str) -> int:
        """处理 Q&A 格式的 xlsx / csv 文件（含以 .csv 命名的 xlsx）。

        期望列：类别 | 问题1 | 回答1 | 问题2 | 回答2 | 关键词1 | 关键词2 | 关键词3
        每行生成 2 个分块（每组 Q&A 各一个）。
        """
        rows = self._read_spreadsheet(path)
        source = Path(path).name
        chunks: list[tuple[str, str]] = []  # (content, category)

        for row in rows:
            if len(row) < 5:
                continue
            category = str(row[0] or "通用")
            q1, a1 = str(row[1] or ""), str(row[2] or "")
            q2, a2 = str(row[3] or ""), str(row[4] or "")
            kws = "、".join(str(row[i]) for i in range(5, min(8, len(row))) if row[i])

            for q, a in ((q1, a1), (q2, a2)):
                if q and a:
                    content = f"类别：{category}\n问题：{q}\n回答：{a}"
                    if kws:
                        content += f"\n关键词：{kws}"
                    chunks.append((content, category))

        if not chunks:
            return 0

        texts = [c[0] for c in chunks]
        embeddings = await self._embedder.embed_batch(texts)
        count = 0
        for (chunk_text, chunk_cat), emb in zip(chunks, embeddings):
            vl = _vec_literal(emb)
            sql = text(f"""
                INSERT INTO knowledge_chunks (content, embedding, source, category, metadata)
                VALUES (:content, '{vl}'::vector, :source, :category, CAST(:metadata AS jsonb))
            """)
            await self._db.execute(sql, {
                "content": chunk_text,
                "source": source,
                "category": chunk_cat,
                "metadata": json.dumps({}),
            })
            count += 1
        await self._db.commit()
        return count

    def _read_spreadsheet(self, path: str) -> list[tuple]:
        """读取 xlsx 或 csv（含伪装成 .csv 的 xlsx），跳过表头。"""
        if _is_xlsx_bytes(path):
            import openpyxl
            with open(path, "rb") as f:
                wb = openpyxl.load_workbook(io.BytesIO(f.read()))
            ws = wb.active
            all_rows = list(ws.iter_rows(values_only=True))
            return all_rows[1:]  # 跳过表头
        # 真正的 CSV
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)
        return rows[1:]  # 跳过表头

    # ── 通用文本分块 ──────────────────────────────────────────────────────────

    def _chunk_text(self, text: str) -> list[str]:
        """滑动窗口分块，保留相邻块重叠以避免语义截断。"""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self._chunk_size, len(text))
            chunks.append(text[start:end])
            start += self._chunk_size - self._chunk_overlap
        return [c for c in chunks if c.strip()]

    def _read_file(self, path: str) -> str:
        """读取文件内容，支持 txt / md / pdf。"""
        ext = Path(path).suffix.lower()
        if ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()


# ── CLI 入口 ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio
    import os
    from dotenv import load_dotenv
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from sqlalchemy import text as sa_text

    load_dotenv()

    async def main() -> None:
        from ai_engine.config import AIEngineConfig
        cfg = AIEngineConfig()
        eng = create_async_engine(cfg.database_url, echo=False)
        Session = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)

        # 确保 pgvector 扩展和知识库表已创建
        migration_path = Path(__file__).parent / "migration.sql"
        migration_sql = migration_path.read_text(encoding="utf-8")
        async with eng.begin() as conn:
            for stmt in migration_sql.split(";"):
                stmt = stmt.strip()
                if stmt:
                    await conn.execute(sa_text(stmt))

        from ai_engine.rag.embedder import Embedder
        embedder = Embedder(cfg)

        docs_dir = Path(__file__).parent / "docs"
        async with Session() as session:
            ingestor = KnowledgeBaseIngestor(session, embedder)
            print(f"开始入库目录：{docs_dir}")
            total = await ingestor.ingest_directory(str(docs_dir))
            print(f"\n完成！共生成 {total} 个向量分块。")

        await eng.dispose()

    asyncio.run(main())
