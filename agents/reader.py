import json
import os
from typing import AsyncGenerator, Iterable

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from pypdf import PdfReader

DEFAULT_ALLOWED_EXTENSIONS = (
    ".md",
    ".txt",
    ".rst",
    ".log",
    ".csv",
    ".json",
    ".yaml",
    ".yml",
    ".pdf",
)


class DocumentReaderAgent(BaseAgent):
    name: str = "Agent2_DocumentReader"
    description: str = "Reads all documentation files from a directory."
    documents_dir: str
    allowed_extensions: tuple[str, ...] = DEFAULT_ALLOWED_EXTENSIONS
    max_file_chars: int = 12000
    preview_chars: int = 500
    prefer_previews: bool = False

    @staticmethod
    def _read_pdf(path: str) -> str:
        reader = PdfReader(path)
        chunks: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text:
                chunks.append(text)
        return "\n".join(chunks).strip()

    def _iter_document_paths(self) -> Iterable[str]:
        if not os.path.isdir(self.documents_dir):
            return []

        paths: list[str] = []
        for root, _, files in os.walk(self.documents_dir):
            for filename in files:
                paths.append(os.path.join(root, filename))
        return sorted(paths)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        documents: list[dict[str, object]] = []
        for path in self._iter_document_paths():
            rel_path = os.path.relpath(path, self.documents_dir)
            _, ext = os.path.splitext(path.lower())
            if ext and ext not in self.allowed_extensions:
                documents.append(
                    {
                        "path": rel_path,
                        "content": "",
                        "truncated": False,
                        "content_available": False,
                        "note": f"Unsupported file type: {ext}",
                    }
                )
                continue
            try:
                if ext == ".pdf":
                    content = self._read_pdf(path)
                else:
                    with open(
                        path, "r", encoding="utf-8", errors="replace"
                    ) as handle:
                        content = handle.read()
            except Exception as exc:
                documents.append(
                    {
                        "path": rel_path,
                        "error": f"Failed to read: {exc}",
                        "content": "",
                        "truncated": False,
                        "content_available": False,
                    }
                )
                continue

            truncated = len(content) > self.max_file_chars
            if truncated:
                content = content[: self.max_file_chars]

            documents.append(
                {
                    "path": rel_path,
                    "content": content,
                    "truncated": truncated,
                    "content_available": True,
                }
            )

        ctx.session.state["documents"] = documents
        ctx.session.state["document_paths"] = [doc["path"] for doc in documents]
        manifest = []
        previews = []
        for doc in documents:
            path = doc.get("path", "")
            content = doc.get("content", "") or ""
            preview = content[: self.preview_chars]
            manifest.append(
                {
                    "path": path,
                    "content_available": doc.get("content_available", False),
                    "content_length": len(content),
                    "note": doc.get("note", ""),
                }
            )
            if preview:
                previews.append({"path": path, "preview": preview})
        ctx.session.state["documents_manifest"] = json.dumps(
            manifest, ensure_ascii=True
        )
        ctx.session.state["documents_preview"] = json.dumps(
            previews, ensure_ascii=True
        )
        if self.prefer_previews:
            ctx.session.state["documents_json"] = ctx.session.state[
                "documents_preview"
            ]
        else:
            ctx.session.state["documents_json"] = json.dumps(
                documents, ensure_ascii=True
            )

        yield Event(author=self.name)
