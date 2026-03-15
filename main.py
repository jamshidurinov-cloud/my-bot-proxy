from fastapi import FastAPI, Request, Response
import httpx
import os

app = FastAPI( )

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GAS_WEB_APP_URL = os.getenv("GAS_WEB_APP_URL")

@app.post(f"/webhook/{{token}}")
async def telegram_webhook(token: str, request: Request):
    if token != TELEGRAM_BOT_TOKEN:
        return Response(content="Unauthorized", status_code=401)

    response = Response(content="OK", status_code=200)
    update_data = await request.json()

    # 🔹 BU YERDA follow_redirects=True QO'ShILDI
    async with httpx.AsyncClient(follow_redirects=True ) as client:
        try:
            gas_response = await client.post(GAS_WEB_APP_URL, json=update_data, timeout=30.0)
            gas_response.raise_for_status()
            print(f"Forwarded to GAS. Status: {gas_response.status_code}")
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting GAS: {exc}" )
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting GAS" )

    return response

@app.get("/")
async def root():
    return {"message": "Telegram Webhook Proxy is running!"}

