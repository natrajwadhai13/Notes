Cron
----------------------------------
import os
import time
import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Load environment variables or defaults
INSTANCE_ID = os.environ.get("INSTANCE_ID", "i-046b95023c356a54b")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "7add990cd5ea")
REGION = os.environ.get("AWS_REGION", "us-east-1")

# Create the SSM client
ssm_client = boto3.client("ssm", region_name=REGION)

def lambda_handler(event, context):
    print("🚀 Lambda function triggered.")
    
    command_to_run = f"docker exec {CONTAINER_NAME} node /app/controllers/runReminders.js"
    print(f"📦 Command to run: {command_to_run} on EC2 instance: {INSTANCE_ID}")

    try:
        # Step 1: Send command
        response = ssm_client.send_command(
            InstanceIds=[INSTANCE_ID],
            DocumentName="AWS-RunShellScript",
            Parameters={
                "commands": [command_to_run]
            }
        )
        command_id = response["Command"]["CommandId"]
        print(f"✅ Command sent to SSM. Command ID: {command_id}")

        # Step 2: Poll for result
        for attempt in range(10):
            print(f"⏳ Polling attempt {attempt + 1} to check command status...")
            time.sleep(2)

            invocation = ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=INSTANCE_ID
            )

            status = invocation["Status"]
            print(f"🔁 Command status at attempt {attempt + 1}: {status}")

            if status in ["Success", "Failed", "Cancelled", "TimedOut"]:
                break

        # Step 3: Print logs
        stdout = invocation.get("StandardOutputContent", "(no output)")
        stderr = invocation.get("StandardErrorContent", "(no errors)")

        print("📤 Command STDOUT:\n", stdout)
        print("⚠️ Command STDERR:\n", stderr)

        # Step 4: Return response
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": status,
                "stdout": stdout,
                "stderr": stderr
            })
        }

    except (BotoCoreError, ClientError) as error:
        print("❌ An error occurred in Lambda:", error)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(error)})
        }
