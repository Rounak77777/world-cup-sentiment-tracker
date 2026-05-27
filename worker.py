import json
import redis
import time
import sqlite3
from datetime import datetime
from transformers import pipeline  

#connecting to same redis queue
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

#loading domain specific model
print("Loading RoBERTa Sentiment Model (this takes a moment)...")
sentiment_analyzer = pipeline(
    "sentiment-analysis", 
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest"
)
print("Model loaded. Ready to process.")

#connect to SQLite database
conn = sqlite3.connect('sentiment_data.db', check_same_thread=False)
cursor = conn.cursor()

#the math mapping 
def map_sentiment(label, confidence):
    """Converts discrete labels into a continuous -1.0 to +1.0 scale.""" 
    if label == 'positive':
        return confidence  
    elif label == 'negative':
        return -confidence 
    else:
        return 0.0          # neutral

def process_queue():
    buffer = [] #temporary RAM list that will hold numeric sentiment scores
    last_flush_time = time.time() #timestamp of last time wrote to SQL, used to determine when 10 second window has passed

    while True:
        #pulls oldest post from queue (rpop = Right Pop, removes item from Redis so it's never processed twice)
        raw_data = redis_client.rpop("match_stream")
        current_time = time.time() 

        #aggregation timer (10 second window) 
        if current_time - last_flush_time >= 10:
            if len(buffer) > 0: 
                #calculate stats for this window
                avg_sentiment = sum(buffer) / len(buffer)
                post_volume = len(buffer)
                window_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                #writing single aggregated row to SQL
                cursor.execute(
                    "INSERT INTO timeline (timestamp, avg_sentiment, post_volume) VALUES (?, ?, ?)",
                    (window_timestamp, avg_sentiment, post_volume)
                )
                conn.commit()
                
                print(f"[{window_timestamp}] Wrote Window -> Vol: {post_volume} | Avg Sentiment: {avg_sentiment:.2f}")
                
                #clear buffer and reset the timer
                buffer.clear()
            
            last_flush_time = current_time

        if raw_data:
            #post found, convert JSON string back to python dictionary
            post = json.loads(raw_data)
            text = post['text']
            #run the model, it returns a list of dictionaries: [{'label': 'positive', 'score': 0.89}]
            result = sentiment_analyzer(post['text'])
            
            #extracting label and confidence score
            label = result[0]['label']
            confidence = result[0]['score']
            
            #map to number and add to RAM buffer
            numeric_score = map_sentiment(label, confidence)
            buffer.append(numeric_score)
            
        else:
            #the queue is empty.
            #sleeping for fraction of second so CPU isn't fried checking an empty queue 10,000 times a second.
            time.sleep(0.1)


if __name__ == "__main__":
    process_queue()