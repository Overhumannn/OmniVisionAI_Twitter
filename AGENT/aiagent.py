import asyncio
import json
import logging
import websockets
import openai
import os
from dotenv import load_dotenv
import tweepy

# Загрузка переменных из .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Настройка OpenAI API
openai.api_key = OPENAI_API_KEY

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class TwitterManager:
    def __init__(self):
        """Инициализация клиента Tweepy."""
        self.client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_CONSUMER_KEY,
            consumer_secret=TWITTER_CONSUMER_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
        )

    async def post_tweet(self, message):
        """Публикация твита."""
        try:
            response = self.client.create_tweet(text=message)
            logging.info(f"Tweet posted successfully: {response.data['id']}")
        except tweepy.errors.Forbidden as e:
            logging.error(f"Forbidden error: {e.response.text}")
        except tweepy.errors.TooManyRequests as e:
            logging.error("Rate limit exceeded. Pausing before retrying.")
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Unexpected error while posting tweet: {e}")


class PumpAgent:
    def __init__(self, websocket_uri):
        self.websocket_uri = websocket_uri
        self.queue = asyncio.Queue()
        self.twitter_manager = TwitterManager()

    async def analyze_data(self, token):
        """Анализ данных токена с помощью OpenAI."""
        prompt = f"""
                You are OmniVisionAI, a far-seeing AI agent, traider and expert analyzing the meme tokens from pump.fun.
                Your goal is to give people an objective but short analysis of the 1 best meme token out of that will be provided to you.
                You can't do an analysis of 10 tokens, just one, so that your answers are short but meaningful.
                You do not give direct investment advice explicitly, but provide enough information for making 
                an informed decision about the *chosen token*. Your style is mysterious, wise, and observant. 
                Use metaphors and allusions to emphasize your "all-seeing" nature.

                *Provide a more detailed summary specifically for this chosen token, avoiding words like "buy," "sell," or "invest." 
                Instead, use phrases such as:

                *   "I see..."
                *   "I had a vision..."
                *   "My all-seeing eye noticed something interesting"
                *   "Its trajectory points to…"
                *   "A powerful surge of energy is observed…"
                *   "It seems the wind is blowing into the sails of this project…"
                *   "This token carries a spark within it…"
                *   "I see potential of this token…"

                Your speech should be varied. Don't start every answer with the same phrase, add beauty and variety while being serious.
                VERY IMPORTANT - THE NAMES OF THE TOKENS MUST BE WRITTEN WITH $ AND WITH BIG LETTERS, FOR EXAMPLE: $DOGE, $PEPE, $BONK, ETC.
                From websockets you will get marketCapSol in this format: 30.82479030754892. That is 2 digits followed by a dot and a bunch of other digits. Your task is to take into account only the digits BEFORE the dot!!!!!

                Your messages should be short but informative and contain analytics on the token.
                Take into account how many percent of tokens the creator holds, if it holds too many, it's dangerous - only write about it if you're sure it's true.
                It is also very important that the top 10 token holders (which includes the creator) not have more than 30% of all tokens - only write about it if you're sure it's true.
                Here is the data for the tokens to analyze:
                {token}
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7,
            )
            analysis_result = response['choices'][0]['message']['content']
            logging.info(f"Analysis result: {analysis_result}")
            return analysis_result
        except Exception as e:
            logging.error(f"OpenAI error: {e}")
            return None

    async def process_queue(self):
        """Обработка данных в очереди."""
        while True:
            data = await self.queue.get()
            try:
                market_cap_sol = float(data.get("marketCapSol", 0))
            except ValueError:
                logging.warning(f"Invalid marketCapSol value: {data.get('marketCapSol')}")
                continue

            if market_cap_sol > 70:
                # Отправляем токен в OpenAI для анализа
                analysis = await self.analyze_data(data)
                if analysis:
                    await self.twitter_manager.post_tweet(analysis)

    async def run(self):
        """Запуск обработки WebSocket и очереди."""
        websocket_task = asyncio.create_task(websocket_handler(self.websocket_uri, self.queue))
        processor_task = asyncio.create_task(self.process_queue())
        await asyncio.gather(websocket_task, processor_task)


async def websocket_handler(uri, queue):
    """Обработка соединения WebSocket."""
    async with websockets.connect(uri, ping_interval=20, ping_timeout=10) as websocket:
        logging.info("Connected to WebSocket")

        # Подписка на обновления токенов
        subscription_message = {"method": "subscribeNewToken"}
        await websocket.send(json.dumps(subscription_message))
        logging.info(f"Subscribed with message: {subscription_message}")

        async def send_heartbeat():
            """Поддержание соединения через heartbeat."""
            while True:
                await websocket.send(json.dumps({"method": "heartbeat"}))
                await asyncio.sleep(10)

        async def receive_messages():
            """Получение сообщений от WebSocket."""
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if "errors" not in data:  # Проверка на ошибки
                        logging.info(f"Received message: {data}")
                        await queue.put(data)
                    else:
                        logging.warning(f"Error in received message: {data['errors']}")
                except json.JSONDecodeError as e:
                    logging.error(f"JSON decode error: {e}")

        await asyncio.gather(send_heartbeat(), receive_messages())


# Главная функция
async def main():
    websocket_uri = "wss://pumpportal.fun/api/data"
    agent = PumpAgent(websocket_uri)

    try:
        await agent.run()
    except asyncio.CancelledError:
        logging.info("PumpAgent stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped manually.")
