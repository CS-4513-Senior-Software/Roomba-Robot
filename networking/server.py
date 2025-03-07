from flask import *
import sys
import os
import subprocess

# subprocess.run(["python", "../hardware/raspberry_pi/main.py"])  # Runs script.py as a separate process


script_dir = os.path.dirname(os.path.abspath(__file__))  # Current script dir
target_path = os.path.abspath(os.path.join(script_dir, "../hardware/raspberry_pi"))
sys.path.append(target_path)

from main import digital_write

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json  # Get JSON data sent from JavaScript
    print("Received data:", data)  # Log the data to console
    
    match data["message"]:
        case 'w':
            print("w")
            digital_write([0, 1, 0, 0], easing=False)
        case 's':
            digital_write([0, -1, 0, 0], easing=False)
        case 'a':
            digital_write([1, 0, 0, 0], easing=False)
        case 'd':
            digital_write([-1, 0, 0, 0], easing=False)
        case 'ArrowUp':
            digital_write([0, 0, 0, 100], easing=False)
        case 'ArrowDown':
            digital_write([0, 0, 0, -100], easing=False)
        case "stop":
            print("stop")
            digital_write([0, 0, 0, 0], easing=False)
    
    return jsonify({'message': 'Data received successfully', 'data': data})  # Send response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)