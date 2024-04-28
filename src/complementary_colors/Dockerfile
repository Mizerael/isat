FROM isat-base:latest 
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY ./src src

ENTRYPOINT ["uvicorn", "--app-dir", "src", "--host", "0.0.0.0", "main:app", "--port", "8011"]