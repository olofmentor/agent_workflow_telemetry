import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    base_dir: str
    model_name: str
    documents_dir: str
    max_file_chars: int
    preview_chars: int
    prefer_previews: bool


def load_config() -> AppConfig:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_name = os.environ.get("MODEL", "gemini-2.0-flash")
    documents_dir = os.environ.get("DOCUMENTS_DIR", "./input_files")
    if not os.path.isabs(documents_dir):
        documents_dir = os.path.join(base_dir, documents_dir)

    max_file_chars = int(os.environ.get("MAX_FILE_CHARS", "12000"))
    preview_chars = int(os.environ.get("PREVIEW_CHARS", "500"))
    prefer_previews = model_name.startswith("openai/")

    return AppConfig(
        base_dir=base_dir,
        model_name=model_name,
        documents_dir=documents_dir,
        max_file_chars=max_file_chars,
        preview_chars=preview_chars,
        prefer_previews=prefer_previews,
    )
