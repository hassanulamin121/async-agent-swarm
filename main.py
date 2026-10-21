import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 1. Yahan humne apne teeno agents import kar liye! ✨
from agents.researcher import run_research_agent
from agents.writer import run_writer_agent
from agents.reviewer import run_reviewer_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="Async Multi-Agent Swarm API",
    description="A scalable, asynchronous microservice orchestrating AI agents.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="The core subject for the AI agent swarm to research and script.",
        examples=["The Microwave Mindset and Gen-Z Digital Solitude"],
    )

class ScriptResponse(BaseModel):
    status: str
    topic_received: str
    script_data: str

@app.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
async def health_check() -> dict:
    return {"status": "healthy", "service": "async-agent-swarm-backend"}

@app.post(
    "/api/v1/generate-script",
    response_model=ScriptResponse,
    status_code=status.HTTP_200_OK,
    tags=["Agent Swarm"],
)
async def generate_script(request: TopicRequest) -> ScriptResponse:
    try:
        clean_topic = request.topic.strip()
        if not clean_topic:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topic cannot be empty or contain only whitespaces.",
            )

        logger.info(f"🚀 Initializing Swarm Pipeline for topic: '{clean_topic}'")

        # 2. Asynchronous Agent Swarm Magic (The Chain!) 🔗
        # Step A: Researcher gathers data
        research_result = await run_research_agent(clean_topic)
        
        # Step B: Writer drafts the script using the research
        writer_result = await run_writer_agent(clean_topic, research_result)
        
        # Step C: Reviewer polishes the script to production quality
        final_script = await run_reviewer_agent(writer_result)

        logger.info("✅ Swarm execution completed successfully!")

        return ScriptResponse(
            status="success",
            topic_received=clean_topic,
            script_data=final_script,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during script generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while processing your request.",
        )