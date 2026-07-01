#!/usr/bin/env python3
"""
main.py - FastAPI Web Service for AI Web Automation Agent (Round 2)

This exposes the browser automation capabilities as a simple HTTP API.
Useful for:
- Calling from other applications/scripts
- Scheduled tasks / cron
- Future frontend or dashboard

Run with:
  uvicorn main:app --reload

After Round 3 this will be containerized and deployable.
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import os

from browser_agent import run_agent

app = FastAPI(
    title="AI Web Automation Agent API",
    description="Trigger browser automation tasks via HTTP",
    version="0.2.0-round2"
)


class RunRequest(BaseModel):
    url: str = Field(..., description="Target URL (must include https://)")
    headless: bool = Field(True, description="Run browser in headless mode")
    take_screenshot: bool = Field(True, description="Capture full page screenshot")
    extract_text: bool = Field(True, description="Extract page title, heading and body snippet")
    screenshot_path: Optional[str] = Field(None, description="Custom path for screenshot (optional)")


class RunResponse(BaseModel):
    success: bool
    url: str
    title: Optional[str] = None
    heading: Optional[str] = None
    body_snippet: Optional[str] = None
    screenshot_path: Optional[str] = None
    error: Optional[str] = None


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "message": "AI Web Automation Agent API is running (Round 2)",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}


@app.post("/run", response_model=RunResponse, tags=["Automation"])
async def run_automation(request: RunRequest):
    """
    Trigger a browser automation run.

    This is synchronous for simplicity in Round 2.
    In production (Round 3+), long tasks should use BackgroundTasks or a task queue.
    """
    try:
        result = run_agent(
            url=request.url,
            take_screenshot=request.take_screenshot,
            extract_text=request.extract_text,
            headless=request.headless,
            screenshot_path=request.screenshot_path,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
