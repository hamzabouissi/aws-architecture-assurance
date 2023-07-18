from python:3.10-slim-buster

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install -y ffmpeg

RUN pip install boto3 botocore

COPY python_scripts/pull-sqs-and-ffmpeg.py .

CMD ["python", "-u", "pull-sqs-and-ffmpeg.py"]