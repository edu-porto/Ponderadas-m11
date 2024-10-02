from flask import Flask, Response, render_template, jsonify
import requests
import cv2
import numpy as np

app = Flask(__name__)

ESP32_STREAM_URL = 'http://10.128.0.23/'  

haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Onde eu salvo os dados das bounding boxes 
bounding_boxes = []


def generate_frames():
    while True:
        try:
            response = requests.get(ESP32_STREAM_URL, stream=True, timeout=5)
            if response.status_code != 200:
                print("Error connecting to ESP32-CAM.")
                break
            
            buffer = b''
            for chunk in response.iter_content(chunk_size=1024):
                buffer += chunk
                a = buffer.find(b'\xff\xd8')  # Start of JPEG
                b = buffer.find(b'\xff\xd9')  # End of JPEG
                if a != -1 and b != -1:
                    jpg = buffer[a:b + 2]
                    buffer = buffer[b + 2:]
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            break

# Usando o haar cascade e salvando as coordenadas 
def generate_haar_cascade_frames():
    global bounding_boxes  
    while True:
        try:
            response = requests.get(ESP32_STREAM_URL, stream=True, timeout=5)
            if response.status_code != 200:
                print("Error connecting to ESP32-CAM.")
                break

            buffer = b''
            for chunk in response.iter_content(chunk_size=1024):
                buffer += chunk
                a = buffer.find(b'\xff\xd8')  
                b = buffer.find(b'\xff\xd9') 
                if a != -1 and b != -1:
                    jpg = buffer[a:b + 2]
                    buffer = buffer[b + 2:]
                    
                    img_array = np.frombuffer(jpg, dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = haar_cascade.detectMultiScale(gray, 1.3, 5)


                    bounding_boxes = []  
                    for (x, y, w, h) in faces:
                        bounding_boxes.append({
                            'x': int(x),  
                            'y': int(y),
                            'w': int(w),
                            'h': int(h)
                        })
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                    ret, jpeg = cv2.imencode('.jpg', frame)
                    if ret:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            break

 
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Mostrando os resultados do video
@app.route('/haar_cascade_feed')
def haar_cascade_feed():
    return Response(generate_haar_cascade_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Rota que retorna as coordenadas da bounding box
@app.route('/bounding_boxes')
def get_bounding_boxes():
    return jsonify(bounding_boxes)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
