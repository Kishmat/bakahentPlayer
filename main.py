from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from urllib.parse import urljoin, quote

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROXY_BASE = "https://accurate-marylee-kishmat-e1cb1721.koyeb.app"  # <-- Replace this before deploy

@app.get("/m3u8")
async def proxy_m3u8(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        content = r.text

        def rewrite_line(line):
            line = line.strip()
            if not line or line.startswith("#"):
                return line
            full_url = urljoin(url, line)
            if ".m3u8" in line:
                return f"{PROXY_BASE}/m3u8?url={quote(full_url)}"
            else:
                return f"{PROXY_BASE}/segment?url={quote(full_url)}"

        rewritten = "\n".join(rewrite_line(line) for line in content.splitlines())
        return PlainTextResponse(rewritten, media_type="application/vnd.apple.mpegurl")

@app.get("/segment")
async def proxy_segment(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return StreamingResponse(r.aiter_bytes(), media_type="video/MP2T")
