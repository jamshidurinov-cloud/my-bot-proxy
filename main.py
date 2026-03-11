
from fastapi import FastAPI, Request, Response
import httpx
import os

app = FastAPI()

# Environment variables for your Telegram Bot Token and Google Apps Script Web App URL
# You will need to set these in your deployment environment (e.g., Render.com, PythonAnywhere)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
GAS_WEB_APP_URL = os.getenv("GAS_WEB_APP_URL", "YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL")

@app.post(f"/webhook/{{token}}")
async def telegram_webhook(token: str, request: Request):
    # Verify the token to ensure the request is from your bot
    if token != TELEGRAM_BOT_TOKEN:
        return Response(content="Unauthorized", status_code=401)

    # Immediately acknowledge the request to Telegram to prevent retries/loops
    # This is crucial for preventing the looping issue you experienced.
    response = Response(content="OK", status_code=200)

    # Get the incoming Telegram update data
    update_data = await request.json()

    # Forward the update to your Google Apps Script Web App
    async with httpx.AsyncClient() as client:
        try:
            # It's important to send the data as application/json
            # Google Apps Script's doPost(e) expects JSON in e.postData.contents
            gas_response = await client.post(GAS_WEB_APP_URL, json=update_data, timeout=30.0)
            gas_response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            print(f"Forwarded to GAS. Status: {gas_response.status_code}, Response: {gas_response.text}")
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting GAS: {exc}")
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting GAS: {exc.response.text}")

    return response

@app.get("/")
async def root():
    return {"message": "Telegram Webhook Proxy is running!"}

# To set up the webhook for your bot, you would typically make a request like this:
# https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/setWebhook?url=<YOUR_PROXY_SERVER_URL>/webhook/<YOUR_TELEGRAM_BOT_TOKEN>
# Replace <YOUR_TELEGRAM_BOT_TOKEN> with your actual bot token
# Replace <YOUR_PROXY_SERVER_URL> with the public URL of this FastAPI application
