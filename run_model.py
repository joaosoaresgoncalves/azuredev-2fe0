from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

endpoint = "https://SOARJOA-2669-resource.openai.azure.com/openai/v1/"
deployment_name = "Mistral-Large-3"
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

completion = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
    temperature=0.7,
)

print(completion.choices[0].message)