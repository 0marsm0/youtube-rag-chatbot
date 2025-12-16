import re
import lancedb
import time
from pathlib import Path
from backend.constants import VECTOR_DATABASE_PATH, DATA_PATH
from backend.data_models import Transcript


def setup_vector_db(path: Path):
    """Connect to LanceDB and create table if not exists"""
    vector_db = lancedb.connect(uri=path)
    vector_db.create_table("transcripts", schema=Transcript, exist_ok=True)
    return vector_db


def clean_data(text: str):
    """Clean and parse markdown transcript text"""
    parts = text.lstrip().split("\n", 1)

    if len(parts) != 2:
        return None

    title = parts[0].lstrip("#").strip()
    content = parts[1]

    clean_text = re.sub(r"\[\d{2}:\d{2}:\d{2}\]", "", content)
    clean_text = re.sub(r"~~.*?~~", "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    if not clean_text:
        return None

    return title, clean_text


def ingest_docs_to_vector_db(table):
    """Ingest markdown files into vector database"""
    files = list(DATA_PATH.glob("*.md"))
    print(f"Found {len(files)} files in {DATA_PATH}")

    processed_count = 0
    skipped_count = 0

    for file in files:
        if re.search(r"\(\d+\)\.md$", file.name):
            skipped_count += 1
            print(f"Skipping duplicate: {file.name}")
            continue

        try:
            raw_text = file.read_text(encoding="utf-8")
            parsed = clean_data(raw_text)

            if parsed is None:
                print(f"Failed to parse {file.name}: No valid title/content")
                skipped_count += 1
                continue

            title, clean_text = parsed
            doc_id = file.stem

            try:
                table.delete(f"id = '{doc_id}'")
            except Exception:
                pass

            table.add(
                [
                    {
                        "doc_id": doc_id,
                        "filepath": str(file),
                        "filename": file.stem,
                        "title": title,
                        "content": clean_text,
                    }
                ]
            )

            processed_count += 1
            print(f"✓ Processed: {file.stem} - {title[:50]}...")

            current_files = table.to_pandas()["filename"].tolist()
            print(f"  Current table has {len(current_files)} documents")
            time.sleep(10)

        except Exception as e:
            print(f"✗ Failed to process {file.name}: {e}")
            skipped_count += 1
            continue

    print(f"Ingestion Complete!")
    print(f"Successfully processed: {processed_count} documents")
    print(f"Skipped/Failed: {skipped_count} documents")


if __name__ == "__main__":
    db = setup_vector_db(VECTOR_DATABASE_PATH)
    ingest_docs_to_vector_db(db["transcripts"])
