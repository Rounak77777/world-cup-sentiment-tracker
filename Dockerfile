FROM python:3.11-slim

#preventing Python from writing .pyc files and force stdout logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#setting working directory inside container
WORKDIR /app

#copying requirements file and installing libraries first to cache the layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copying all Python scripts into container
COPY . .

#executing the actual script
CMD ["python", "producer.py"]