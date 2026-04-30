import cv2
import requests
import time

# الـ URL متاع الـ Flask اللي خدام عندك توة
url = "http://127.0.0.1:5000/upload"

cap = cv2.VideoCapture(0) # حل كاميرا الـ PC

while True:
    ret, frame = cap.read()
    if not ret: break

    # تحويل الصورة لـ JPEG
    _, img_encoded = cv2.imencode('.jpg', frame)
    
    # بعث الصورة للـ Flask ( imageFile هو الاسم اللي يستناه Flask)
    files = {'imageFile': ('image.jpg', img_encoded.tobytes(), 'image/jpeg')}
    
    try:
        response = requests.post(url, files=files)
        print(f"Status: {response.status_code}") # لازم يكتبلك 201
    except:
        print("Erreur de connexion")

    time.sleep(0.1) # سرعة الإرسال