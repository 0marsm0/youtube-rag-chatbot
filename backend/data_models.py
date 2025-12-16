from pydantic import BaseModel, Field
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from dotenv import load_dotenv

load_dotenv()

embedding_model = get_registry().get("gemini-text").create(name="gemini-embedding-001")

EMBEDDING_DIM = 3072


class Transcript(LanceModel):
    doc_id: str
    filepath: str
    filename: str = Field(description="the stem of the file i.e. without the suffix")
    title: str
    content: str = embedding_model.SourceField()
    embedding: Vector(EMBEDDING_DIM) = embedding_model.VectorField()


class UserPrompt(BaseModel):
    prompt: str = Field(description="prompt from user, if empty consider it as missing")


class BotResponse(BaseModel):
    filename: str = Field(description="filename of retrieved file without suffix")
    filepath: str = Field(description="absolute path to the retrieved file")
    response: str = Field(description="answer based on the transcript from the video")
