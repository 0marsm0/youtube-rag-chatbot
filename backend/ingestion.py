from backend.constants import VECTOR_DATABASE_PATH, DATA_PATH
import re

# from pathlib import Path
import lancedb
from backend.data_models import Transcript
import pandas as pd


def setup_vector_db(path):
    vector_db = lancedb.connect(uri=path)

    table = vector_db.create_table("transcripts", schema=Transcript, mode="overwrite")
    print(f"Table has been successfully created")
    return table


def clean_data(text):

    parts = text.split("\n", 1)

    if len(parts) == 2:
        title = parts[0].lstrip("#").strip()
        content = parts[1]

        clean_text = re.sub(r"\[\d{2}:\d{2}:\d{2}\]", "", content)  # Timecode
        clean_text = re.sub(r"~~.*?~~", "", clean_text)  # Strikethrough
        clean_text = re.sub(r"\s+", " ", clean_text)  # Spacing
        clean_text = clean_text.strip()

        return {"title": title, "text": clean_text}

    return None


def deduplicate_files(path):
    file_paths = list(path.glob("*.md"))

    files = []

    for file in file_paths:
        if re.search(r" \(\d+\)\.md$", file.name):
            continue

        try:
            raw_text = file.read_text(encoding="utf-8")
            result = clean_data(raw_text)
        except Exception as e:
            print(f"File {file} has not been added due to error")
            continue

        if result is not None:
            files.append(result)
    print(f"{len(file_paths) - len(files)} files skipped due to duplicates and errors")
    return files


def ingest_docs_to_vector_db(files, table):
    df_transcripts = pd.DataFrame(files)
    table.add(df_transcripts)


if __name__ == "__main__":
    transcript_table = setup_vector_db(VECTOR_DATABASE_PATH)
    transcripts = deduplicate_files(DATA_PATH)

    ingest_docs_to_vector_db(transcripts, transcript_table)
