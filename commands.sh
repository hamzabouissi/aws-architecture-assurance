
# Download ssh-key for EC2
aws ec2 describe-key-pairs --filters Name=key-name,Values="Ec2Key" --output json --query 'KeyPairs[*].KeyPairId' | xargs -I{} aws ssm get-parameter --name /ec2/keypair/{} --with-decryption --query Parameter.Value --output text > new-key-pair.pem
# Create Vpc


aws cloudformation create-stack --stack-name openvidu-vpc-subnet --template-body file://vpc-subnet.yml --capabilities CAPABILITY_NAMED_IAM --parameters \
  ParameterKey=EnvironmentName,ParameterValue=test

# Create OpenVIdu EC2 Instance

aws cloudformation create-stack --stack-name openvidu-ec2 --template-body file://openvidu-ec2.yaml \
 --capabilities CAPABILITY_NAMED_IAM --parameters \
  ParameterKey=OpenViduSecret,ParameterValue=the_obvious_secret
  

# Create SQS

aws cloudformation create-stack --stack-name openvidu-eventbridge-sqs --template-body file://eventbridge_SQS.yml\
 --capabilities CAPABILITY_AUTO_EXPAND --parameter


# Create ECS

aws cloudformation create-stack --stack-name openvidu-ecs-stack --template-body file://service-fargate-private-subnet-private.yml \
 --capabilities CAPABILITY_NAMED_IAM --parameters \
  ParameterKey=EnvironmentName,ParameterValue=test

# Update ECS

aws cloudformation update-stack --stack-name openvidu-ecs-stack --template-body file://service-fargate-private-subnet-private.yml --capabilities CAPABILITY_NAMED_IAM --parameters \
  ParameterKey=EnvironmentName,ParameterValue=test \
  ParameterKey=ImageUrl,ParameterValue=363488162633.dkr.ecr.us-east-1.amazonaws.com/sqs-pull-ffmpeg-repo:latest

# Receive Messages from SQS

aws sqs receive-message --queue-url https://sqs.eu-west-3.amazonaws.com/021338898563/openvidu-eventbridge-sqs-MySqsQueue-Mgue4XS13pIZ --attribute-names All --message-attribute-names All --max-number-of-messages 10

# Login Ecr and push image
 aws ecr get-login-password \
    --region eu-west-3 \
| docker login \
    --username AWS \
    --password-stdin 021338898563.dkr.ecr.eu-west-3.amazonaws.com

docker push image 

# Run image

docker run -e AWS_SECRET_ACCESS_KEY= -e AWS_ACCESS_KEY_ID= -e AWS_DEFAULT_REGION=eu-west-3 -e QueueName=openvidu-eventbridge-sqs-MySqsQueue-Mgue4XS13pIZ -e DestinationBucket=openvidu-recording-14d7