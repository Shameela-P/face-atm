import base64
import cv2
import numpy as np
import tensorflow as tf
from mtcnn import MTCNN
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pickle

app = Flask(__name__)
CORS(app) # Allow SvelteKit to connect

# Initialize models
print("Loading Models...")
detector = MTCNN()
try:
    liveness_model = tf.keras.models.load_model("liveness.model")
except:
    try:
        liveness_model = tf.keras.models.load_model("liveness_model.h5")
    except Exception as e:
        print("Warning: Liveness model not found.", e)

try:
    facenet = tf.keras.models.load_model("facenet_keras.h5", compile=False)
except Exception as e:
    print("Warning: FaceNet model not found.", e)

# Helper function to convert base64 from SvelteKit to OpenCV Image
def get_cv2_image_from_base64(b64_string):
    header, encoded = b64_string.split(",", 1)
    nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def detect_mobile_photo(face_img):
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    texture_std = np.std(gray)
    if texture_std < 18:
        return True
    return False

def check_liveness_cnn(face_img):
    if detect_mobile_photo(face_img):
        return False
    face_resized = cv2.resize(face_img, (64, 64))
    face_resized = face_resized.astype("float32") / 255.0
    face_resized = np.expand_dims(face_resized, axis=0)
    pred = liveness_model.predict(face_resized, verbose=0)[0][0]
    return pred > 0.5

@app.route('/verify_face', methods=['POST'])
def verify_face():
    data = request.json
    b64_img = data.get('image')
    user_id = data.get('uid')
    
    if not b64_img:
        return jsonify({"status": "error", "message": "No image provided"}), 400

    img = get_cv2_image_from_base64(b64_img)
    
    # 1. MTCNN Detection
    results = detector.detect_faces(img)
    if len(results) == 0:
        return jsonify({"status": "error", "message": "No face detected"})
    if len(results) > 1:
        return jsonify({"status": "error", "message": "Multiple faces detected"})

    x, y, w, h = results[0]['box']
    face_img = img[max(0, y):y+h, max(0, x):x+w]

    # 2. Liveness Check
    is_live = check_liveness_cnn(face_img)
    if not is_live:
        return jsonify({"status": "fail", "message": "Spoof detected (Liveness Failed)"})

    # 3. FaceNet Embedding
    face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    face_norm = cv2.resize(face_rgb, (160, 160))
    face_norm = face_norm.astype("float32") / 255.0
    embedding = facenet.predict(np.expand_dims(face_norm, axis=0), verbose=0)[0]

    # 4. Compare with existing dataset
    # (Since we are using DB, the user's images should be in dataset/user{user_id})
    user_dir = f"dataset/user{user_id}"
    if not os.path.exists(user_dir):
        return jsonify({"status": "error", "message": "User face dataset not found"})

    match_found = False
    for filename in os.listdir(user_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            path = os.path.join(user_dir, filename)
            db_img = cv2.imread(path)
            if db_img is None: continue
            
            db_rgb = cv2.cvtColor(db_img, cv2.COLOR_BGR2RGB)
            db_norm = cv2.resize(db_rgb, (160, 160)).astype("float32") / 255.0
            db_emb = facenet.predict(np.expand_dims(db_norm, axis=0), verbose=0)[0]
            
            # Euclidean distance
            dist = np.linalg.norm(embedding - db_emb)
            if dist < 1.0:  # Threshold for FaceNet
                match_found = True
                break

    if match_found:
        return jsonify({"status": "success", "message": "Identity Verified"})
    else:
        return jsonify({"status": "fail", "message": "Face mismatch (Identity Failed)"})

if __name__ == '__main__':
    app.run(port=5000)
