from dotenv import load_dotenv
import os

load_dotenv(override=True)
token = os.getenv('META_ACCESS_TOKEN')
print('Current token:', token[:30] + '...' if token and len(token) > 30 else token)
print('Token length:', len(token) if token else 0)
