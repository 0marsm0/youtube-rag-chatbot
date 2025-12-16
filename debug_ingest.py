import lancedb
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from pydantic import Field

# 1. Настройка окружения
load_dotenv()
print(f"📍 Current Working Directory: {os.getcwd()}")

# 2. Определяем пути (ЖЕСТКО, чтобы не ошибиться)
# Предлагаем, что data лежит в корне проекта
ROOT_DIR = Path(os.getcwd())
DATA_PATH = ROOT_DIR / "data" / "raw"
DB_PATH = ROOT_DIR / "data" / "lancedb"

print(f"📂 Looking for Markdown files in: {DATA_PATH}")
print(f"💾 Database will be saved to:    {DB_PATH}")

# 3. Модель данных (Как у тебя)
embedding_model = (
    get_registry().get("sentence-transformers").create(name="BAAI/bge-small-en-v1.5")
)


class Transcript(LanceModel):
    id: str
    filename: str
    title: str
    text: str = embedding_model.SourceField()
    vector: Vector(384) = embedding_model.VectorField()


# 4. Функция очистки
def clean_data(text: str):
    parts = text.lstrip().split("\n", 1)
    if len(parts) < 2:
        return None, "Too short/No newline"

    title = parts[0].lstrip("#").strip()
    content = parts[1]

    clean_text = re.sub(r"\[\d{2}:\d{2}:\d{2}\]", "", content)
    clean_text = re.sub(r"~~.*?~~", "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    if not clean_text:
        return None, "Empty content after clean"

    return (title, clean_text), "OK"


# 5. Главная логика
def run_ingestion():
    if not DATA_PATH.exists():
        print(f"❌ ERROR: Raw data folder does not exist: {DATA_PATH}")
        return

    # Подключаемся
    db = lancedb.connect(uri=DB_PATH)

    files = list(DATA_PATH.glob("*.md"))
    print(f"🔎 Found {len(files)} .md files.")

    docs = []

    for file in files:
        # Проверка на дубликаты
        if re.search(r"\(\d+\)\.md$", file.name):
            print(f"SKIP (Duplicate): {file.name}")
            continue

        try:
            raw_text = file.read_text(encoding="utf-8")
            parsed, status = clean_data(raw_text)

            if parsed is None:
                print(f"SKIP ({status}): {file.name}")
                continue

            title, clean_text = parsed
            print(f"✅ OK: {file.name} (Title: {title[:30]}...)")

            docs.append(
                {
                    "id": file.stem,
                    "filename": file.stem,
                    "title": title,
                    "text": clean_text,
                }
            )

        except Exception as e:
            print(f"❌ ERROR reading {file.name}: {e}")

    # Запись
    if docs:
        print(f"🚀 Inserting {len(docs)} records into DB...")
        try:
            db.create_table(
                "transcripts", data=docs, schema=Transcript, mode="overwrite"
            )
            print("🎉 SUCCESS! Data inserted.")

            # Проверка сразу же
            tbl = db.open_table("transcripts")
            print(f"👀 Verification: Table now has {tbl.count_rows()} rows.")
        except Exception as e:
            print(f"❌ ERROR during insertion: {e}")
    else:
        print("⚠️  WARNING: No documents collected. Database remains empty.")


if __name__ == "__main__":
    run_ingestion()
