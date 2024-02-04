import os

'''
Get and make these variables available from the env
    environment:
      - API_KEY=''
      - PULSAR_URL=''
      - BABBLEBOX_URL=''
'''
API_TOKEN = os.getenv('API_TOKEN')
PULSAR_URL = os.getenv('PULSAR_URL')
BABBLEBOX_URL = os.getenv('BABBLEBOX_URL')
