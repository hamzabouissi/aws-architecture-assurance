import boto3
import uuid
import json

session = boto3.Session()
s3 = session.client('s3')
sqs = session.client('sqs')
queue = sqs.get_queue_url(QueueName='openvidu-eventbridge-sqs-MySqsQueue-DZKc9xpSz6d7')

files = s3.list_objects_v2(Bucket="openvidu-recording-597edw") # source bucket
names = []
for f in files['Contents']:
    names.append(f['Key'])



messages = []
for name in names:
    message = {
        "version": "0",
        "id": "c9f6251e-97a8-411f-b517-e9e2129ebe2c",
        "detail-type": "Object Created",
        "source": "aws.s3",
        "account": "363488162633",
        "time": "2023-05-09T18: 47: 46Z",
        "region": "us-east-1",
        "resources": [
            "arn:aws:s3:::openvidu-recording-597edw"
        ],
        "detail": {
            "version": "0",
            "bucket": {
                "name": "openvidu-recording-597edw"
            },
            "object": {
                "key": name,
                "sequencer": "00645A95522F1DF46A"
            },
            "request-id": "DF5YFEFPYR3WNDAG",
            "requester": "363488162633",
            "source-ip-address": "102.171.186.85",
            "reason": "PutObject"
        }
    },
    messages.append({
        "Id":str(uuid.uuid4()),
        "MessageBody":json.dumps(message)
    })
for start in range(0,len(messages),10): # because sqs batch can send maximum of 10 messages
    end = start+10    
    if end > len(messages):
        end = len(messages)
    print(start,end)
    result = messages[start:end]
    # response = sqs.send_message_batch(QueueUrl=queue['QueueUrl'], Entries=result)

print("end")

