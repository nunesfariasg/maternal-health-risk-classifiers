"""Empacota apenas fontes, dados públicos, resultados e documentação; nunca ambientes."""

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
NAME = "MatheusOliveira-MatheusBuratto-LuizOtavio-GabrielDias-GustavoNunes.zip"


def main():
    destination = ROOT / "dist"
    destination.mkdir(exist_ok=True)
    files = [
        ROOT / p
        for p in ["README.md", "requirements.txt", "pyproject.toml", ".gitignore", ".gitattributes"]
    ]
    for folder in ["src", "tests", "scripts", "data", "results", "report", "docs"]:
        files += [
            p
            for p in (ROOT / folder).rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
        ]
    with ZipFile(destination / NAME, "w", ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(ROOT))
    digest = hashlib.sha256((destination / NAME).read_bytes()).hexdigest()
    (destination / "SHA256SUMS.txt").write_text(f"{digest}  {NAME}\n", encoding="ascii")
    print(f"ZIP: {destination / NAME}\nSHA-256: {digest}")


if __name__ == "__main__":
    main()
