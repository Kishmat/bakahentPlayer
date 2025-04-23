from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from urllib.parse import urljoin

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/m3u8")
async def proxy_m3u8(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        content = r.text

        def rewrite_line(line):
            if line.strip().startswith("#") or not line.strip():
                return line
            full_url = urljoin(url, line.strip())
            return f"/segment?url={full_url}"

        rewritten = "\n".join(rewrite_line(line) for line in content.splitlines())
        return PlainTextResponse(rewritten, media_type="application/vnd.apple.mpegurl")

@app.get("/segment")
async def proxy_segment(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return StreamingResponse(r.aiter_bytes(), media_type="video/MP2T")