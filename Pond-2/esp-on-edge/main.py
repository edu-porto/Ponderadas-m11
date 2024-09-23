from flask import Flask, Response, render_template
import requests

app = Flask(__name__)

ESP32_STREAM_URL = 'http://10.128.0.31/'  # Your ESP32-CAM stream URL

def generate_frames():
    while True:
        try:
            # Set a timeout for the request
            response = requests.get(ESP32_STREAM_URL, stream=True, timeout=5)
            if response.status_code != 200:
                print("Failed to connect to the ESP32-CAM stream.")
                break
            
            # Read the stream in chunks
            buffer = b''
            for chunk in response.iter_content(chunk_size=1024):
                buffer += chunk
                a = buffer.find(b'\xff\xd8')  # Start of JPEG
                b = buffer.find(b'\xff\xd9')  # End of JPEG
                if a != -1 and b != -1:
                    jpg = buffer[a:b+2]
                    buffer = buffer[b+2:]
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching frame: {e}")
            break

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)