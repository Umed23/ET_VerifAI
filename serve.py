import uvicorn
from fastapi import FastAPI
from langserve import add_routes

from main import app as agent_graph

app = FastAPI(
    title="VerifAI Enterprise API",
    version="1.0",
    description="The flagship 7-agent orchestrator for workflow automation.",
)

# Adds REST routes to the app, extending the compiled LangGraph logic natively
add_routes(
    app,
    agent_graph,
    path="/verifai",
)

if __name__ == "__main__":
    print("🚀 VerifAI Production Server Starting on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
