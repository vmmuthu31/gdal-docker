# Geospatial Python Runtime Deployment

This README outlines the steps to deploy a geospatial Python runtime environment on AWS using EC2 instances and Docker. The environment includes GDAL and other geospatial libraries, and exposes a Flask API for managing user-defined geospatial functions.

## Prerequisites

- AWS CLI configured with appropriate credentials
- AWS account with access to launch EC2 instances
- SSH key pair for accessing EC2 instances
- Git installed on your local machine

## Step 1: Launch an EC2 Instance

1. **Launch an EC2 Instance:**

   ```bash
   aws ec2 run-instances --image-id ami-0abcdef1234567890 --count 1 --instance-type t2.micro --key-name MyKeyPair --security-group-ids sg-0123456789abcdef0 --subnet-id subnet-6e7f829e
   ```

Connect to the EC2 Instance:

bash Code:
ssh -i "MyKeyPair.pem" ec2-user@ec2-198-51-100-1.compute-1.amazonaws.com
Step 2: Install Docker on the EC2 Instance
Update the package index:

bash Code:
sudo yum update -y
Install Docker:

bash Code:
sudo amazon-linux-extras install docker
Start the Docker service:

bash Code:
sudo service docker start
Add the ec2-user to the docker group:

bash Code:
sudo usermod -a -G docker ec2-user
Log out and log back in again to pick up the new docker group membership.

Step 3: Set Up the Docker Environment
Create a Dockerfile:

Dockerfile
Code:

# Use an official Python runtime as a parent image

FROM python:3.9-slim

# Set the working directory in the container

WORKDIR /usr/src/app

# Install GDAL, build tools, and other dependencies

RUN apt-get update && \
 apt-get install -y \
 gdal-bin \
 libgdal-dev \
 python3-gdal \
 build-essential \
 gcc \
 g++ && \
 rm -rf /var/lib/apt/lists/\*

# Install Python packages

RUN pip install --no-cache-dir \
 rasterio \
 geopandas \
 xarray \
 zarr \
 flask

# Verify GDAL installation

RUN gdalinfo --version

# Copy the current directory contents into the container at /usr/src/app

COPY . .

# Expose port 5000 for the Flask app

EXPOSE 5000

# Run the Flask app

CMD ["python", "main.py"]
Build the Docker Image:

Code:
docker build -t geospatial-python-runtime .
Run the Docker Container:

Code:
docker run -d -p 5000:5000 geospatial-python-runtime
Step 4: Set Up the Flask Application
Ensure your Flask application (main.py) is included in the Docker image.

Code:
from flask import Flask, request, jsonify, render_template_string
import os
import subprocess

app = Flask(**name**)

# Directory to store user functions

FUNCTIONS_DIR = "/usr/src/app/functions"

# Ensure the directory exists

os.makedirs(FUNCTIONS_DIR, exist_ok=True)

