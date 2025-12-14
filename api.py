from fastapi import FastAPI
from pydantic import BaseModel
from rag import youtuber_agent

app = FastAPI(title="Youtube RAG Chatbot")


class UserPrompt(BaseModel):
    prompt: str


class BotResponse(BaseModel):
    response: str


@app.get("/")
async def test():
    return {"Status": "The API is Running Correctly!"}


@app.post("/chat")
async def get_response(query: UserPrompt):
    result = await youtuber_agent.run(query.prompt)

    return BotResponse(response=result.output)
