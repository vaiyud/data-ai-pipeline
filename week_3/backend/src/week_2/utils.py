import os
from pathlib import Path
from week_2.prompt_model import prompt_model

MODEL_NAME = os.getenv("DEFAULT_MODEL")


def calculate_model_configs(model_name: str) -> tuple[int, int]:

    default_max_retries = 3
    default_retry_duration = 2

    rate_limit_path = Path("rate_limits.txt")

    if not rate_limit_path.exists():
        return default_max_retries, default_retry_duration

    with open(rate_limit_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("<MODEL_NAME") or not line.strip():
                continue

            parts = line.split()
            if parts and parts[0] == model_name:
                try:
                    rpm = int(parts[1])
                    # 60s/5rpm = 12s intervals; 60s/10rpm = 6s intervals
                    calculated_duration = max(1, 60 // rpm)
                    max_retries = min(5, rpm)
                    return max_retries, calculated_duration
                except ValueError, IndexError:
                    break

    return default_max_retries, default_retry_duration


def get_file_summary(resume_text: str, prompt: str):
    model_instructions = f"""
        You are an expert technical recruiter analyzing a candidate's background.
        Execute the following user request: '{prompt}'

        --- ATTACHED RESUME TEXT CONTENT ---
        {resume_text}
        ----------------------------------
        CRITICAL FORMATTING INSTRUCTIONS:
        1. Provide your response as a single, natural, fluid paragraph. 
        2. Talk directly to the recruiter or user about the candidate in the third person (e.g., "The candidate is...").
        3. DO NOT use any markdown formatting, headers (##), bold text (**), dividers (---), or bullet points (*). 
        4. Write it entirely as clean, unformatted plain text.
    """
    return prompt_model(MODEL_NAME, model_instructions)