@app.route('/')
def index():
return render_template_string('''

<!DOCTYPE html>
<html>
<head>
<title>Geospatial Python Runtime API</title>
</head>
<body>
<h1>Geospatial Python Runtime API</h1>
<p>The API is working!</p>
<h2>Create Function</h2>
<form id="create-form">
<label for="name">Function Name:</label>
<input type="text" id="name" name="name"><br><br>
<label for="code">Function Code:</label><br>
<textarea id="code" name="code" rows="10" cols="50"></textarea><br><br>
<button type="button" onclick="createFunction()">Create Function</button>
</form>
<h2>Run Function</h2>
<form id="run-form">
<label for="run-name">Function Name:</label>
<input type="text" id="run-name" name="run-name"><br><br>
<label for="input">Input Data:</label><br>
<textarea id="input" name="input" rows="10" cols="50"></textarea><br><br>
<button type="button" onclick="runFunction()">Run Function</button>
</form>
<h2>Delete Function</h2>
<form id="delete-form">
<label for="delete-name">Function Name:</label>
<input type="text" id="delete-name" name="delete-name"><br><br>
<button type="button" onclick="deleteFunction()">Delete Function</button>
</form>
<script>
async function createFunction() {
const name = document.getElementById('name').value;
const code = document.getElementById('code').value;
const response = await fetch('/create_function', {
method: 'POST',
headers: {
'Content-Type': 'application/json'
},
body: JSON.stringify({name: name, code: code})
});
const result = await response.json();
alert(result.message);
}

            async function runFunction() {
                const name = document.getElementById('run-name').value;
                const input = document.getElementById('input').value;
                const response = await fetch(`/run_function/${name}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({input: input})
                });
                const result = await response.json();
                alert(JSON.stringify(result));
            }

            async function deleteFunction() {
                const name = document.getElementById('delete-name').value;
                const response = await fetch(`/delete_function/${name}`, {
                    method: 'DELETE',
                });
                const result = await response.json();
                alert(result.message);
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/create_function', methods=['POST'])
def create_function():
data = request.json
function_name = data['name']
function_code = data['code']

    # Save the function code to a file
    function_file = os.path.join(FUNCTIONS_DIR, f"{function_name}.py")
    with open(function_file, 'w') as f:
        f.write(function_code)

    return jsonify({"message": "Function created successfully"}), 201

@app.route('/run_function/<function_name>', methods=['POST'])
def run_function(function_name):
function_file = os.path.join(FUNCTIONS_DIR, f"{function_name}.py")
if not os.path.exists(function_file):
return jsonify({"error": "Function not found"}), 404

    input_data = request.json.get('input', {})

    # Run the function using subprocess
    result = subprocess.run(
        ["python", function_file],
        input=str(input_data),
        text=True,
        capture_output=True
    )

    if result.returncode != 0:
        return jsonify({"error": result.stderr}), 500

    return jsonify({"result": result.stdout}), 200

@app.route('/delete_function/<function_name>', methods=['DELETE'])
def delete_function(function_name):
function_file = os.path.join(FUNCTIONS_DIR, f"{function_name}.py")
if not os.path.exists(function_file):
return jsonify({"error": "Function not found"}), 404

    os.remove(function_file)
    return jsonify({"message": "Function deleted successfully"}), 200

if **name** == '**main**':
app.run(host='0.0.0.0', port=5000)
Verify the Application is Running:

Code:
curl http://localhost:5000

Step 5: Automate the Deployment
You can create a shell script to automate the deployment process.

Deployment Script
Create a file named deploy.sh with the following content:
#!/bin/bash

# Variables

AMI_ID="ami-0abcdef1234567890"
INSTANCE_TYPE="t2.micro"
KEY_NAME="MyKeyPair"
SECURITY_GROUP="sg-0123456789abcdef0"
SUBNET_ID="subnet-6e7f829e"
REGION="us-west-2"
IMAGE_NAME="geospatial-python-runtime"
CONTAINER_NAME="geospatial-runtime"
PORT=5000

# Launch EC2 instance

INSTANCE_ID=$(aws ec2 run-instances \
 --image-id $AMI_ID \
 --count 1 \
 --instance-type $INSTANCE_TYPE \
 --key-name $KEY_NAME \
 --security-group-ids $SECURITY_GROUP \
 --subnet-id $SUBNET_ID \
 --region $REGION \
 --query 'Instances[0].InstanceId' \
 --output text)

echo "Launched EC2 instance with ID: $INSTANCE_ID"

# Wait for the instance to be in a running state

aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get the public DNS name of the instance

INSTANCE_DNS=$(aws ec2 describe-instances \
 --instance-ids $INSTANCE_ID \
 --query 'Reservations[0].Instances[0].PublicDnsName' \
 --output text)

echo "Instance DNS: $INSTANCE_DNS"

# Connect to the instance and set up Docker environment

ssh -o StrictHostKeyChecking=no -i "$KEY_NAME.pem" ec2-user@$INSTANCE_DNS << EOF
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
logout
EOF

# Reconnect to apply Docker group membership

ssh -o StrictHostKeyChecking=no -i "$KEY_NAME.pem" ec2-user@$INSTANCE_DNS << EOF

# Clone your project repository if not already done

git clone https://github.com/your-repo/geospatial-python-runtime.git
cd geospatial-python-runtime

# Build and run the Docker container

docker build -t $IMAGE_NAME .
docker run -d -p $PORT:5000 --name $CONTAINER_NAME $IMAGE_NAME
EOF

echo "Deployment complete. Access the application at http://$INSTANCE_DNS:$PORT"

Accessing the Application
After running the script, you should be able to access your Flask application using the public DNS of your EC2 instance at port 5000.
