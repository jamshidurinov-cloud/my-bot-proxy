from fastapi import FastAPI, Request, Response
import httpx
import os
import uvicorn

app = FastAPI( )

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GAS_WEB_APP_URL = os.getenv("GAS_WEB_APP_URL")

@app.post(f"/webhook/{{token}}")
async def telegram_webhook(token: str, request: Request):
    if token != TELEGRAM_BOT_TOKEN:
        return Response(content="Unauthorized", status_code=401)

    response = Response(content="OK", status_code=200)
    update_data = await request.json()

    # follow_redirects=True qo'shildi (302 xatosini yo'qotish uchun)
    async with httpx.AsyncClient(follow_redirects=True ) as client:
        try:
            gas_response = await client.post(GAS_WEB_APP_URL, json=update_data, timeout=30.0)
            print(f"Forwarded to GAS. Status: {gas_response.status_code}")
        except Exception as exc:
            print(f"Error: {exc}")

    return response

@app.get("/")
async def root():
    return {"message": "Telegram Webhook Proxy is running!"}

# 🔹 Render uchun portni aniq ko'rsatish qismi qo'shildi
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
