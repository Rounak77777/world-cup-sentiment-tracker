# Real-Time Premier League Sentiment Tracker

A distributed, asynchronous data pipeline that ingests live social media data, performs real-time Natural Language Processing (NLP), and visualizes public sentiment shifts during matches.

## 📺 Live Demo
*(Insert a link to a 2-minute YouTube screen recording of your dashboard updating live here)*

## 🏗️ System Architecture
This project is built using a decoupled microservices architecture, entirely containerized via Docker.

1. **Ingestion Node (Producer):** Maintains an open WebSocket connection to the data firehose. Filters incoming global data using regex word boundaries for specific entities and pushes raw text to a RAM buffer.
2. **Message Broker (Redis):** Acts as a high-speed, in-memory queue to decouple ingestion speed from processing speed, preventing the system from choking during high-volume match events.
3. **NLP Worker:** Pulls asynchronously from Redis. Uses `cardiffnlp/twitter-roberta-base-sentiment-latest` via HuggingFace Transformers to accurately score modern internet slang and sarcasm in real-time. 
4. **Aggregation Engine:** Groups scored text into 10-second rolling windows, calculates statistical means, and commits the aggregated volume/sentiment metrics to SQLite.
5. **Frontend (Plotly Dash):** A reactive, dual-axis dashboard that queries the database and visualizes the moving average of public sentiment against total post volume.

## ⚙️ Tech Stack
* **Languages:** Python 3.11
* **Message Broker:** Redis
* **Machine Learning:** PyTorch, HuggingFace (RoBERTa)
* **Database:** SQLite
* **Frontend:** Plotly Dash, Pandas
* **Infrastructure:** Docker & Docker Compose

## 🚀 How to Run Locally

You must have Docker and Docker Desktop installed and running on your machine.

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git)
   cd YOUR-REPO-NAME
2. Build and launch the containerized fleet:
   ```bash
   docker-compose up --build -d
   ```
3. Open your browser and navigate to:
   `http://localhost:8050`

4. To gracefully shut down the pipeline and free up system resources:
   ```bash
   docker-compose down
   ```   