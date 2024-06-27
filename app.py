from flask import Flask, request, render_template, redirect, url_for, Response
import os
from datetime import datetime
from twilio.rest import Client
from config import Config
from models.resnet50_model import analyze_image
import cv2

app = Flask(_name_)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

twilio_client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def calculate_dynamic_price(current_demand, base_price):
    max_price = base_price * 2
    min_price = base_price * 0.5
    price = base_price * (1 + current_demand / 100)
    return max(min(price, max_price), min_price)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"
    
    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        analysis_result = analyze_image(img_path=file_path)

        if analysis_result is not None:
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            output_csv_path = os.path.join(os.path.dirname(os.path.realpath(_file_)), f"{current_date}_parking_results.csv")

            with open(output_csv_path, 'a', newline='') as f:
                f.write(f"{file.filename},{analysis_result}\n")

            twilio_client.messages.create(
                body=f"Your parking spot {file.filename} is detected. Analysis result: {analysis_result}",
                from_=app.config['TWILIO_PHONE_NUMBER'],
                to='user_phone_number'
            )

            return redirect(url_for('index'))

    return "Analysis failed"

def generate_frames():
    camera = cv2.VideoCapture(0)  # 0 for default camera

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Analyze the frame
            analysis_result = analyze_image(img_array=frame)

            # Draw the analysis result on the frame
            if analysis_result is not None:
                cv2.putText(frame, f'Analysis: {analysis_result}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
