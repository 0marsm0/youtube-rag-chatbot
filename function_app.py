import azure.functions as func
import logging
import json
from backend.rag import youtuber_agent

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="chat")
async def chat(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing chat request.")

    try:
        # 1. Getting question
        req_body = req.get_json()
        user_prompt = req_body.get("prompt")

        if not user_prompt:
            return func.HttpResponse(
                json.dumps({"error": "No prompt provided"}),
                status_code=400,
                mimetype="application/json",
            )

        # 2. Start our Agent
        result = await youtuber_agent.run(user_prompt)

        # 3. Getting response
        return func.HttpResponse(
            json.dumps({"response": result.data}),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}), status_code=500, mimetype="application/json"
        )
