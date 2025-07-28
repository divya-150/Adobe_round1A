import sys
from pathlib import Path
from io_utils import INPUT_DIR, OUTPUT_DIR, ensure_dirs, write_json
from heading_detection import detect_outline

def main():
    ensure_dirs()
    pdfs = sorted(INPUT_DIR.glob("*.pdf"))
    if not pdfs:
        print("No PDFs found in /app/input")
        return

    for pdf in pdfs:
        out = detect_outline(pdf)
        out_name = pdf.stem + ".json"
        out_path = OUTPUT_DIR / out_name
        write_json(out, out_path)
        print(f"Wrote {out_path}")

if __name__ == "__main__":
    sys.exit(main())
