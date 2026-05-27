#starting with lightweight version of Python 3.11
FROM python:3.11-slim

#setting working directory inside container
WORKDIR /app

#copying requirements file and installing libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copying all Python scripts into container
COPY . .

#we don't define run command here as Docker Compose will tell each container which specific script to run