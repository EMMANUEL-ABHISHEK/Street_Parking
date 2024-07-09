from flask import Flask, request, render_template, redirect, url_for, Response, jsonify
import os
from datetime import datetime
from twilio.rest import Client
from config import Config
from models.resnet50_model import analyze_image
import cv2

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

twilio_client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])

registered_users = []

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

@app.route('/register', methods=['POST'])
def register_user():
    phone_number = request.form['phone_number']
    area = request.form['area']
    
    registered_users.append({'phone_number': phone_number, 'area': area})
    
    return jsonify({'message': 'User registered successfully'})

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

        try:
            # Check if the file is a video
            if file.filename.rsplit('.', 1)[1].lower() in ['mp4', 'avi', 'mov']:
                analysis_result = analyze_video(file_path)
            else:
                analysis_result = analyze_image(img_path=file_path)

            if analysis_result is not None:
                now = datetime.now()
                current_date = now.strftime("%Y-%m-%d")
                output_csv_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), f"{current_date}_parking_results.csv")

                with open(output_csv_path, 'a', newline='') as f:
                    f.write(f"{file.filename},{analysis_result}\n")

                for user in registered_users:
                    # Use your logic to detect area from analysis_result
                    area_detected = "some_area_from_analysis_result"

                    if user['area'] == area_detected:
                        twilio_client.messages.create(
                            body=f"Parking spot detected in {area_detected} for {file.filename}. Analysis result: {analysis_result}",
                            from_=app.config['TWILIO_PHONE_NUMBER'],
                            to=user['phone_number']
                        )

                return redirect(url_for('index'))

        except Exception as e:
            print(f"Error during analysis: {e}")
            return "Analysis failed"

    return "Analysis failed"

def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    analysis_result = None

    try:
        for _ in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break
            analysis_result = analyze_image(img_array=frame)  # Assuming analyze_image can process individual frames

            if analysis_result is not None:
                # Optionally, stop on the first detection
                break

    except Exception as e:
        print(f"Error analyzing video: {e}")
    finally:
        cap.release()

    return analysis_result

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
