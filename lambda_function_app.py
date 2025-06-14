import boto3
import os
import json

def lambda_handler(event, context):
    github_token = os.environ['GITHUB_PAT']

    # Command to be run on EC2 instance
    commands = [
        "cd /home/ec2-user/CICD || exit 1",

        # Clone or pull frontend
        f"if [ ! -d frontend ]; then git clone https://x:{github_token}@github.com/natrajwadhai13/app.narasolicitors.co.uk.frontend.git frontend; else cd frontend && git pull && cd ..; fi",

        # Build frontend Docker
        "cd frontend",
        "docker build -t frontend-app .",
        "docker stop frontend-container || true",
        "docker rm frontend-container || true",
        "docker run -d --name frontend-container -p 2000:2000 frontend-app",
        "cd ..",

        # Clone or pull backend
        f"if [ ! -d backend ]; then git clone https://x:{github_token}@github.com/natrajwadhai13/app.narasolicitors.co.uk.backend.git backend; else cd backend && git pull && cd ..; fi",

        # Build backend Docker
        "cd backend",
        "docker build -t backend-app .",
        "docker stop backend-container || true",
        "docker rm backend-container || true",
        "docker run -d --name backend-container -p 1000:1000 backend-app"
    ]

    ssm = boto3.client('ssm')

    response = ssm.send_command(
        InstanceIds=["i-046b95023c356a54b"],  # Replace with your EC2 Instance ID
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': commands},
    )

    return {
        "statusCode": 200,
        "body": json.dumps("✅ Command sent to EC2 via SSM.")
    }
