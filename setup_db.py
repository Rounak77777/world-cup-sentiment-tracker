import sqlite3

#createing a local file named 'sentiment_data.db'
conn = sqlite3.connect('sentiment_data.db')
cursor = conn.cursor()

#creating the aggregation table
#timestamp: start of the 10-second window
#avg_sentiment: The mean score between -1.0 and 1.0
#post_volume: How many posts were in this window (spikes indicate events like goals)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS timeline (
        timestamp DATETIME PRIMARY KEY,
        avg_sentiment REAL,
        post_volume INTEGER
    )
''')

conn.commit()
conn.close()
print("Database and table created successfully.")