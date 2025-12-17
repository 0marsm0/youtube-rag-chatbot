from fastapi import FastAPI, HTTPException
from backend.rag import youtuber_agent
from backend.data_models import UserPrompt

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
        raise HTTPException(status_code=500, detail=str(e))
