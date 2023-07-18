import boto3
import subprocess
import json
import os
import time
import shutil

session = boto3.Session()

s3 = session.client("s3")
sqs = session.client("sqs")

queueName = os.getenv("QueueName",)
destinationBucket = os.getenv("DestinationBucket")
queue = sqs.get_queue_url(QueueName=queueName)
while True:
    # Get the queue
    
    time.sleep(60)
    # Receive a new message
    response = sqs.receive_message(
        QueueUrl=queue["QueueUrl"],
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        VisibilityTimeout=360,
        WaitTimeSeconds=5,
    )
    
    if not response.get("Messages", None):
        print({"Status": "Info", "Message": "escape processing"})
        continue
    for message in response["Messages"]:
        print(f"processing message with id {message['MessageId']}")
        body = json.loads(message["Body"])
        if isinstance(body,list):
           body = body[0]
        bucketName = body["detail"]["bucket"]["name"]
        object_name = body["detail"]["object"]["key"]
        output = body["detail"]["object"]["key"].split(".")[0]
        output = output + ".m3u6"
        object_folder = object_name.split(".")[0]

        print(f"changing folder to {object_folder}")
        os.mkdir(object_folder)
        os.chdir(object_folder)
        
        print({"Status": "Info","Message": f"download file {object_name}"})
        s3.download_file(bucketName, object_name, object_name)
        
        print({"Status": "Info","Message": f"ffmpeg is running for {object_name}"})
        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                object_name,
                "-codec:",
                "copy",
                "-start_number",
                "0",
                "-hls_time",
                "10",
                "-hls_list_size",
                "0",
                "-f",
                "hls",
                output,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print({"Status": "ERROR", "Message": result.stderr})
            continue
        
        print({"Status": "INFO", "Message": result.stdout})
        
        os.chdir("../")

        print(f"create {object_folder} folder on {destinationBucket}")
        s3.put_object(Bucket=destinationBucket,Key=f"{object_folder}/")

        for file_ in os.listdir(object_folder):
            print(f"uploading file {file_}")
            s3.upload_file(f"{object_folder}/{file_}",destinationBucket,f"{object_folder}/{file_}")
        
        print(f"deleting {object_folder}")
        shutil.rmtree(object_folder)
        
        print(f"deleting the message {message['ReceiptHandle']}")
        response = sqs.delete_message(
            QueueUrl=queue["QueueUrl"], ReceiptHandle=message['ReceiptHandle']
        )