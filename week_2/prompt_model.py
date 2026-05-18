# import os
from ollama import Client, ChatResponse

def prompt_model(model: str, prompt: str) -> str :
	try:
		# os.getenv("GOOGLE_API_KEY")
		client = Client(host='http://127.0.0.1:11434')
		# print(f"Sending request to {model} on port 11434...")
		
		response: ChatResponse = client.chat(
			model=model, 
			messages=[
				{
					'role': 'user',
					'content': prompt,
				},
			]
		)

		print("\n--- RESPONSE ---\n")
		print(response.message.content)

		return response.message.content
	except Exception as e:
		print("\n--- RESPONSE ---\n")
		print(e)


if __name__ == "__main__":
    # prompt_model("deepseek-r1:1.5b", "tell me one malaysian joke")
	# prompt_model("phi3", "tell me one malaysian joke")
	# prompt_model("llama3.1", "tell me one malaysian joke")
	prompt_model("gemini-2.5-flash", "tell me one malaysian joke")