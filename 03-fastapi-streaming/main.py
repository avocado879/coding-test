import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI(title="Streaming API Demo")

async def events(prompt: str):
    for index, token in enumerate((f"You said: {prompt}. ", "This is ", "a streaming ", "FastAPI response.")):
        await asyncio.sleep(0.15)
        yield f"data: {{\"index\": {index}, \"token\": {token!r}}}\n\n"
    yield "data: [DONE]\n\n"

@app.get("/stream")
async def stream(prompt: str = "hello World"):
    return StreamingResponse(events(prompt), media_type="text/event-stream")

@app.get("/health")
async def health(): return {"status": "ok"}
