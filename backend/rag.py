# import os
from pydantic_ai import Agent, RunContext
import lancedb
from constants import VECTOR_DATABASE_PATH

# from pydantic_ai.models.gemini import GoogleModel
from dotenv import load_dotenv

load_dotenv()

youtuber_agent = Agent(
    model="google-gla:gemini-2.5-flash",
    system_prompt="The Youtuber is knowledgeable in the data engineering field with a nerdy humour. He is making Tutorial videos. Your target audience is students trying to learn Data Engineering. Try to make your answeres similar to The Youtuber's personality.",
)


@youtuber_agent.tool_plain
def retrieve_context(query: str) -> str:
    """
    Retrieve relevant context from the vector database based on the user's query.
    """
    vector_db = lancedb.connect(uri=VECTOR_DATABASE_PATH)
    table = vector_db.open_table("transcripts")
    results = table.search(query=query).limit(3).to_list()

    result_string = ""
    for item in results:
        result_string += f"Title: {item['title']}\nText: {item['text']}\n\n"

    return result_string


if __name__ == "__main__":
    response = youtuber_agent.run_sync("What is lancedb?")

    print(response.output)
