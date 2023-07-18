import os
import json
import boto3
import botocore

s3 = boto3.client('s3')


recording_bucket = "openvidu-recording-587ed"
path = "/opt/openvidu/recordings"

folders = os.listdir(path)

for folder in folders:
    files = os.listdir(f"{path}/{folder}")
    state_file  = list([ f for f in files if f.startswith(".recording")])
    mp4_file = list([ f for f in files if f.endswith(".mp4")])
   
    if state_file:
        d = f"{path}/{folder}/{state_file[0]}"
        with open(d, "r") as f:
            d = f.read()
            data = json.loads(d)
            if data['status'] == 'ready':
                try:
                    bucket_exist = s3.get_object(
                        Bucket=recording_bucket,
                        Key=mp4_file[0],
                    )

                except botocore.exceptions.ClientError as error :
                    if error.response['Error']['Code'] == 'NoSuchKey':
                        print(f"uploading {mp4_file}")
                        s3.upload_file(f"{path}/{folder}/{mp4_file[0]}",recording_bucket, mp4_file[0])
                    else:
                        print(f"error {error}")
            else:
                print(f"{state_file[0]} still streaming")



