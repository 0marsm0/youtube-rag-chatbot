from fastapi import FastAPI
from backend.rag import youtuber_agent
from backend.data_models import UserPrompt, BotResponse

app = FastAPI()


@app.get("/test")
async def test():
    return {"Status": "API is Running!"}


@app.post("/chat")
async def get_response(query: UserPrompt):
    try:
        result = await youtuber_agent.run(query.prompt)
        return result.output
    except Exception as e:
        return BotResponse(response=f"Error: {str(e)}")
