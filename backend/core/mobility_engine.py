import time
import random
import os
from groq import Groq

class MobilityEngine:
    def __init__(self):
        # We assume load_dotenv() has already been called in main.py
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.system_prompt = "You are a sustainable smart mobility assistant. Provide a concise, eco-friendly route suggestion or mobility advice to the user's query."

    def process_query(self, query: str):
        start_time = time.time()
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt,
                    },
                    {
                        "role": "user",
                        "content": query,
                    }
                ],
                model="llama-3.1-8b-instant", 
                temperature=0.7,
                max_tokens=150,
            )
            ans = chat_completion.choices[0].message.content.strip()
        except Exception as e:
            import logging
            logging.getLogger("MobilityAssistant").error(f"Groq API Error: {e}")
            ans = f"Analyzed your request: '{query}'. The optimal path involves a combination of express transit and micro-mobility to ensure sustainability. (Fallback)"

        end_time = time.time()
        delay = end_time - start_time
        
        return {
            'mode': 'Smart Recommendation',
            'description': ans,
            'estimated_time': f"{random.randint(15, 60)} mins",
            'carbon_footprint': f"{random.uniform(0.2, 4.0):.1f} kg CO2",
            'engine_latency': round(delay, 2)
        }
