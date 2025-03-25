from flask import *
import sys
import os

# subprocess.run(["python", "../hardware/raspberry_pi/main.py"])  # Runs script.py as a separate process


script_dir = os.path.dirname(os.path.abspath(__file__))  # Current script dir
target_path = os.path.abspath(os.path.join(script_dir, "../hardware/raspberry_pi"))
sys.path.append(target_path)

from main import digital_write, generate_frames

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/videoFeed')
def videoFeed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/writeRequest', methods=['POST'])
def writeRequest():
    data = request.json  # Get JSON data sent from JavaScript
    msg = data["message"]
    axis_values = [msg["LR"], msg["FB"], msg["PAN"], msg["TILT"]]
    
    print(f"Received: {axis_values}")  # Debugging log
    digital_write(axis_values, easing=False)
    
    return jsonify({'message': 'Data received successfully', 'data': data})  # Send response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)