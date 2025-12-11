from pydantic import BaseModel, Field
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from dotenv import load_dotenv


load_dotenv()

embedding_model = (
    get_registry().get("sentence-transformers").create(name="BAAI/bge-small-en-v1.5")
)

EMBEDDING_DIM = 384


class Transcript(LanceModel):
    title: str
    text: str = embedding_model.SourceField()
    vector: Vector(EMBEDDING_DIM) = embedding_model.VectorField()
