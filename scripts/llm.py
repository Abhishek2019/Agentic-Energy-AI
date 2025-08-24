import warnings
warnings.filterwarnings("ignore", category=UserWarning)


import os, re, glob, json
import ollama
from pypdf import PdfReader
import numpy as np
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# ---------- Config ----------
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi4-mini:latest")
EMBED_MODEL  = os.getenv("EMBED_MODEL",  "nomic-embed-text")


#!/usr/bin/env python3
import argparse, json, os, re
import pdfplumber
import ollama

SCHEMA = {
  "schema_version": "duke.v1",
  "source_file": "",
  "account": {"number": "", "service_address": ""},
  "bill": {"period_start": None, "period_end": None, "due_date": None, "amount_due_usd": None},
  "charges": [{"item": None, "qty": None, "unit": None, "rate_usd": None, "amount_usd": None}],
  "usage": [{"meter": None, "prev_read": None, "curr_read": None, "kwh": None, "days": None, "avg_kwh_per_day": None}],
  "notes": ""
}

SYS = (
  "You are a precise information extractor for utility bills. "
  "Return ONLY one JSON object matching the provided schema. "
  "Use bill content only; do not guess. Dates must be YYYY-MM-DD. "
  "Money must be numbers (e.g., 142.58). Missing fields → null/empty list. No extra keys or commentary."
)

PROMPT_TMPL = """Extract fields from this Duke Energy bill and return ONLY JSON.

SCHEMA (example, not data):
{schema}

TEXT:
{body}
"""

def read_pdf_text(pdf_path):
    pages_txt = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, p in enumerate(pdf.pages, 1):
            t = p.extract_text() or ""
            t = re.sub(r"[ \t]+", " ", t).strip()
            pages_txt.append(f"--- PAGE {i} ---\n{t}")
    return "\n\n".join(pages_txt)

def call_ollama(model, system_msg, user_msg):
    resp = ollama.chat(
        model=model,
        messages=[{"role":"system","content":system_msg},{"role":"user","content":user_msg}],
        options={"temperature":0},
        format="json"  # force JSON-only output
    )
    return resp["message"]["content"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="Path to bill PDF")
    ap.add_argument("--model", default="phi4:mini", help="Ollama model tag (default: phi4:mini)")
    ap.add_argument("--out", help="Output JSON path (default: <pdf>.json)")
    args = ap.parse_args()

    body = read_pdf_text(args.pdf)
    schema = dict(SCHEMA); schema["source_file"] = os.path.basename(args.pdf)
    user = PROMPT_TMPL.format(schema=json.dumps(schema, indent=2), body=body)

    content = call_ollama(args.model, SYS, user)

    # parse or lightly repair
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        s = content.strip()
        first, last = s.find("{"), s.rfind("}")
        if first != -1 and last > first:
            data = json.loads(s[first:last+1])
        else:
            raise

    out_path = args.out or (args.pdf + ".json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Wrote {out_path}")

if __name__ == "__main__":
    main()
