
# import asyncio
# import logging
# import os
# from dotenv import load_dotenv
# from AGENT.websocket_manager import subscribe
# from AGENT.twitter_manager import TwitterManager
# import openai

# # Загрузка переменных из .env
# load_dotenv()

# # Устанавливаем API-ключ OpenAI
# openai.api_key = os.getenv("OPENAI_API_KEY")

# class PumpAgent:
#     def __init__(self, websocket_uri):
#         self.websocket_manager = subscribe(uri=websocket_uri)
#         self.twitter_manager = TwitterManager(
#             bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
#             consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
#             consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
#             access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
#             access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
#         )

#     async def analyze_data(self, tokens):
#         prompt = f"Analyze the following token data and provide investment recommendations:\n{tokens}"
#         try:
#             response = openai.ChatCompletion.create(
#                 model="gpt-4",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=300,
#                 temperature=0.7,
#             )
#             return response['choices'][0]['message']['content']
#         except Exception as e:
#             logging.error(f"Error analyzing data with OpenAI: {e}")
#             return "Error generating analysis."

#     async def run(self):
#         await self.websocket_manager.connect()
#         await self.websocket_manager.subscribe(method="subscribeNewToken")
        
#         tokens_data = []
#         async for data in self.websocket_manager.listen():
#             tokens_data.append(data)
#             if len(tokens_data) >= 15:  # Обрабатываем каждые 15 токенов
#                 analysis = await self.analyze_data(tokens_data)
#                 if analysis:  # Проверяем, что анализ не пустой
#                     await self.twitter_manager.post_tweet(analysis)
#                 tokens_data.clear()  # Очищаем список после анализа

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

#     websocket_uri = "wss://pumpportal.fun/api/data"
#     agent = PumpAgent(websocket_uri)
#     asyncio.run(agent.run())
