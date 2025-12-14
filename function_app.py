import azure.functions as func
import logging
import json
import nest_asyncio
from backend.rag import youtuber_agent

nest_asyncio.apply()

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="chat")
async def chat(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing chat request.")

    try:
        req_body = req.get_json()
        user_prompt = req_body.get("prompt")

        if not user_prompt:
            return func.HttpResponse(
                json.dumps({"error": "No prompt provided"}),
                status_code=400,
                mimetype="application/json",
            )

        result = await youtuber_agent.run(user_prompt)

        answer_text = result.output

        return func.HttpResponse(
            json.dumps({"response": answer_text}),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error(f"CRITICAL ERROR: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}), status_code=500, mimetype="application/json"
        )
