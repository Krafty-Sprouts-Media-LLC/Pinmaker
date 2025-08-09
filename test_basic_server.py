#!/usr/bin/env python3
"""
Minimal server test to check basic dependencies
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create minimal app
app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async def test():
    return {"status": "ok", "message": "Basic server working"}

if __name__ == "__main__":
    print("Starting minimal test server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
