from flask import Flask, Response, render_template
import requests
import cv2
import numpy as np

app = Flask(__name__)

# Endereço do esp32-cam 
ESP32_STREAM_URL = 'http://10.128.0.31/'  # Your ESP32-CAM stream URL
haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


# Essa função permite que o vídeo seja exibido no navegador 
def generate_frames():
    while True:
        try:
            # Set a timeout for the request
            response = requests.get(ESP32_STREAM_URL, stream=True, timeout=5)
            if response.status_code != 200:
                print("Erro na conexão com o ESP32-CAM.")
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
            print(f"Error : {e}")
            break

# Função que detecta os rostos com haar cascade 
def generate_haar_cascade_frames():
    while True:
        try:
            response = requests.get(ESP32_STREAM_URL, stream=True, timeout=5)
            if response.status_code != 200:
                print("Erro na conexão com o ESP32-CAM.")
                break

            buffer = b''
            for chunk in response.iter_content(chunk_size=1024):
                buffer += chunk
                a = buffer.find(b'\xff\xd8')  
                b = buffer.find(b'\xff\xd9') 
                if a != -1 and b != -1:
                    jpg = buffer[a:b+2]
                    buffer = buffer[b+2:]
                    
                    # Detectando os rostos   
                    img_array = np.frombuffer(jpg, dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = haar_cascade.detectMultiScale(gray, 1.3, 5)

                    # Desenha um retângulo ao redor de cada rosto detectado
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                    ret, jpeg = cv2.imencode('.jpg', frame)
                    if ret:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            break

# Rota que recebe o vídeo do ESP32-CAM 
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Rota com o vídeo já processado 
@app.route('/haar_cascade_feed')
def haar_cascade_feed():
    return Response(generate_haar_cascade_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Home
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)