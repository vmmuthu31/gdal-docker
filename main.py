from flask import Flask, request, jsonify, render_template_string
import os
import subprocess

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
