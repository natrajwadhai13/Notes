AWS_lambda Code Node Js
---------------------------------------------

import {
    SSMClient,
    SendCommandCommand,
    GetCommandInvocationCommand,
  } from "@aws-sdk/client-ssm";
  
  // Set environment variables or use defaults
  const INSTANCE_ID = process.env.INSTANCE_ID || "i-046b95023c356a54b"; // EC2 instance where Docker is running
  const CONTAINER_NAME = process.env.CONTAINER_NAME || "Live_backend_container";  // Docker container name
  const REGION = process.env.AWS_REGION || "us-east-1";                // AWS region
  
  // Create an SSM client instance for issuing commands
  const client = new SSMClient({ region: REGION });
  
  export const handler = async (event) => {
    console.log("🚀 Lambda function triggered.");
  
    try {
      // Step 1: Build the shell command to run inside Docker
      const commandToRun = `docker exec ${CONTAINER_NAME} node /app/controllers/runReminders.js`;
      console.log(`📦 Command to run: ${commandToRun} on EC2 instance: ${INSTANCE_ID}`);
  
      // Step 2: Prepare the SSM SendCommand request to run the command
      const sendCommand = new SendCommandCommand({
        InstanceIds: [INSTANCE_ID],              // The EC2 instance ID
        DocumentName: "AWS-RunShellScript",      // Built-in SSM document to run shell scripts
        Parameters: {
          commands: [commandToRun],              // Actual shell command to run inside EC2
        },
      });
  
      // Step 3: Send the command to SSM
      const { Command } = await client.send(sendCommand);
      const commandId = Command.CommandId;       // Capture the command ID for polling
      console.log("✅ Command sent to SSM. Command ID:", commandId);
  
      // Step 4: Poll for command result (up to 10 tries with 2-second delay each)
      let result;
      for (let i = 0; i < 10; i++) {
        console.log(`⏳ Polling attempt ${i + 1} to check command status...`);
  
        // Wait for 2 seconds before checking the result
        await new Promise((r) => setTimeout(r, 2000));
  
        // Prepare request to get the command result
        const getCommand = new GetCommandInvocationCommand({
          CommandId: commandId,
          InstanceId: INSTANCE_ID,
        });
  
        // Fetch the result of the command
        result = await client.send(getCommand);
        console.log(`🔁 Command status at attempt ${i + 1}: ${result.Status}`);
  
        // If command has completed (success/fail), exit the loop
        if (
          ["Success", "Failed", "Cancelled", "TimedOut"].includes(result.Status)
        ) {
          break;
        }
      }
  
      // Step 5: Output result logs
      console.log("📤 Command STDOUT:\n", result.StandardOutputContent || "(no output)");
      console.error("⚠️ Command STDERR:\n", result.StandardErrorContent || "(no errors)");
  
      // Step 6: Return the final response from Lambda
      return {
        statusCode: 200,
        body: JSON.stringify({
          status: result.Status,                  // Final status of the command
          stdout: result.StandardOutputContent,   // Anything printed to stdout
          stderr: result.StandardErrorContent,    // Errors or warnings from the script
        }),
      };
    } catch (err) {
      // Step 7: Catch and log any errors from SSM or Lambda itself
      console.error("❌ An error occurred in Lambda:", err);
      return {
        statusCode: 500,
        body: JSON.stringify({ error: err.message }),
      };
    }
  };
  
