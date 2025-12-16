from pydantic_ai import Agent
from backend.data_models import BotResponse
from backend.constants import VECTOR_DATABASE_PATH
import lancedb

vector_db = lancedb.connect(uri=VECTOR_DATABASE_PATH)

youtuber_agent = Agent(
    model="google-gla:gemini-2.5-flash",
    retries=2,
    system_prompt=(
        "You are a Data Engineering Youtuber teaching in your videos."
        "You like Pokemon, you are always happy when you succeed in your coding, and you have a nerdy humour."
        "Your answer ALWAYS has to be based on the retrieved knowledge. If you think it's not enough, you can add 1-2 sentences of your own knowledge, because you don't like to leave your audience without any answer."
        "Your answer has to be rather short and clear to fulfill the user's prompt."
        "ALWAYS explicitly mention the video title and the filename you used to answer the question."
        "If you cannot find the answer in the context and the user prompt is outside the retrieved knowledge, say 'I don't know'.",
    ),
    output_type=BotResponse,
)


@youtuber_agent.tool_plain
def retrieve_top_documents(query: str, k=3) -> str:
    """
    Uses vector search to find the closest k matchin documents to the query
    """
    results = vector_db["transcripts"].search(query=query).limit(k).to_list()
    best_result = results[0]

    return f"""
    Filename: {best_result['filename']},
    Filepath: {best_result["filepath"]},
    Title: {best_result['title']},
    Content: {best_result['content']},
    """
