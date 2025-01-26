
# import tweepy
# import logging

# class TwitterManager:
#     def __init__(self, bearer_token, consumer_key, consumer_secret, access_token, access_token_secret):
#         # Инициализация клиента Tweepy для API v2
#         self.client = tweepy.Client(
#             bearer_token=bearer_token,
#             consumer_key=consumer_key,
#             consumer_secret=consumer_secret,
#             access_token=access_token,
#             access_token_secret=access_token_secret
#         )
#         logging.basicConfig(level=logging.INFO)
#         logging.info("TwitterManager initialized successfully.")

#     async def post_tweet(self, message):
#         try:
#             # Публикация твита через API v2
#             response = self.client.create_tweet(text=message)
#             logging.info(f"Tweet posted successfully: {response.data['id']}")
#             return response.data
#         except tweepy.errors.TweepyException as e:
#             logging.error(f"Error posting tweet: {e}")
#             raise

