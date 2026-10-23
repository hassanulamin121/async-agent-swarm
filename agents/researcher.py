import os
import httpx
import logging
import google.generativeai as genai

# Professional logging setup
logger = logging.getLogger(__name__)

async def run_research_agent(topic: str) -> str:
    """
    Research Agent: Fetches real-time external data (Free API) 
    and uses Gemini to analyze and summarize it for the script.
    """
    logger.info(f"🔍 Research Agent activated for topic: '{topic}'")
    
    # 1. Fetching External Data (The Free API Magic)
    external_data = "No external data fetched."
    try:
        # Asynchronous API call to a free public Poetry API for that cinematic touch!
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://poetrydb.org/random/1/author,title,lines")
            if response.status_code == 200:
                poetry_data = response.json()
                lines = " ".join(poetry_data[0].get("lines", [])[:2])
                external_data = f"Poetry Reference: '{lines}' by {poetry_data[0].get('author')}"
                logger.info("Successfully fetched data from Public API.")
    except Exception as e:
        logger.warning(f"External API call failed, continuing with Gemini only: {str(e)}")

    # 2. Activating The Brain (Gemini API)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from .env file!")
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.8-flash')
    
    # 3. Prompt Engineering for the Agent
    prompt = f"""
    You are an expert Research Agent working on a multi-agent system.
    Your task is to analyze the following Gen-Z or modern topic and provide a crisp, 3-bullet point research summary.
    
    Topic: {topic}
    External Poetry Context to weave into the theme: {external_data}
    
    Keep it professional, highly insightful, and ready for a scriptwriter to use.
    """
    
    # Generate the response
    logger.info("🧠 Gemini is analyzing the research data...")
    response = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": 500}
    )
    
    return response.text