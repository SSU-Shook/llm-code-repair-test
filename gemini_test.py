import google.generativeai as genai
from env import settings
import os

genai.configure(api_key=settings.LLM_API_KEY['gemini'])

model = genai.GenerativeModel('gemini-pro')
response = model.generate_content('What is the color of an apple?')

print(response.text)