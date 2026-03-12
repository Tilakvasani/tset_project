"""
DocForge AI — docx_builder.py
Place this file at: D:\\turabit nlp\\tset_project\\docx_builder.py
(project root, same level as generate_docx.js)

Called directly from streamlit_app.py — no HTTP roundtrip to backend.
"""
import json
import subprocess
import tempfile
import os
from pathlib import Path


# Absolute path to generate_docx.js — same directory as this file
SCRIPT_DIR   = Path(__file__).parent.resolve()
DOCX_SCRIPT  = SCRIPT_DIR / "generate_docx.js"


def build_docx(
    doc_type: str,
    department: str,
    company_name: str,
    industry: str,
    region: str,
    sections: list[dict],          # [{"name": ..., "content": ...}]
) -> bytes:
    """
    Generate a .docx file from section data.
    Returns the raw bytes of the .docx file.
    Raises RuntimeError on failure.
    """
    if not DOCX_SCRIPT.exists():
        raise RuntimeError(
            f"generate_docx.js not found at {DOCX_SCRIPT}\n"
            "Make sure generate_docx.js is in the project root."
        )

    payload = {
        "doc_type":     doc_type,
        "department":   department,
        "company_name": company_name,
        "industry":     industry,
        "region":       region,
        "sections":     sections,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path  = os.path.join(tmpdir, "input.json")
        output_path = os.path.join(tmpdir, "output.docx")

        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)

        result = subprocess.run(
            ["node", str(DOCX_SCRIPT), input_path, output_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"DOCX generation failed (exit {result.returncode}):\n"
                f"{result.stderr or result.stdout}"
            )

        if not os.path.exists(output_path):
            raise RuntimeError("generate_docx.js ran but produced no output file.")

        with open(output_path, "rb") as f:
            return f.read()
