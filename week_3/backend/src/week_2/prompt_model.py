import os
import sys
from ollama import Client as OllamaClient, ChatResponse
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pathlib import Path


def prompt_model(model: str, prompt: str) -> str:

    parent_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=parent_env_path)

    try:
        #
        if model.lower().startswith("gemini"):
            if not os.getenv("GOOGLE_API_KEY"):
                return "❌ Error: GOOGLE_API_KEY environment variable is not set."

            google_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

            response = google_client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1),
            )
            return response.text.strip()
        else:
            ollama_client = OllamaClient(host=os.getenv("OLLAMA_HOST"))
            # print(f"🛜 Sending request to {model} on port 11434...")

            response: ChatResponse = ollama_client.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )
            return response.message.content

    except Exception as e:
        print("❌ Error: ", e)
        return ""


if __name__ == "__main__":
    model_list = [
        "gemma3:1b",
        "deepseek-r1:1.5b",
        "phi3",
        "llama3.1",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-3-flash-preview",
    ]

    if len(sys.argv) < 3:
        print("❌ Error: Missing arguments")
        print(f"🛠️ Usage: uv run prompt_model.py [{' | '.join(model_list)}] <prompt>")
        sys.exit(1)

    chosen_model = sys.argv[1]
    user_prompt = sys.argv[2]

    print("\n--- RESPONSE ---\n")
    print(prompt_model(chosen_model, user_prompt))
