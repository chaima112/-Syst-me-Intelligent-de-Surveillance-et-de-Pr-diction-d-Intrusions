from flask import Flask, render_template, Response, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np
import threading
import queue
import time
import os
#import winsound 
from datetime import datetime

app = Flask(__name__)

if not os.path.exists('static/captures'):
    os.makedirs('static/captures')

model = YOLO('best.pt')
CONF_THRESH = 0.5

frame_queue = queue.Queue(maxsize=5)
latest_annotated = None
latest_score = 0
movement_detected = False
total_detections = 0
last_detection_time = "-"
lock = threading.Lock()

# 3. دالة معالجة الصور (القلب النابض للمشروع)
def process_frames():
    global latest_annotated, latest_score, movement_detected, total_detections, last_detection_time
    
    while True:
        if not frame_queue.empty():
            img = frame_queue.get()
            results = model(img, conf=CONF_THRESH)
            
            # البحث عن الأشخاص فقط
            found_persons = [box for box in results[0].boxes if model.names[int(box.cls[0])] == 'person']
            
            with lock:
                if len(found_persons) > 0:
                    # إذا اكتشف شخص جديد (لم يكن موجوداً في الإطار السابق)
                    if not movement_detected:
                        total_detections += 1
                        movement_detected = True
                    
                    latest_score = round(found_persons[0].conf[0].item() * 100, 2)
                    last_detection_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # تسجيل الصورة (الـ Capture)
                    img_name = f"intruder_{datetime.now().strftime('%H%M%S')}.jpg"
                    save_path = f"static/captures/{img_name}"
                    annotated_plot = results[0].plot()
                    
                    cv2.imwrite(save_path, annotated_plot)
                    cv2.imwrite('static/captures/latest.jpg', annotated_plot) # للعرض السريع
                    
                    # تنبيه صوتي
                    #winsound.Beep(1000, 200)
                else:
                    movement_detected = False
                    latest_score = 0
                
                # تحويل الصورة الحالية لـ Stream
                annotated_img = results[0].plot()
                _, buffer = cv2.imencode('.jpg', annotated_img)
                latest_annotated = buffer.tobytes()
                
        time.sleep(0.01)

# تشغيل المعالجة في الخلفية
threading.Thread(target=process_frames, daemon=True).start()

# 4. الـ Routes (المسارات)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'imageFile' in request.files:
        file = request.files['imageFile']
        nparr = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None and not frame_queue.full():
            frame_queue.put(img)
        return "[SUCCESS]", 201
    return "[FAILED]", 400

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            with lock:
                if latest_annotated is not None:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + latest_annotated + b'\r\n')
            time.sleep(0.05)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_status')
def get_status():
    with lock:
        return jsonify({
            "score": latest_score,
            "movement": movement_detected,
            "total": total_detections,
            "time": last_detection_time
        })

if __name__ == '__main__':
    # أعملي host='0.0.0.0' باش تجمي تحليه من تليفونك زادة
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
