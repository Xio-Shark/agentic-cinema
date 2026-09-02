"""
Main Entrypoint for CineOps Studio.
Launches the FastAPI server and serves the Web Console.
"""

import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print("\n" + "=" * 65)
    print("  🎬 CineOps Studio: The Agentic Cinema Platform")
    print(f"  🌐 Web Console: http://localhost:{port}")
    print(f"  📡 API Docs:    http://localhost:{port}/docs")
    print("=" * 65 + "\n")
    uvicorn.run("services.api_server:app", host=host, port=port, reload=False)
