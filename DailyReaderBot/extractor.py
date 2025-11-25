from pathlib import Path
import json
import pdfplumber

# epub용 라이브러리
from ebooklib import epub
from bs4 import BeautifulSoup

RAW = Path("original_books")
OUT = Path("extracted")
OUT.mkdir(exist_ok=True)


def extract_pdf(pdf_path):
    book = pdf_path.stem
    out_file = OUT / f"{book}.json"
    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append({
                "page": i,
                "text": text.strip()
            })

    save_json(out_file, pages)
    print(f"✅ PDF 완료: {book} ({len(pages)} pages)")


def extract_txt(txt_path):
    book = txt_path.stem
    out_file = OUT / f"{book}.json"

    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        # UTF-8 실패 시 latin-1로 폴백
        with open(txt_path, "r", encoding="latin-1") as f:
            content = f.read()

    pages = [{
        "page": 1,
        "text": content.strip()
    }]

    save_json(out_file, pages)
    print(f"✅ TXT 완료: {book} (1 page)")


def extract_epub(epub_path):
    book = epub_path.stem
    out_file = OUT / f"{book}.json"
    pages = []

    book_data = epub.read_epub(epub_path)

    i = 1
    for item in book_data.get_items():
        if item.get_type() == 9:  # ebooklib.ITEM_DOCUMENT
            html = item.get_content()
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="\n").strip()

            if text:
                pages.append({
                    "page": i,
                    "text": text
                })
                i += 1

    save_json(out_file, pages)
    print(f"✅ EPUB 완료: {book} ({len(pages)} sections)")


def save_json(out_file, pages):
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    for file in RAW.iterdir():
        suffix = file.suffix.lower()

        if suffix == ".pdf":
            extract_pdf(file)

        elif suffix == ".txt":
            extract_txt(file)

        elif suffix == ".epub":
            extract_epub(file)

        else:
            print(f"⚠️ 지원하지 않는 형식: {file.name}")
