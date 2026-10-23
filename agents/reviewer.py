import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

async def run_reviewer_agent(script_data: str) -> str:
    """
    Reviewer Agent: Checks the script for Gen-Z tone, cinematic flow, and impact.
    """
    logger.info("🧐 Reviewer Agent activated to analyze the script.")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from .env file!")
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.8-flash')
    
    prompt = f"""
    You are a brutal but brilliant Creative Director. 
    Review this cinematic script and provide a final polished version.
    Fix any cringe dialogue, ensure the transitions are smooth, and maximize the emotional hook.
    
    Original Draft:
    {script_data}
    
    Return ONLY the final polished script, ready for production. Do not add any conversational filler.
    """
    
    logger.info("🧐 Gemini (Reviewer) is polishing the final cut...")
    response = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": 8192}
    )
    
    return response.text