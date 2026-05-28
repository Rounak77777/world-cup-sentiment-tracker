import websockets 
import json  
import asyncio 
import redis 
import re

#connecting to local Docker Redis container 
#port 6379 is default Redis port & db=0 is default database, decode_responses=True ensures we get clean strings back, not raw bytes
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True) 

KEYWORDS = [
    #core tournament (high volume)
    "world cup", "fifa2026", "wc2026", "worldcup2026",
    
    #high signal country identifiers (low noise)
    "#eng", "#fra", "#bra", "#arg", "#esp", "#usmnt", 
    "three lions", "seleção", "allez les bleus", "la albiceleste",
    
    #elite players (high specific volume)
    "mbappe", "bellingham", "vinicius", "messi", "lamine yamal", "haaland", "ronaldo"
]

#compiling regex pattern for strict word boundaries, ensures "pep" matches "pep out" but ignores "peppermint"
# \b means "word boundary", this creates a pattern like: \b(arsenal|man city|haaland|saka|pep)\b
PATTERN = re.compile(r'\b(' + '|'.join(KEYWORDS) + r')\b')

async def stream_bluesky():
    #only subscribes to text posts, filters out likes/follows at server level
    uri = "wss://jetstream1.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"

    print("Connecting to Bluesky Firehose...")

    #Opening the persistent connection to the Bluesky server
    async with websockets.connect(uri) as websocket:
        print("Connected. ...")
        #infinite listening loop
        while True:
             #await pauses specific loop until new message is received, allowing other tasks to run in meantime
             raw_message = await websocket.recv() 
             data = json.loads(raw_message) #parses raw json string to python dict

             #Ensures its new post, not a deletion
             if data.get('kind')=='commit' and data['commit'].get('operation')=='create':
                  record = data['commit']['record']

                  #Extractes text and convert all to lowercase (deafault to empty string if missing)
                  text =  record.get('text', '').lower() 

                  #regex search to ensure only posts that mention keywords as standalone words are captured, not as part of other words
                  if PATTERN.search(text):
                    payload = {
                        "timestamp": record.get('createdAt'),
                        "text": text
                    }
                    
                    #convert dictionary back to JSON string and push it into Redis List called "match_stream"
                    redis_client.lpush("match_stream", json.dumps(payload))
                    print(f"Pushed to queue: {text[:50]}...")


#Running async event loop 
if __name__ == "__main__": 
    try:
        asyncio.run(stream_bluesky())   
    except KeyboardInterrupt: 
            print("\nDisconnected.")
            