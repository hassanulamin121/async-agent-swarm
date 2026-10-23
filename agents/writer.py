import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

async def run_writer_agent(topic: str, research_data: str) -> str:
    """
    Writer Agent: Takes the research data and writes a cinematic script.
    """
    logger.info(f"✍️ Writer Agent activated for topic: '{topic}'")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from .env file!")
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.8-flash')
    
    prompt = f"""
    You are an expert cinematic Scriptwriter creating content for a Gen-Z audience.
    Your task is to write a short, highly engaging video script about '{topic}'.
    
    You MUST weave the following research and poetry reference into the narrative naturally:
    {research_data}
    
    Format the output professionally:
    - [SCENE DESCRIPTION]: Visuals, lighting, camera angles.
    - [VOICEOVER / NARRATOR]: The dialogue or narration.
    - Keep the tone modern, slightly philosophical, and highly impactful.
    """
    
    logger.info("✍️ Gemini (Writer) is drafting the cinematic script...")
    response = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": 8192}
    )
    
    return response.text