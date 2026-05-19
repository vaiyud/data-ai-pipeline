# import os
import sys
from ollama import Client, ChatResponse

def prompt_model(model: str, prompt: str) -> str :
	try:
		# os.getenv("GOOGLE_API_KEY")
		client = Client(host='http://127.0.0.1:11434')
		# print(f"🛜 Sending request to {model} on port 11434...")
		
		response: ChatResponse = client.chat(
			model=model, 
			messages=[
				{
					'role': 'user',
					'content': prompt,
				},
			]
		)

		# print("\n--- RESPONSE ---\n")
		# print(response.message.content)

		return response.message.content
	except Exception as e:
		print("\n--- RESPONSE ---\n")
		print("❌ Error: ", e)


if __name__ == "__main__":

	model_list = ["deepseek-r1:1.5b", "phi3", "llama3.1"]

	if len(sys.argv) < 3:
		print("❌ Error: Missing arguments")
		print(f"🛠️ Usage: uv run prompt_model.py [{' | '.join(model_list)}] <prompt>")
		sys.exit(1)
	
	chosen_model = sys.argv[1]
	user_prompt = sys.argv[2]

	prompt_model(chosen_model, user_prompt)