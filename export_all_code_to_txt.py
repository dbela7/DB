import hashlib
import json
import os
from datetime import datetime
from pathlib import Path


# --- Beállítások ---
PROJECT_ROOT = Path(__file__).resolve().parent  # ahova ezt a scriptet mented (pl. C:\DB\R)
OUTPUT_TXT = PROJECT_ROOT / "ALL_CODE.txt"
OUTPUT_MANIFEST = PROJECT_ROOT / "ALL_CODE_MANIFEST.json"

# Mit gyűjtsünk össze?
INCLUDE_EXTS = {".py", ".ini"}  # alap: python + config.ini
OPTIONAL_EXTS = {".txt", ".md"}  # ha szeretnéd, ezeket is hozzáadja

# Mely mappákat hagyjuk ki?
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".idea",
    ".vscode",
}

# Mely fájlokat hagyjuk ki?
EXCLUDE_FILES = {
    OUTPUT_TXT.name,
    OUTPUT_MANIFEST.name,
}


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def safe_read_text(p: Path) -> tuple[str, str]:
    """
    Returns (text, encoding_used). Never throws UnicodeDecodeError.
    """
    raw = p.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "cp1250", "latin-1"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            pass
    # fallback (should not happen because latin-1 decodes everything)
    return raw.decode("latin-1", errors="replace"), "latin-1"


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue

        rel_parts = p.relative_to(root).parts
        if rel_parts and rel_parts[0] in EXCLUDE_DIRS:
            continue

        if p.name in EXCLUDE_FILES:
            continue

        ext = p.suffix.lower()
        if ext in INCLUDE_EXTS or ext in OPTIONAL_EXTS:
            files.append(p)

    # stabil sorrend
    files.sort(key=lambda x: str(x.relative_to(root)).lower())
    return files


def main() -> None:
    root = PROJECT_ROOT
    if not root.exists():
        raise SystemExit(f"Project root nem létezik: {root}")

    files = iter_files(root)
    if not files:
        raise SystemExit("Nem találtam exportálható fájlt (.py/.ini/.txt/.md).")

    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(root),
        "file_count": len(files),
        "files": [],
    }

    out_lines: list[str] = []
    out_lines.append("ALL_CODE export")
    out_lines.append(f"Generated at: {manifest['generated_at']}")
    out_lines.append(f"Project root: {manifest['project_root']}")
    out_lines.append(f"File count: {manifest['file_count']}")
    out_lines.append("=" * 80)
    out_lines.append("")

    for p in files:
        rel = p.relative_to(root)
        raw = p.read_bytes()
        text, enc = safe_read_text(p)
        file_info = {
            "path": str(rel).replace("\\", "/"),
            "size_bytes": len(raw),
            "sha256": sha256_bytes(raw),
            "encoding_read": enc,
        }
        manifest["files"].append(file_info)

        out_lines.append("#" * 80)
        out_lines.append(f"# FILE: {file_info['path']}")
        out_lines.append(f"# SIZE: {file_info['size_bytes']} bytes")
        out_lines.append(f"# SHA256: {file_info['sha256']}")
        out_lines.append(f"# ENCODING_READ: {file_info['encoding_read']}")
        out_lines.append("#" * 80)
        out_lines.append("")
        out_lines.append(text.rstrip("\n"))
        out_lines.append("")
        out_lines.append("")

    export_text = "\n".join(out_lines).replace("\r\n", "\n")

    OUTPUT_TXT.write_text(export_text, encoding="utf-8")
    OUTPUT_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Kész export.")
    print("TXT :", OUTPUT_TXT)
    print("JSON:", OUTPUT_MANIFEST)
    print("\nTipp: ha hibát jelentesz, elég az ALL_CODE_MANIFEST.json + az ALL_CODE.txt releváns része.")


if __name__ == "__main__":
    main()