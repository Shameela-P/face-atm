import os
import tkinter as tk
from tkinter import messagebox
import cv2
import mysql.connector
import imutils
import numpy as np
from PIL import Image, ImageTk
from mtcnn import MTCNN
import threading
import time
import pickle
#
#from keras_facenet import FaceNet
from numpy.linalg import norm
import datetime
import tensorflow as tf
from tensorflow.keras.models import load_model
from skimage.feature import local_binary_pattern
import urllib.request
import urllib.parse
from urllib.request import urlopen
# ------------------ DATABASE ------------------
'''
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    charset="utf8",
    database="atm_face_multi"
)
cursor = mydb.cursor()
'''

class ATM:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM Simulator")
        self.root.state("zoomed")

        # Screen dimensions
        self.W = self.root.winfo_screenwidth()
        self.H = self.root.winfo_screenheight()
        
        self.LEFT_X = int(self.W * 0.30) + 80
        self.RIGHT_X = int(self.W * 0.72) - 80
        self.SY1 = int(self.H * 0.18)
        self.SY2 = int(self.H * 0.70)

        self.CENTER_X = self.W // 2
        self.CENTER_Y = (self.SY1 + self.SY2) // 2

        self.card_number = None
        self.cam_running = False
        self.cap = None
        self.user_id = 0

        self.cam_width = 200   # width of camera preview
        self.cam_height = 200  # height of camera preview
        self.cam_x = self.LEFT_X
        self.cam_y = (self.SY1 + self.SY2) // 2

        # --- LIVENESS ---
        self.blink_count = 0
        self.eye_closed_frames = 0
        self.eye_state = "OPEN"

        self.EAR_CLOSE_THRESH = 0.18
        self.EAR_OPEN_THRESH = 0.23
        self.MIN_CLOSED_FRAMES = 2
        self.REQUIRED_BLINKS = 2
        self.prev_eye_y = None
        self.eye_closed = False
        
        self.liveness_passed = False

        # --- FACE LOCK ---
        self.face_captured = False
        self.captured_face = None

        self.verify_start_time = None

        # ---- BLINK (MTCNN SAFE) ----
        self.prev_eye_y = None
        
        self.eye_close_frames = 0
        

        self.EYE_CLOSE_DELTA = 4     # pixels
        self.MIN_CLOSE_FRAMES = 2
        self.REQUIRED_BLINKS = 2

        self.match_result = None     # True / False
        self.match_distance = None
        self.match_image_path = None

        self.blink_count = 0
        self.eye_closed = False
        self.blink_verified = False
        self.face_captured = False
        self.comparison_shown = False
        self.match_result = None


        self.prev_eyes_open = True
        self.blink_done = False

        self.face_captured = False
        self.face_capture_time = 0


        self.EAR_THRESHOLD = 0.20   # tune if needed
        self.MIN_BLINK_GAP = 0.25   # seconds
        self.last_blink_time = 0
        self.waiting_for_approval = False

        self.approved_amount = 0
        self.approved_accid = 0
        # ------------------ Load Models ------------------

        
        
        
        self.confidence_threshold = 0.3
        self.face_captured = False
        self.face_capture_time = 0
        try:
            # Face recognizer
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.recognizer.read("trainer/trainer.yml")

            # Encodings
            encodings_path = 'encoded_faces.pickle'
            with open(encodings_path, 'rb') as file:
                self.encoded_data = pickle.loads(file.read())

            # Face detector
            self.detector_folder = 'face_detector'
            proto_path = os.path.sep.join([self.detector_folder, 'deploy.prototxt'])
            model_path_detector = os.path.sep.join([self.detector_folder, 'res10_300x300_ssd_iter_140000.caffemodel'])
            self.detector_net = cv2.dnn.readNetFromCaffe(proto_path, model_path_detector)

            # Liveness model
            model_path = 'liveness.model'
            le_path = 'label_encoder.pickle'
            self.liveness_model = tf.keras.models.load_model(model_path)
            with open(le_path, 'rb') as f:
                self.le = pickle.loads(f.read())

        except Exception as e:
            messagebox.showerror("Error", f"Model load failed:\n{e}")
            self.root.destroy()
            return
        
        # Canvas
        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        bg_img = Image.open("at1.png").resize((self.W, self.H), Image.Resampling.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(bg_img)

        # Database connection
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            charset="utf8",
            database="atm_face_multi"
        )

        # Face system
        self.detector = MTCNN()
        self.mtcnn_detector = self.load_mtcnn()
        #self.embedder = FaceNet()
        facenet = load_model("facenet_keras.h5")
        
        self.face_verified = False
        self.verified_name = None

        # Load trained face database
        if os.path.exists("face_db.pkl"):
            with open("face_db.pkl", "rb") as f:
                self.face_db = pickle.load(f)
        else:
            self.face_db = {}
            print("WARNING: face_db.pkl not found!")

        # Liveness vars
        self.verify_duration = 25
        self.prev_eye_dist = None
        self.blink_detected = False
        self.prev_nose_x = None
        self.head_moved = False

        self.screen_card()

    # ------------------ MESSAGES ------------------
    def load_mtcnn(self):
        from mtcnn import MTCNN
        return MTCNN()
    def show_msg(self, message, color="white"):
        self.canvas.delete("status_msg")
        msg_y = self.SY1 + 90
        self.canvas.create_text(
            self.CENTER_X, msg_y,
            text=message,
            font=("Arial", 18, "bold"),
            fill=color,
            tags=("ui", "status_msg")
        )
    def load_user_embeddings(self, user_id):
        """
        Load all face images for the user from vt_face table,
        compute embeddings and return a list of embeddings
        """
        cur = self.db.cursor()
        cur.execute("SELECT vface FROM vt_face WHERE vid=%s", (user_id,))
        rows = cur.fetchall()

        embeddings = []

        for row in rows:
            filename = row[0]  # e.g., User.1.2.jpg
            path = os.path.join("dataset", f"user{user_id}", filename)
            if os.path.exists(path):
                img = cv2.imread(path)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (160,160))
                img = img.astype("float32") / 255.0
                emb = self.embedder.embeddings([img])[0]
                embeddings.append(emb)
            else:
                print(f"WARNING: {path} not found!")

        return embeddings
    # ------------------ LIVENESS ------------------
    '''def eye_aspect_ratio(self, eye):
        eye = np.array(eye)
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])
        if C == 0:
            return 0
        return (A + B) / (2.0 * C)'''
    def eye_aspect_ratio(self, eye):
        # eye = [(x1,y1),(x2,y2)...(x6,y6)]
        A = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))
        B = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))
        C = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))
        return (A + B) / (2.0 * C)

    def eyes_open(self, kp):
        le = kp['left_eye']
        re = kp['right_eye']

        # vertical distance small → closed
        return abs(le[1] - re[1]) > 3
    # ----------------- EYE BLINK -----------------
    def check_eye_blink(self, kp):
        """
        Returns True only when 2 proper blinks are completed
        """

        # Approximate eye landmarks from MTCNN
        left_eye = kp['left_eye']
        right_eye = kp['right_eye']

        # Fake 6-point eye (simple vertical check)
        eye_dist = abs(left_eye[1] - right_eye[1])

        now = time.time()

        # EYES CLOSED
        if eye_dist < 4 and not self.eye_closed:
            self.eye_closed = True

        # EYES OPEN AFTER CLOSE = BLINK
        elif eye_dist >= 4 and self.eye_closed:
            if now - self.last_blink_time > self.MIN_BLINK_GAP:
                self.blink_count += 1
                self.last_blink_time = now
            self.eye_closed = False

        if self.blink_count >= 2:
            self.blink_verified = True
            return True

        return False
    '''def check_eye_blink(self, kp):
        
        left_eye = kp['left_eye']
        right_eye = kp['right_eye']

        # Average Y of both eyes
        eye_y = (left_eye[1] + right_eye[1]) // 2

        # ---------- FIRST FRAME FIX ----------
        if self.prev_eye_y is None:
            self.prev_eye_y = eye_y
            return False

        diff = eye_y - self.prev_eye_y
        self.prev_eye_y = eye_y

        CLOSE_THRESHOLD = 4    # eye moves down
        OPEN_THRESHOLD = -4   # eye moves up
        BLINK_COOLDOWN = 0.3  # seconds

        now = time.time()

        # -------- EYE CLOSED --------
        if diff > CLOSE_THRESHOLD and not self.eye_closed:
            self.eye_closed = True
            self.eye_close_time = now

        # -------- EYE OPEN (BLINK COUNT) --------
        if diff < OPEN_THRESHOLD and self.eye_closed:
            if now - self.last_blink_time > BLINK_COOLDOWN:
                self.blink_count += 1
                self.last_blink_time = now

            self.eye_closed = False

        # -------- BLINK VERIFIED --------
        if self.blink_count >= 3:
            return True

        return False'''



    def check_liveness(self, kp):
        le = kp['left_eye']
        re = kp['right_eye']

        avg_eye_y = (le[1] + re[1]) // 2

        if self.prev_eye_y is None:
            self.prev_eye_y = avg_eye_y
            return False

        diff = avg_eye_y - self.prev_eye_y
        self.prev_eye_y = avg_eye_y

        CLOSE_THRESH = 3  # adjust for small movements

        # Detect simple up-down movement
        if diff > CLOSE_THRESH and not self.eye_closed:
            self.eye_closed = True

        if diff < -CLOSE_THRESH and self.eye_closed:
            self.blink_count += 1
            self.eye_closed = False
            print("Blink:", self.blink_count)

        return self.blink_count >= 2

    # Load your pretrained liveness model
    #self.liveness_model = load_model("liveness_model.h5")

    # Preprocessing function
    '''def preprocess_face_for_liveness(self, face_img, target_size=(64,64)):
        face_resized = cv2.resize(face_img, target_size)
        face_normalized = face_resized.astype("float") / 255.0
        face_batch = np.expand_dims(face_normalized, axis=0)
        return face_batch

    def check_liveness_cnn(self, face_img):
        pre = self.preprocess_face_for_liveness(face_img)
        pred = self.liveness_model.predict(pre)[0][0]
        return True if pred > 0.5 else False'''
    def preprocess_face_for_liveness(self, face_img):
        face_resized = cv2.resize(face_img, (64, 64))
        face_resized = face_resized.astype("float32") / 255.0
        face_resized = np.expand_dims(face_resized, axis=0)
        return face_resized  # (1,64,64,3)

    # ------------------------------------------------
    # MOBILE PHOTO DETECTION (SCREEN vs REAL SKIN)
    # ------------------------------------------------
    def detect_mobile_photo(self, face_img):
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)

        # Skin has texture, phone screen is smooth
        texture_std = np.std(gray)

        if texture_std < 18:   # threshold (tune if needed)
            return True        # Mobile / printed photo
        return False           # Real face

    # ------------------------------------------------
    # FINAL LIVENESS CHECK
    # ------------------------------------------------
    def check_liveness_cnn(self, face_img):
        # Step 1: block mobile photo
        if self.detect_mobile_photo(face_img):
            return False

        # Step 2: CNN prediction
        pre = self.preprocess_face_for_liveness(face_img)
        pred = self.liveness_model.predict(pre, verbose=0)[0][0]

        return pred > 0.5

    # ------------------ COMMON ------------------
    def clear_screen(self):
        self.canvas.delete("all")
        for w in self.root.place_slaves():
            w.destroy()

    def draw_bg(self):
        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")

    def stop_camera(self):
        self.cam_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        if hasattr(self, "after_id"):
            self.root.after_cancel(self.after_id)

    # ------------------ CARD ------------------
    def screen_card(self):
        self.stop_camera()
        self.clear_screen()
        self.draw_bg()

        ff=open("unknown_face.txt","w")
        ff.write("0-0-0")
        ff.close()

        ff2=open("sm.txt","w")
        ff2.write("")
        ff2.close()

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Insert Card / Enter Card Number",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        self.card_entry = tk.Entry(self.root, font=("Arial", 20), width=20, justify="center")
        self.card_entry.place(x=self.CENTER_X - 170, y=self.SY1 + 120)
        self.show_msg("", "")
        tk.Button(
            self.root, text="ENTER",
            font=("Arial", 16, "bold"),
            width=12,
            command=self.card_entered
        ).place(x=self.CENTER_X - 100, y=self.SY1 + 200)

    def card_entered(self):
        card = self.card_entry.get().strip()
        if not card:
            messagebox.showerror("Error", "Enter card number")
            return

        # Check card in DB
        cur = self.db.cursor()
        cur.execute("SELECT id FROM register WHERE card=%s", (card,))
        result = cur.fetchone()
        if not result:
            messagebox.showerror("Error", "Card number not recognized")
            return

        self.user_id = result[0]
        self.card_number = card

        ff=open("facest.txt","w")
        ff.write("")
        ff.close()

        cur.execute("SELECT * FROM register WHERE card=%s", (card,))
        rr = cur.fetchone()
        rid=rr[0]
        name=rr[1]
        mobile=str(rr[3])
        mess="Someone Access ATM"
        dd=name+"|"+mobile+"|"+mess

        ff=open("facest_det.txt","w")
        ff.write(dd)
        ff.close()

        cur.execute("SELECT * FROM user_account WHERE rid=%s", (rid,))
        ds = cur.fetchall()
        vv=""
        for dv in ds:
            v1=str(dv[0])
            vv+=v1+"-"+dv[2]+","

        ff=open("bk_det.txt","w")
        ff.write(vv)
        ff.close()
            

        # Load all embeddings for this user
        #self.user_embeddings = self.load_user_embeddings(self.user_id)
        #if not self.user_embeddings:
        #    messagebox.showwarning("Warning", "No face images registered for this user!")

        self.screen_face()

    # ------------------ FACE ------------------
    '''def reset_liveness_state(self):
        self.blink_count = 0
        self.eye_closed = False
        self.blink_verified = False
        self.face_captured = False
        self.comparison_shown = False
        self.match_result = None'''

    def reset_liveness_state(self):
        self.blink_count = 0
        self.eye_closed = False
        self.face_captured = False
        self.verify_start_time = time.time()

        self.prev_eye_y = None
        self.last_blink_time = 0
        self.blink_verified = False
   
    def screen_face(self):
        self.clear_screen()
        self.draw_bg()

        self.cam_x = self.LEFT_X
        self.cam_y = (self.SY1 + self.SY2) // 2

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Face Verification",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        self.canvas.create_rectangle(
            self.cam_x - 120, self.cam_y - 120,
            self.cam_x + 120, self.cam_y + 120,
            outline="white", width=2
        )

        self.cam_image = self.canvas.create_image(self.cam_x, self.cam_y)

        self.status_text = self.canvas.create_text(
            self.RIGHT_X, self.cam_y,
            text="Looking for face...",
            font=("Arial", 18),
            fill="yellow"
        )

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.canvas.itemconfig(self.status_text, text="Camera Not Found", fill="red")
            return

        self.cam_running = True
        self.start_time = time.time()

        self.cap = cv2.VideoCapture(0)
        self.verify_start_time = time.time()
        self.reset_liveness_state()
        self.update_camera()

    # ------------------ FACE RECOGNITION ------------------
    def recognize_face(self, embedding):
        min_dist = 1.0
        recognized_name = None

        for name, db_emb in self.face_db.items():
            dist = np.linalg.norm(embedding - db_emb)
            if dist < 0.6 and dist < min_dist:
                min_dist = dist
                recognized_name = name

        if recognized_name:
            return recognized_name, min_dist
        return None

    # ------------------ CAMERA LOOP ------------------
    def draw_spider_lines(self, frame, kp):
        nose = kp['nose']
        points = [kp['left_eye'], kp['right_eye'],
                  kp['mouth_left'], kp['mouth_right']]

        for p in points:
            cv2.line(frame, nose, p, (0, 255, 255), 2)
            cv2.circle(frame, p, 4, (255, 0, 0), -1)

        cv2.circle(frame, nose, 4, (0, 0, 255), -1)

    def match_face(self, live_face):
        user_folder = f"dataset/user_{self.user_id}"

        if not os.path.exists(user_folder):
            return "Unknown", None, 999

        # ---- Live face embedding ----
        live_face = cv2.resize(live_face, (160, 160))
        live_emb = self.get_embedding(live_face)
        live_emb = live_emb / np.linalg.norm(live_emb)

        min_dist = 999
        matched_img = None

        for img_name in os.listdir(user_folder):
            img_path = os.path.join(user_folder, img_name)

            db_img = cv2.imread(img_path)
            if db_img is None:
                continue

            db_img = cv2.cvtColor(db_img, cv2.COLOR_BGR2RGB)
            db_img = cv2.resize(db_img, (160, 160))
            db_emb = self.get_embedding(db_img)
            db_emb = db_emb / np.linalg.norm(db_emb)

            sim = cosine_similarity([live_emb], [db_emb])[0][0]
            dist = 1 - sim

            if dist < min_dist:
                min_dist = dist
                matched_img = img_path

        # ---- THRESHOLD ----
        if min_dist < 0.35:
            self.face_verified = True
            return f"User {self.user_id}", matched_img, min_dist
        else:
            self.face_verified = False
            return "Unknown", matched_img, min_dist

    def safe_face_crop(self, frame, x, y, w, h, margin=0.35):
        H, W, _ = frame.shape

        mx = int(w * margin)
        my = int(h * margin)

        x1 = max(0, x - mx)
        y1 = max(0, y - my)
        x2 = min(W, x + w + mx)
        y2 = min(H, y + h + my)

        face = frame[y1:y2, x1:x2]

        return face

    def go_face_compare(self):
        # Use your existing match_face function or dummy values
        matched_name, db_face_path, distance = self.match_face(self.captured_face)
        self.show_face_match_screen(self.captured_face, db_face_path, distance)

    def detect_liveness_only(self, frame):
        """
        Returns:
            frame        : annotated frame
            is_real      : True / False
            face_box     : (x1, y1, x2, y2) or None
        """

        frame = imutils.resize(frame, width=800)
        (h, w) = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            1.0, (300, 300),
            (104.0, 177.0, 123.0)
        )

        self.detector_net.setInput(blob)
        detections = self.detector_net.forward()

        for i in range(detections.shape[2]):
            conf = detections[0, 0, i, 2]
            if conf < self.confidence_threshold:
                continue

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            startX, startY, endX, endY = box.astype(int)

            startX, startY = max(0, startX), max(0, startY)
            endX, endY = min(w, endX), min(h, endY)

            face = frame[startY:endY, startX:endX]
            if face.size == 0:
                continue

            # ---------- LIVENESS CNN ----------
            face_resized = cv2.resize(face, (32, 32))
            face_resized = face_resized.astype("float") / 255.0
            face_resized = tf.keras.preprocessing.image.img_to_array(face_resized)
            face_resized = np.expand_dims(face_resized, axis=0)

            preds = self.liveness_model.predict(face_resized, verbose=0)[0]
            j = np.argmax(preds)
            label = self.le.classes_[j]      # "real" or "fake"
            score = preds[j]

            # ---------- DRAW ----------
            color = (0, 255, 0) if label == "real" else (0, 0, 255)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            cv2.putText(
                frame, f"Liveness: {label} ({score:.2f})",
                (startX, startY - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
            )

            return frame, label == "real", (startX, startY, endX, endY)

        return frame, False, None

    def capture_face_and_embed(self):
       
        frame = self.current_frame  # already captured frame

        embedding = self.generate_embedding(frame)

        if embedding is None:
            self.show_msg("Face not detected", "red")
            return

        # Store 
        self.current_face_embedding = embedding

        print("Face embedding generated")
        print("Embedding shape:", embedding.shape)  # (128,)

        self.show_msg("Face captured successfully", "green")
    def update_camera(self):
        if not self.cam_running or self.cap is None:
            return

        # ---------- READ RAW FRAME ----------
        ret, raw_frame = self.cap.read()
        if not ret:
            self.root.after(30, self.update_camera)
            return

        display_frame = raw_frame.copy()  # Copy for drawing on display only

        # ---------- FACE DETECTION ----------
        rgb = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2RGB)
        faces = self.detector.detect_faces(rgb)

        if faces:
            # Use largest face if multiple
            face = sorted(faces, key=lambda f: f['box'][2]*f['box'][3], reverse=True)[0]
            x, y, w, h = face['box']
            kp = face['keypoints']

            # ---------- DRAW SPIDER LINES----------
            points = [kp['left_eye'], kp['right_eye'], kp['nose'], kp['mouth_left'], kp['mouth_right']]
            for i in range(len(points)):
                for j in range(i + 1, len(points)):
                    cv2.line(display_frame, points[i], points[j], (0, 255, 255), 2)
            for p in points:
                cv2.circle(display_frame, p, 4, (0, 0, 255), -1)

            # ---------- BLINK CHECK ----------
            eyes_open_now = self.eyes_open(kp)  # Implement this to return True if eyes open

            if getattr(self, "prev_eyes_open", True) and not eyes_open_now:
                self.blink_count = getattr(self, "blink_count", 0) + 1
                self.show_msg(f"Blink count: {self.blink_count}/2", "yellow")

            self.prev_eyes_open = eyes_open_now

            self.blink_done = getattr(self, "blink_done", False)
            if getattr(self, "blink_count", 0) >= 2:
                self.blink_done = True

            # ---------- AFTER 2 BLINKS → LIVENESS ----------
            if self.blink_done and not getattr(self, "face_captured", False):
                display_frame, is_real, box = self.detect_liveness_only(display_frame)

                if is_real and box:
                    startX, startY, endX, endY = box

                    # ---------- CAPTURE EXACT FACE WITH PADDING ----------
                    pad_w = int(0.25 * w)
                    pad_h = int(0.35 * h)
                    h_img, w_img = raw_frame.shape[:2]
                    x1, y1 = max(0, x - pad_w), max(0, y - pad_h)
                    x2, y2 = min(w_img, x + w + pad_w), min(h_img, y + h + pad_h)
                    clean_face = raw_frame[y1:y2, x1:x2].copy()

                    # Save captured face
                    cv2.imwrite("test_capture.jpg", clean_face)
                    cv2.imwrite("static/test_capture.jpg", clean_face)

                    self.face_captured = True
                    self.face_capture_time = time.time()
                    self.show_msg("Real face verified", "green")

                    # ---------- FACE MATCH ----------
                    match_percent, is_match = self.recognize_face("test_capture.jpg")

                    self.cam_running = False
                    self.stop_camera()

                    # Load DB face path safely if not already loaded
                    if not hasattr(self, 'db_face_path') or self.db_face_path is None:
                        try:
                            cur = self.db.cursor()
                            cur.execute("SELECT fimg FROM register WHERE id=%s", (self.user_id,))
                            row = cur.fetchone()
                            self.db_face_path = f"dataset/user{self.user_id}/{row[0]}" if row else None
                        except:
                            self.db_face_path = None

                    
                    self.show_face_match_screen(match_percent, is_match)
                    return

                elif not is_real:
                    self.show_msg("Fake face detected! Access denied.", "red")

        else:
            self.show_msg("No face detected. Please look at camera & blink twice", "white")

        # ---------- DISPLAY CAMERA ----------
        cam_view = cv2.resize(display_frame, (240, 240))
        cam_view = cv2.cvtColor(cam_view, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(cam_view))

        self.canvas.itemconfig(self.cam_image, image=img)
        self.canvas.image = img

        # ---------- REPEAT ----------
        if self.cam_running:
            self.root.after(30, self.update_camera)



    

    '''def update_camera(self):
        if not self.cam_running or self.cap is None:
            return

        # ---------- RAW CAMERA FRAME ----------
        ret, raw_frame = self.cap.read()
        if not ret:
            self.root.after(30, self.update_camera)
            return

        # ---------- COPY FOR DISPLAY ----------
        display_frame = raw_frame.copy()

        # ---------- FACE DETECTION ----------
        rgb = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2RGB)
        faces = self.detector.detect_faces(rgb)

        if faces:
            face = faces[0]
            x, y, w, h = face['box']
            kp = face['keypoints']

            # ---------- DRAW SPIDER LINES ON DISPLAY ONLY ----------
            le, re, nose, ml, mr = kp['left_eye'], kp['right_eye'], kp['nose'], kp['mouth_left'], kp['mouth_right']
            for p1, p2 in [(le, re), (le, nose), (re, nose), (nose, ml), (nose, mr), (ml, mr)]:
                cv2.line(display_frame, p1, p2, (0, 255, 255), 2)
            for p in [le, re, nose, ml, mr]:
                cv2.circle(display_frame, p, 4, (0, 0, 255), -1)

            # ---------- FACE ROI ----------
            pad = int(0.25 * max(w, h))
            h_img, w_img = raw_frame.shape[:2]
            x1, y1 = max(0, x - pad), max(0, y - pad)
            x2, y2 = min(w_img, x + w + pad), min(h_img, y + h + pad)

            # ---------- LIVENESS CHECK ----------
            display_frame, is_real, box_detected = self.detect_liveness_only(display_frame)

            if is_real and box_detected:
                # Only capture once
                if not self.face_captured:
                    self.captured_face = raw_frame[y1:y2, x1:x2].copy()
                    self.face_captured = True
                    self.face_capture_time = time.time()
                    cv2.imwrite("test_capture.jpg", self.captured_face)
                    self.show_msg("Real face detected & captured", "green")

            elif not is_real and box_detected:
                self.show_msg("Fake face detected! Access denied.", "red")

        # ---------- CHECK IF READY TO MOVE TO NEXT SCREEN ----------
        if self.face_captured and time.time() - self.face_capture_time >= 2:
            self.cam_running = False
            self.stop_camera()

            # Load DB face path safely if not already loaded
            if not hasattr(self, 'db_face_path') or self.db_face_path is None:
                try:
                    cur = self.db.cursor()
                    cur.execute("SELECT fimg FROM register WHERE id=%s", (self.user_id,))
                    row = cur.fetchone()
                    self.db_face_path = f"dataset/user{self.user_id}/{row[0]}" if row else None
                except:
                    self.db_face_path = None

            # Show match screen (distance 0.0 for now)
            self.show_face_match_screen(self.captured_face, self.db_face_path, 0.0)
            self.root.after(10000, self.screen_menu)
            return

        # ---------- DISPLAY CAMERA ----------
        cam_view = cv2.resize(display_frame, (240, 240))
        cam_view_rgb = cv2.cvtColor(cam_view, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(cam_view_rgb))
        self.canvas.itemconfig(self.cam_image, image=img)
        self.canvas.image = img

        if self.cam_running:
            self.root.after(30, self.update_camera)'''

    
    '''def update_camera(self):
        if not self.cam_running or self.cap is None:
            return

        # ---------- READ RAW CAMERA FRAME (BGR) ----------
        ret, frame = self.cap.read()
        if not ret:
            self.show_msg("Camera Error", "red")
            self.root.after(100, self.update_camera)
            return

        # ---------- COPY FOR DRAWING / PROCESSING ----------
        display_frame = frame.copy()

        # ---------- LIVENESS CHECK (NO COLOR CHANGE) ----------
        display_frame, is_real, box = self.detect_liveness_only(display_frame)

        # ---------- SPIDER LINES (MTCNN KEYPOINTS) ----------
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = self.detector.detect_faces(rgb)

            if faces:
                kp = faces[0]['keypoints']
                le, re = kp['left_eye'], kp['right_eye']
                nose = kp['nose']
                ml, mr = kp['mouth_left'], kp['mouth_right']

                for p1, p2 in [(le, re), (le, nose), (re, nose),
                               (nose, ml), (nose, mr), (ml, mr)]:
                    cv2.line(display_frame, p1, p2, (0, 255, 255), 2)

                for p in [le, re, nose, ml, mr]:
                    cv2.circle(display_frame, p, 4, (0, 0, 255), -1)
        except:
            pass

        # ---------- CAPTURE LIVE FACE (FROM RAW FRAME ONLY) ----------
        if is_real and box and not self.face_captured:
            x1, y1, x2, y2 = box

            pad = int(0.25 * max(x2 - x1, y2 - y1))
            h, w = frame.shape[:2]

            x1 = max(0, x1 - pad)
            y1 = max(0, y1 - pad)
            x2 = min(w, x2 + pad)
            y2 = min(h, y2 + pad)

            #  CRITICAL FIX: capture from RAW frame
            self.captured_face = frame[y1:y2, x1:x2].copy()
            self.face_capture_time = time.time()
            self.face_captured = True
            cv2.imwrite("test_capture.jpg", self.captured_face)

            # ---------- LOAD TRAINED FACE FROM DB ----------
            try:
                cur = self.db.cursor()
                cur.execute("SELECT fimg FROM register WHERE id=%s", (self.user_id,))
                row = cur.fetchone()
                self.db_face_path = f"dataset/user{self.user_id}/{row[0]}" if row else None
            except:
                self.db_face_path = None

            self.show_msg("Face Captured", "green")

        # ---------- MOVE TO FACE MATCH SCREEN (CONTROLLED) ----------
        if self.face_captured and hasattr(self, "db_face_path"):
            if time.time() - self.face_capture_time >= 2:
                self.cam_running = False
                self.stop_camera()

                self.show_face_match_screen(
                    self.captured_face,
                    self.db_face_path,
                    0.0
                )

                self.root.after(10000, self.screen_menu)
                return

        # ---------- DISPLAY CAMERA (NO COLOR DISTORTION) ----------
        cam_view = cv2.resize(display_frame, (240, 240))
        cam_view_rgb = cv2.cvtColor(cam_view, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(cam_view_rgb))

        self.canvas.itemconfig(self.cam_image, image=img)
        self.canvas.image = img

        if self.cam_running:
            self.root.after(30, self.update_camera)'''


    ###################
    '''def update_camera(self):
        if not self.cam_running or self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.show_msg("Camera Error", "red")
            self.root.after(100, self.update_camera)
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.detector.detect_faces(rgb)

        if faces:
            face = faces[0]
            x, y, w, h = face['box']
            kp = face['keypoints']

            # ---------- SPIDER LINES ----------
            le, re, nose, ml, mr = kp['left_eye'], kp['right_eye'], kp['nose'], kp['mouth_left'], kp['mouth_right']
            for p1, p2 in [(le, re), (le, nose), (re, nose), (nose, ml), (nose, mr), (ml, mr)]:
                cv2.line(frame, p1, p2, (0, 255, 255), 2)
            for p in [le, re, nose, ml, mr]:
                cv2.circle(frame, p, 5, (0, 0, 255), -1)

            # ---------- FACE REGION ----------
            pad = int(0.3 * max(w, h))
            h_img, w_img = rgb.shape[:2]
            x1, y1 = max(0, x - pad), max(0, y - pad)
            x2, y2 = min(w_img, x + w + pad), min(h_img, y + h + pad)
            face_img = rgb[y1:y2, x1:x2]

           
            if self.face_captured:
                # Wait at least 2 seconds to show comparison
                if time.time() - self.face_capture_time >= 2:
                    # Load DB face safely
                    try:
                        cur = self.db.cursor()
                        cur.execute("SELECT fimg FROM register WHERE id=%s", (self.user_id,))
                        row = cur.fetchone()
                        db_face_path = f"dataset/user{self.user_id}/{row[0]}" if row else None
                    except:
                        db_face_path = None

                    distance = 0.4  # placeholder
                    self.face_captured = False  # stop repeating
                    if db_face_path and os.path.exists(db_face_path):
                        self.show_face_match_screen(self.captured_face, db_face_path, distance)
                    else:
                        self.show_msg("Registered image not found", "red")
                    self.cam_running = False
                    self.stop_camera()
                    # Go to menu or approval after 10 seconds
                    self.root.after(10000, self.screen_menu)

        # ---------- DISPLAY CAMERA ----------
        display = cv2.resize(frame, (240, 240))
        img = ImageTk.PhotoImage(Image.fromarray(display))
        self.canvas.itemconfig(self.cam_image, image=img)
        self.canvas.image = img

        if self.cam_running:
            self.root.after(30, self.update_camera)'''


    def get_camera_window(self, frame, size=120):
        h, w = frame.shape[:2]

        cx = w // 2
        cy = h // 2

        x1 = max(0, cx - size)
        y1 = max(0, cy - size)
        x2 = min(w, cx + size)
        y2 = min(h, cy + size)

        return frame[y1:y2, x1:x2]

    '''def update_camera(self):
        if not self.cam_running or self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.after_id = self.root.after(30, self.update_camera)
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        display_frame = rgb.copy()

        faces = self.detector.detect_faces(rgb)

        if faces:
            face = faces[0]
            x, y, w, h = face['box']
            kp = face['keypoints']

            # ------------------ SPIDER LINES ------------------
            le, re = kp['left_eye'], kp['right_eye']
            nose = kp['nose']
            ml, mr = kp['mouth_left'], kp['mouth_right']

            line_pairs = [
                (le, re), (le, nose), (re, nose),
                (nose, ml), (nose, mr), (ml, mr)
            ]
            for p1, p2 in line_pairs:
                cv2.line(display_frame, p1, p2, (0, 255, 255), 2)
            for p in [le, re, nose, ml, mr]:
                cv2.circle(display_frame, p, 5, (0, 0, 255), -1)

            # ------------------ EYE BLINK CHECK ------------------
            blink_now = self.check_eye_blink(kp)  # increments self.blink_count properly
            self.show_msg(f"Blink Count: {self.blink_count}", "yellow")

            # Once enough blinks detected → mark verified
            if self.blink_count >= 2 and not getattr(self, 'blink_verified', False):
                self.blink_verified = True
                self.show_msg("Blink Verified! Hold still...", "lightgreen")
                self.capture_time = time.time()

                # Capture face
                pad = int(0.3 * max(w, h))
                h_img, w_img = rgb.shape[:2]
                x1, y1 = max(0, x - pad), max(0, y - pad)
                x2, y2 = min(w_img, x + w + pad), min(h_img, y + h + pad)
                face_img = rgb[y1:y2, x1:x2]
                if face_img.size != 0:
                    face_resized = cv2.resize(face_img, (160, 160))
                    self.captured_face = face_resized.astype("float32") / 255.0
                    self.face_captured = True

            # ------------------ FACE MATCH ------------------
            if getattr(self, 'face_captured', False) and getattr(self, 'blink_verified', False) \
                    and (time.time() - self.capture_time) >= 3 and not getattr(self, 'comparison_shown', False):

                cur = self.db.cursor()
                cur.execute("SELECT fimg FROM register WHERE id=%s", (self.user_id,))
                row = cur.fetchone()
                db_face_path = f"dataset/user{self.user_id}/{row[0]}" if row else None

                if db_face_path and os.path.exists(db_face_path):
                    db_img = cv2.imread(db_face_path)
                    db_img = cv2.cvtColor(db_img, cv2.COLOR_BGR2RGB)
                    db_img_resized = cv2.resize(db_img, (160, 160)).astype("float32") / 255.0
                    emb_live = self.embedder.embeddings([self.captured_face])[0]
                    emb_db = self.embedder.embeddings([db_img_resized])[0]
                    distance = np.linalg.norm(emb_live - emb_db)
                else:
                    distance = 1.0

                self.show_face_match_screen(self.captured_face, db_face_path, distance)
                self.comparison_shown = True

                # After 5s → menu or owner approval
                if distance < 0.6:
                    self.root.after(5000, self.screen_menu)
                else:
                    self.root.after(5000, self.process_face_result)

                self.stop_camera()
                return

        else:
            self.show_msg("Looking for face...", "yellow")
            # Reset blink if no face
            self.prev_eye_y = None
            self.eye_closed = False

        # ------------------ DISPLAY CAMERA ------------------
        frame_disp = cv2.resize(display_frame, (self.cam_width, self.cam_height))
        img = Image.fromarray(frame_disp)
        imgtk = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.cam_image, image=imgtk)
        self.canvas.image = imgtk

        self.after_id = self.root.after(30, self.update_camera)'''


    
    '''def update_camera(self):
        if not self.cam_running or self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.after_id = self.root.after(30, self.update_camera)
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        display_frame = rgb.copy()

        faces = self.detector.detect_faces(rgb)

        if faces:
            face = faces[0]
            x, y, w, h = face['box']
            kp = face['keypoints']

            # ---------- SPIDER LINES ----------
            le, re, nose, ml, mr = kp['left_eye'], kp['right_eye'], kp['nose'], kp['mouth_left'], kp['mouth_right']
            for p1, p2 in [(le, re), (le, nose), (re, nose), (nose, ml), (nose, mr), (ml, mr)]:
                cv2.line(display_frame, p1, p2, (0, 255, 255), 2)
            for p in [le, re, nose, ml, mr]:
                cv2.circle(display_frame, p, 5, (0, 0, 255), -1)

            # ---------- EYE BLINK ----------
            blink_ok = self.check_eye_blink(kp)
            if blink_ok and not hasattr(self, 'blink_verified'):
                self.show_msg("Blink Verified. Hold Still", "lightgreen")
                self.blink_verified = True
                self.capture_time = time.time()
                # Capture face after blink
                pad = int(0.3 * max(w, h))
                h_img, w_img = rgb.shape[:2]
                x1, y1 = max(0, x - pad), max(0, y - pad)
                x2, y2 = min(w_img, x + w + pad), min(h_img, y + h + pad)
                face_img = rgb[y1:y2, x1:x2]
                face_resized = cv2.resize(face_img, (160, 160))
                self.captured_face = face_resized.astype("float32") / 255.0
                self.face_captured = True

            # ---------- FACE MATCH SCREEN ----------
            if self.face_captured and self.blink_verified and (time.time() - self.capture_time) >= 3 and not hasattr(self, 'comparison_shown'):
                cur = self.db.cursor()
                cur.execute("SELECT fimg FROM register WHERE id=%s", (self.user_id,))
                row = cur.fetchone()
                db_face_path = f"dataset/user{self.user_id}/{row[0]}" if row else None

                # Compute embedding distance
                if db_face_path and os.path.exists(db_face_path):
                    db_img = cv2.imread(db_face_path)
                    db_img = cv2.cvtColor(db_img, cv2.COLOR_BGR2RGB)
                    db_img_resized = cv2.resize(db_img, (160, 160)).astype("float32") / 255.0
                    emb_live = self.embedder.embeddings([self.captured_face])[0]
                    emb_db = self.embedder.embeddings([db_img_resized])[0]
                    distance = np.linalg.norm(emb_live - emb_db)
                else:
                    distance = 1.0

                self.show_face_match_screen(self.captured_face, db_face_path, distance)
                self.comparison_shown = True
                self.root.after(5000, self.screen_menu if distance < 0.6 else self.process_face_result)
                self.stop_camera()
                return

        else:
            self.show_msg("Looking for face...", "yellow")

        # ---------- DISPLAY CAMERA ----------
        frame_disp = cv2.resize(display_frame, (self.cam_width, self.cam_height))
        img = Image.fromarray(frame_disp)
        imgtk = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.cam_image, image=imgtk)
        self.canvas.image = imgtk

        self.after_id = self.root.after(30, self.update_camera)'''

    #def clear_window(self):
    #    self.canvas.delete("all")
        
    # ---------------- HELPER FUNCTION TO SHOW FACE COMPARISON ----------------
    def recognize_face(self, image_path):
        TRAINER_PATH = "trainer/trainer.yml"
        CASCADE_PATH = "haarcascade_frontalface_default.xml"

        if not os.path.exists(TRAINER_PATH):
            return 0, False

        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        if len(faces) == 0:
            return 0, False

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(TRAINER_PATH)

        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]

        _, confidence = recognizer.predict(face_roi)

        match_percent = max(0, min(100, 100 - confidence))
        is_match = match_percent >= 50   # YOUR RULE

        return match_percent, is_match

    def show_face_match_screen(self, match_percent, is_match):
        # ---------- CLEAR + BACKGROUND ----------
        self.clear_screen()
        self.draw_bg()   # IMPORTANT: background restore

        # ---------- TITLE ----------
        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Face Verification",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        # ---------- LOAD LIVE FACE ----------
        try:
            live_img = Image.open("static/test_capture.jpg").convert("RGB")
        except:
            live_img = Image.new("RGB", (200, 200), (80, 80, 80))
        live_img = live_img.resize((200, 200))
        live_tk = ImageTk.PhotoImage(live_img)

        self.canvas.create_image(
            self.LEFT_X,
            (self.SY1 + self.SY2) // 2,
            image=live_tk
        )
        self.canvas.image_live = live_tk

        # ---------- LOAD TRAINED FACE ----------
        try:
            if self.db_face_path and os.path.exists(self.db_face_path):
                db_img = Image.open(self.db_face_path).convert("RGB")
            else:
                raise FileNotFoundError
        except:
            db_img = Image.new("RGB", (200, 200), (80, 80, 80))

        db_img = db_img.resize((200, 200))
        db_tk = ImageTk.PhotoImage(db_img)

        self.canvas.create_image(
            self.RIGHT_X,
            (self.SY1 + self.SY2) // 2,
            image=db_tk
        )
        self.canvas.image_db = db_tk

        # ---------- LABELS ----------
        self.canvas.create_text(
            self.LEFT_X,
            (self.SY1 + self.SY2) // 2 + 130,
            text="Live Capture",
            fill="yellow",
            font=("Arial", 16)
        )

        self.canvas.create_text(
            self.RIGHT_X,
            (self.SY1 + self.SY2) // 2 + 130,
            text="Registered",
            fill="yellow",
            font=("Arial", 16)
        )

        # ---------- SIMILARITY ----------
        '''self.canvas.create_text(
            self.CENTER_X,
            self.SY1 + 230,
            text=f"Similarity: {match_percent:.2f} %",
            font=("Arial", 20, "bold"),
            fill="lime" if is_match else "red"
        )'''

        # ---------- RESULT LOGIC ----------
        if is_match:
            result_text = "FACE MATCHED"
            result_color = "lime"

            self.canvas.create_text(
                self.CENTER_X, self.SY1 + 280,
                text=result_text,
                font=("Arial", 20, "bold"),
                fill=result_color
            )

            # Go to main menu after short delay
            self.root.after(7000, self.screen_menu)

        else:
            result_text = "UNKNOWN PERSON"
            result_color = "red"

            # write facest = no
            ff2=open("sm.txt","w")
            ff2.write("1")
            ff2.close()
            with open("facest.txt", "w") as f:
                f.write("no")

            self.canvas.create_text(
                self.CENTER_X, self.SY1 + 300,
                text=result_text,
                font=("Arial", 20, "bold"),
                fill=result_color
            )

            # Go to owner approval
            self.root.after(7000, self.screen_wait_approval)


    '''def show_face_match_screen(self, match_percent, is_match):
        self.clear_screen()
        self.draw_bg()

        center_y = (self.SY1 + self.SY2) // 2

        # ---------- TITLE ----------
        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Face Verification Result",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        # ---------- LIVE FACE ----------
        live_img = Image.open("test_capture.jpg").convert("RGB").resize((200, 200))
        live_tk = ImageTk.PhotoImage(live_img)
        self.canvas.create_image(self.LEFT_X, center_y, image=live_tk)
        self.canvas.image_live = live_tk

        # ---------- RESULT ----------
        if is_match:
            result = "FACE MATCHED"
            color = "lime"
            status = "Correct User"
        else:
            result = "FACE NOT MATCHED"
            color = "red"
            status = "Unknown Person"

            with open("facest.txt", "w") as f:
                f.write("no")

        self.canvas.create_text(
            self.CENTER_X,
            self.SY1 + 220,
            text=result,
            font=("Arial", 22, "bold"),
            fill=color
        )

       
        self.canvas.create_text(
            self.CENTER_X,
            self.SY1 + 300,
            text=status,
            font=("Arial", 20, "bold"),
            fill=color
        )'''

    
    '''def show_face_match_screen(self,live_face, db_face_path, distance):
        self.clear_screen()
        self.draw_bg()
        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Face Comparison",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        # =====================================
        # LIVE FACE (LOAD FROM SAVED FILE)
        # =====================================
        try:
            live_img = Image.open("test_capture.jpg").convert("RGB")
            live_img = live_img.resize((200, 200))
        except:
            live_img = Image.new("RGB", (200, 200), (80, 80, 80))

        live_tk = ImageTk.PhotoImage(live_img)
        self.canvas.create_image(
            self.LEFT_X,
            (self.SY1 + self.SY2) // 2,
            image=live_tk
        )
        self.canvas.image_live = live_tk

        # =====================================
        # DB FACE
        # =====================================
        try:
            if db_face_path and os.path.exists(db_face_path):
                db_img = Image.open(db_face_path).convert("RGB")
            else:
                raise FileNotFoundError
            db_img = db_img.resize((200, 200))
        except:
            db_img = Image.new("RGB", (200, 200), (80, 80, 80))

        db_tk = ImageTk.PhotoImage(db_img)
        self.canvas.create_image(
            self.RIGHT_X,
            (self.SY1 + self.SY2) // 2,
            image=db_tk
        )
        self.canvas.image_db = db_tk

        # =====================================
        # LABELS
        # =====================================
        self.canvas.create_text(
            self.LEFT_X,
            (self.SY1 + self.SY2) // 2 + 120,
            text="Live Capture",
            fill="yellow",
            font=("Arial", 16)
        )

        self.canvas.create_text(
            self.RIGHT_X,
            (self.SY1 + self.SY2) // 2 + 120,
            text="Registered",
            fill="yellow",
            font=("Arial", 16)
        )

        # =====================================
        # SIMILARITY DISPLAY (PLACEHOLDER)
        # =====================================
        self.canvas.create_text(
            self.CENTER_X,
            self.SY1 + 220,
            text=f"Similarity: {100 - int(distance * 100)}%",
            font=("Arial", 18, "bold"),
            fill="lime"
        )
        #import cv2, os
        #from PIL import Image, ImageTk
        #import tkinter as tk

        # ---------------- PATHS ----------------
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        IMAGE_PATH = os.path.join(BASE_DIR, "test_capture.jpg")
        TRAINER_PATH = os.path.join(BASE_DIR, "trainer", "trainer.yml")
        CASCADE_PATH = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")

        # ---------------- UI ----------------
        #self.clear_window()
        

        title = tk.Label(self.root, text="Face Match Result",
                         font=("Arial", 26, "bold"), fg="white", bg="black")
        title.pack(fill="x")

        # ---------------- CHECK FILES ----------------
        if not os.path.exists(IMAGE_PATH):
            tk.Label(self.root, text="Captured image not found",
                     font=("Arial", 18), fg="red").pack(pady=30)
            return

        if not os.path.exists(TRAINER_PATH):
            tk.Label(self.root, text="trainer.yml missing",
                     font=("Arial", 18), fg="red").pack(pady=30)
            return

        # ---------------- LOAD IMAGE ----------------
        image = cv2.imread(IMAGE_PATH)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # ---------------- FACE DETECT ----------------
        face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        if len(faces) == 0:
            tk.Label(self.root, text="No face detected",
                     font=("Arial", 18), fg="red").pack(pady=30)
            return

        # ---------------- LOAD LBPH ----------------
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(TRAINER_PATH)

        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]

        # ---------------- PREDICT ----------------
        label_id, confidence = recognizer.predict(face_roi)

        # Convert LBPH confidence to %
        match_percent = round(max(0, min(100, 100 - confidence)), 2)

        # ---------------- RESULT ----------------
        if match_percent >= 50:
            result_text = "FACE MATCHED"
            result_color = "green"
            user_status = "Correct User"
        else:
            result_text = "FACE NOT MATCHED"
            result_color = "red"
            user_status = "Unknown Person"

            #
            ff=open("facest.txt","w")
            ff.write("no")
            ff.close()
            
            

        # ---------------- DISPLAY IMAGE ----------------
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        img = img.resize((350, 350))
        imgtk = ImageTk.PhotoImage(img)

        panel = tk.Label(self.root, image=imgtk)
        panel.image = imgtk
        panel.pack(pady=20)

        # ---------------- DISPLAY TEXT ----------------
        tk.Label(self.root, text=result_text,
                 font=("Arial", 22, "bold"),
                 fg=result_color).pack(pady=10)

        tk.Label(self.root, text=f"Similarity: {match_percent} %",
                 font=("Arial", 18)).pack(pady=5)

        tk.Label(self.root, text=f"Status: {user_status}",
                 font=("Arial", 18, "bold")).pack(pady=5)'''
    ####################################

    '''def show_face_match_screen(self, live_face, db_face_path, distance):
        self.clear_screen()
        self.draw_bg()

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Face Comparison",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        # =====================================
        # LIVE FACE (LOAD FROM SAVED FILE)
        # =====================================
        try:
            live_img = Image.open("test_capture.jpg").convert("RGB")
            live_img = live_img.resize((200, 200))
        except:
            live_img = Image.new("RGB", (200, 200), (80, 80, 80))

        live_tk = ImageTk.PhotoImage(live_img)
        self.canvas.create_image(
            self.LEFT_X,
            (self.SY1 + self.SY2) // 2,
            image=live_tk
        )
        self.canvas.image_live = live_tk

        # =====================================
        # DB FACE
        # =====================================
        try:
            if db_face_path and os.path.exists(db_face_path):
                db_img = Image.open(db_face_path).convert("RGB")
            else:
                raise FileNotFoundError
            db_img = db_img.resize((200, 200))
        except:
            db_img = Image.new("RGB", (200, 200), (80, 80, 80))

        db_tk = ImageTk.PhotoImage(db_img)
        self.canvas.create_image(
            self.RIGHT_X,
            (self.SY1 + self.SY2) // 2,
            image=db_tk
        )
        self.canvas.image_db = db_tk

        # =====================================
        # LABELS
        # =====================================
        self.canvas.create_text(
            self.LEFT_X,
            (self.SY1 + self.SY2) // 2 + 120,
            text="Live Capture",
            fill="yellow",
            font=("Arial", 16)
        )

        self.canvas.create_text(
            self.RIGHT_X,
            (self.SY1 + self.SY2) // 2 + 120,
            text="Registered",
            fill="yellow",
            font=("Arial", 16)
        )

        # =====================================
        # SIMILARITY DISPLAY (PLACEHOLDER)
        # =====================================
        self.canvas.create_text(
            self.CENTER_X,
            self.SY1 + 220,
            text=f"Similarity: {100 - int(distance * 100)}%",
            font=("Arial", 18, "bold"),
            fill="lime"
        )'''

    '''def show_face_match_screen(self, live_face, db_face_path, distance):
        self.clear_screen()
        self.draw_bg()

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Face Comparison",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        # Live face
        live_img = (live_face * 255).astype(np.uint8)
        live_img = Image.fromarray(live_img)
        live_img = live_img.resize((200, 200))
        live_tk = ImageTk.PhotoImage(live_img)
        self.canvas.create_image(self.LEFT_X, (self.SY1 + self.SY2)//2, image=live_tk)
        self.canvas.image_live = live_tk

        self.canvas.create_text(
            self.LEFT_X, (self.SY1 + self.SY2)//2 + 120,
            text="Live Capture", fill="yellow", font=("Arial", 16)
        )

        # DB face
        db_img = Image.open(db_face_path).resize((200, 200))
        db_tk = ImageTk.PhotoImage(db_img)
        self.canvas.create_image(self.RIGHT_X, (self.SY1 + self.SY2)//2, image=db_tk)
        self.canvas.image_db = db_tk

        self.canvas.create_text(
            self.RIGHT_X, (self.SY1 + self.SY2)//2 + 120,
            text="Registered", fill="yellow", font=("Arial", 16)
        )

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 220,
            text=f"Cosine Similarity: {100-int(distance*100)}%",
            font=("Arial", 18, "bold"),
            fill="lime"
        )'''

    

    '''def show_face_match_screen(self, live_face, db_face_path, distance):
        self.clear_screen()
        self.draw_bg()

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Face Comparison",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        # ---------- Live face ----------
        # live_face shape may be (1, H, W, 3) or (H, W, 3)
        if live_face.ndim == 4:
            live_face = live_face[0]

        live_img = (live_face * 255).astype(np.uint8)  # convert to uint8
        live_img = Image.fromarray(live_img)
        live_img = live_img.resize((200, 200))
        live_tk = ImageTk.PhotoImage(live_img)
        self.canvas.create_image(self.LEFT_X, (self.SY1 + self.SY2)//2, image=live_tk)
        self.canvas.image_live = live_tk

        # ---------- DB face ----------
        db_img = Image.open(db_face_path).resize((200, 200))
        db_tk = ImageTk.PhotoImage(db_img)
        self.canvas.create_image(self.RIGHT_X, (self.SY1 + self.SY2)//2, image=db_tk)
        self.canvas.image_db = db_tk

        self.canvas.create_text(
            self.LEFT_X, (self.SY1 + self.SY2)//2 + 120,
            text="Live Capture", fill="yellow", font=("Arial", 16)
        )

        self.canvas.create_text(
            self.RIGHT_X, (self.SY1 + self.SY2)//2 + 120,
            text="Registered", fill="yellow", font=("Arial", 16)
        )

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 220,
            text=f"Cosine Similarity: {100-int(distance*100)}%",
            font=("Arial", 18, "bold"),
            fill="lime"
        )'''




    def process_face_result(self):
        self.stop_camera()

        self.waiting_for_approval = True   # START WAITING

        self.canvas.itemconfig(
            self.status_text,
            text="Unknown Face Detected\nWaiting for Owner Approval",
            fill="red"
        )

        with open("unknown_face.txt", "w") as f:
            f.write("0-0-0")

        self.screen_wait_approval()

    # ---------------- WAITING FOR OWNER ----------------
    def screen_wait_approval(self):
        self.clear_screen()
        self.draw_bg()

        self.waiting_for_approval = True  # IMPORTANT

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Waiting for Owner Approval",
            font=("Arial", 28, "bold"),
            fill="yellow"
        )

        self.status_msg = self.canvas.create_text(
            self.CENTER_X, (self.SY1 + self.SY2)//2,
            text="Please wait while account owner approves...",
            font=("Arial", 22),
            fill="white"
        )

        tk.Button(
            self.root, text="EXIT",
            font=("Arial", 12, "bold"),
            width=10,
            command=self.exit_from_approval
        ).place(x=self.RIGHT_X - 60, y=self.SY2 - 100)

        # cancel any previous timer
        if hasattr(self, "approval_after_id"):
            self.root.after_cancel(self.approval_after_id)

        # start approval checking
        self.approval_after_id = self.root.after(
            1000, self.check_owner_approval
        )

    '''def screen_wait_approval(self):
        self.clear_screen()
        self.draw_bg()

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Waiting for Owner Approval",
            font=("Arial", 28, "bold"),
            fill="yellow"
        )

        self.status_msg = self.canvas.create_text(
            self.CENTER_X, (self.SY1 + self.SY2)//2,
            text="Please wait while account owner approves...",
            font=("Arial", 22),
            fill="white"
        )

       
        tk.Button(
            self.root, text="EXIT",
            font=("Arial", 12, "bold"),
            width=10,
            command=self.exit_from_approval
        ).place(x=self.RIGHT_X - 60, y=self.SY2 - 100)

        ff=open("unknown_face.txt","r")
        status=ff.read()
        ff.close()

        print("vv")
        print(status)
        
        # Check approval every 5 seconds
        self.root.after(5000, self.check_owner_approval)'''

    def exit_from_approval(self):
        self.waiting_for_approval = False
        self.clear_screen()
        self.draw_bg()
        self.screen_card()

    def check_owner_approval(self):

        # -------- STOP IF EXITED --------
        if not self.waiting_for_approval:
            if hasattr(self, "approval_after_id"):
                self.root.after_cancel(self.approval_after_id)
            return

        # -------- READ FILE --------
        try:
            with open("unknown_face.txt", "r") as f:
                status = f.read().strip()
        except Exception:
            status = ""

        print("OWNER STATUS:", status)

        # -------- ACCEPTED (NO AMOUNT YET) --------
        if status == "accepted" or status == "accepted-1-0":

            self.canvas.itemconfig(
                self.status_msg,
                text="Owner Approved\nWaiting for Cash..."
            )
            self.root.update_idletasks()

            self.approval_after_id = self.root.after(
                3000, self.check_owner_approval
            )
            return

        # -------- ACCEPTED WITH AMOUNT --------
        if status.startswith("accepted-"):
            parts = status.split("-")

            if len(parts) == 3:
                try:
                    amount = int(parts[1])
                    accid = int(parts[2])
                except ValueError:
                    amount = 0
                    accid = 0

                if amount > 0 and accid > 0:
                    self.waiting_for_approval = False
                    self.approved_amount = amount
                    self.approved_accid = accid

                    self.canvas.itemconfig(
                        self.status_msg,
                        text=f"Owner Approved\nCollect ₹ {amount}"
                    )
                    self.root.update_idletasks()

                    # clear file after use
                    open("unknown_face.txt", "w").close()

                    self.root.after(3000, self.withdraw_from_approval)
                    return

        # -------- REJECTED --------
        if status == "rejected":
            self.waiting_for_approval = False

            self.canvas.itemconfig(
                self.status_msg,
                text="Withdraw Rejected by Owner"
            )
            self.root.update_idletasks()

            open("unknown_face.txt", "w").close()

            self.root.after(3000, self.screen_card)
            return

        # -------- STILL WAITING --------
        self.canvas.itemconfig(
            self.status_msg,
            text="Please Wait...\nOwner Approval Pending"
        )
        self.root.update_idletasks()

        self.approval_after_id = self.root.after(
            3000, self.check_owner_approval
        )


    '''def check_owner_approval(self):
        
       
        status = "0-0-0"
        ff=open("unknown_face.txt","r")
        status=ff.read()
        ff.close()

        print("aa")
        print(status)
        # ---------------- APPROVED ----------------
        if status.startswith("accepted"):
            parts = status.split("-")
            print("accepted")
            if len(parts) == 3:
                amount = int(parts[1])
                accid = int(parts[2])

                # Approved but amount not entered yet
                if amount <= 0 or accid <= 0:
                    self.show_msg(
                        "Owner Approved\nWaiting for Amount...",
                        "limegreen"
                    )
                    self.root.after(5000, self.check_owner_approval)
                    return

                # Fully approved
                self.approved_amount = amount
                self.approved_accid = accid
                print("Amount")
                print(amount)

                self.show_msg(
                    f"Owner Approved!\nCollect ₹ {self.approved_amount}",
                    "green"
                )

                self.root.after(3000, self.withdraw_from_approval)
                return

        # ---------------- REJECTED ----------------
        elif status.startswith("rejected"):
            self.show_msg("Withdraw Rejected by Owner", "red")
            self.root.after(3000, self.screen_card)
            return

        # ---------------- STILL WAITING ----------------
        else:
            self.show_msg(
                "Please Wait...\nOwner Approval Pending",
                "yellow"
            )

        if not self.waiting_for_approval:
            return
        # Check again after 5 seconds
        self.root.after(5000, self.check_owner_approval)'''
    def withdraw_from_approval(self):
        import datetime

        amount = self.approved_amount

        cur = self.db.cursor()

        # -------- FETCH BALANCE --------
        cur.execute(
            "SELECT deposit FROM user_account WHERE id=%s",
            (self.approved_accid,)
        )
        row = cur.fetchone()

        if not row:
            self.show_msg("Account Not Found", "red")
            return

        balance = int(row[0])

        # -------- BALANCE CHECK --------
        if amount > balance:
            self.show_msg("Insufficient Balance", "red")
            return

        new_balance = balance - amount

        # -------- UPDATE BALANCE --------
        cur.execute(
            "UPDATE user_account SET deposit=%s WHERE id=%s",
            (new_balance, self.approved_accid)
        )
        self.db.commit()

        # -------- FETCH ACCOUNT DETAILS --------
        cur.execute(
            "SELECT * FROM user_account WHERE id=%s",
            (self.approved_accid,)
        )
        dat = cur.fetchone()
        account = dat[3]  # accno

        # -------- EVENT LOG --------
        now = datetime.datetime.now()
        rdd = now.strftime("%d-%m-%Y %H-%M-%S")

        cur.execute("SELECT MAX(id)+1 FROM event")
        maxid = cur.fetchone()[0]
        if maxid is None:
            maxid = 1

        sql = """
            INSERT INTO event(id, name, accno, amount, rdate, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        val = (
            maxid,
            "Withdraw",
            account,
            amount,
            rdd,
            self.user_id
        )

        cur.execute(sql, val)
        self.db.commit()

        # -------- FINAL UI --------
        self.show_msg(
            f"Please Collect Your Cash\n₹ {amount}",
            "limegreen"
        )

        # Go back to card screen after cash collection
        self.root.after(5000, self.screen_card)



    '''def withdraw_from_approval(self):
        self.clear_screen()
        self.draw_bg()
        self.show_msg(f"Please Collect Cash: ₹ {self.approved_amount}", "limegreen")

        
        self.root.after(15000, self.screen_card)'''
    # ------------------ MENU ------------------
    def screen_menu(self):
        self.clear_screen()
        self.draw_bg()

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Select Transaction",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        # LEFT SIDE
        tk.Button(self.root, text="Withdraw",
                  font=("Arial", 16, "bold"), width=18,
                  command=self.screen_select_bank_withdraw
        ).place(x=self.LEFT_X - 90, y=self.SY1 + 120)

        tk.Button(self.root, text="Fast Cash",
                  font=("Arial", 16, "bold"), width=18,
                  command=self.screen_select_bank_fastcash
        ).place(x=self.LEFT_X - 90, y=self.SY1 + 200)

        tk.Button(self.root, text="Deposit",
                  font=("Arial", 16, "bold"), width=18,
                  command=self.screen_select_bank_deposit
        ).place(x=self.LEFT_X - 90, y=self.SY1 + 280)

        # RIGHT SIDE
        tk.Button(self.root, text="Balance",
                  font=("Arial", 16, "bold"), width=18,
                  command=self.screen_select_bank_balance
        ).place(x=self.RIGHT_X - 110, y=self.SY1 + 120)

        tk.Button(self.root, text="Mini Statement",
                  font=("Arial", 16, "bold"), width=18,
                  command=self.screen_select_bank_statement
        ).place(x=self.RIGHT_X - 110, y=self.SY1 + 200)

        tk.Button(self.root, text="EXIT",
                  font=("Arial", 14), width=12,
                  command=self.screen_card
        ).place(x=self.CENTER_X - 60, y=self.SY2 - 120)

    def add_back_button(self):

        back_x = self.RIGHT_X - 40      # slightly inside blue area
        back_y = self.SY2 - 120          # bottom padding

        '''tk.Button(
            self.root,
            text="BACK",
            font=("Arial", 12, "bold"),
            width=10,
            command=self.screen_menu
        ).place(x=self.LEFT_X - 60, y=self.SY2 - 60)'''
        tk.Button(
            self.root,
            text="BACK",
            font=("Arial", 12, "bold"),
            width=10,
            bg="#0b3c5d",
            fg="white",
            activebackground="#145374",
            activeforeground="white",
            relief="raised",
            command=self.screen_menu   # or screen_card based on flow
        ).place(x=back_x, y=back_y)
        

    def screen_processing(self, amount):
        self.clear_screen()
        self.draw_bg()

        # Store amount temporarily
        self.processing_amount = amount

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 80,
            text="Processing Transaction",
            font=("Arial", 26, "bold"),
            fill="white"
        )

        self.canvas.create_text(
            self.CENTER_X, (self.SY1 + self.SY2)//2,
            text="Please wait...",
            font=("Arial", 20),
            fill="yellow"
        )

        # After 3 seconds → show collect cash
        self.root.after(3000, self.screen_collect_cash)

    def screen_collect_cash(self):
        self.clear_screen()
        self.draw_bg()

        amt = self.processing_amount

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 100,
            text="Please Collect Your Cash",
            font=("Arial", 28, "bold"),
            fill="lime"
        )

        self.canvas.create_text(
            self.CENTER_X, (self.SY1 + self.SY2)//2,
            text=f"₹ {amt}",
            font=("Arial", 40, "bold"),
            fill="white"
        )

        # After 5 seconds → return to card screen
        self.root.after(5000, self.screen_card)

    def screen_select_bank_withdraw(self):
        self.tx_type = "withdraw"
        self.screen_select_bank()
    def screen_select_bank_balance(self):
        self.tx_type = "balance"
        self.screen_select_bank()

    def screen_select_bank_deposit(self):
        self.tx_type = "deposit"
        self.screen_select_bank()
    
    def screen_select_bank(self):
        self.clear_screen()
        self.draw_bg()

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Select Bank",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        cur = self.db.cursor()
        cur.execute("""
            SELECT id, bank, account
            FROM user_account
            WHERE rid = %s
        """, (self.user_id,))

        accounts = cur.fetchall()

        if not accounts:
            self.show_msg("No Bank Accounts Found", "red")
            self.root.after(3000, self.screen_card)
            return

        y = self.SY1 + 120

        for acc_id, bank, accno in accounts:
            btn_text = f"{bank}\nA/C: {accno}"

            tk.Button(
                self.root,
                text=btn_text,
                font=("Arial", 14, "bold"),
                width=30,
                height=2,
                command=lambda a=acc_id: self.process_account(a)
            ).place(x=self.CENTER_X - 200, y=y)

            y += 90

        self.add_back_button()
            
    def screen_select_account(self, bank):
        self.clear_screen()
        self.draw_bg()
        self.selected_bank = bank

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text=f"{bank} - Select Account",
            font=("Arial", 24, "bold"),
            fill="white"
        )

        cur = self.db.cursor()
        cur.execute(
            "SELECT id, account, branch FROM user_account WHERE bank=%s",
            (bank,)
        )
        accounts = cur.fetchall()

        y = self.SY1 + 120
        for acc_id, acc_no, branch in accounts:
            tk.Button(
                self.root,
                text=f"A/C {acc_no} ({branch})",
                font=("Arial", 14),
                width=36,
                command=lambda a=acc_id: self.process_account(a)
            ).place(x=self.CENTER_X - 180, y=y)
            y += 60

    def process_account(self, acc_id):
        self.selected_account_id = acc_id

        if self.tx_type == "withdraw":
            self.screen_withdraw_amount()
        elif self.tx_type == "deposit":
            self.screen_deposit_amount()
        elif self.tx_type == "fastcash":
            self.screen_fast_cash()
        elif self.tx_type == "balance":
            self.show_balance()
        elif self.tx_type == "statement":
            self.screen_mini_statement()

    def show_balance(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT deposit
            FROM user_account
            WHERE id=%s AND rid=%s
        """, (self.selected_account_id, self.user_id))

        result = cur.fetchone()
        if not result:
            self.show_msg("Unauthorized Access", "red")
            return

        balance = result[0]
        self.show_msg(f"Available Balance\n₹ {balance}", "cyan")
        self.add_back_button()

    def screen_withdraw_amount(self):
        self.clear_screen()
        self.draw_bg()

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Enter Withdraw Amount",
            font=("Arial", 26, "bold"),
            fill="white"
        )

        self.amount_entry = tk.Entry(
            self.root, font=("Arial", 20), justify="center"
        )
        self.amount_entry.place(
            x=self.CENTER_X - 120, y=self.SY1 + 120, width=240
        )

        tk.Button(
            self.root, text="CONFIRM",
            font=("Arial", 16, "bold"),
            width=12,
            command=self.withdraw_confirm
        ).place(x=self.CENTER_X - 70, y=self.SY1 + 200)

        self.add_back_button()

    def withdraw_confirm(self):
        amount = int(self.amount_entry.get())

        cur = self.db.cursor()
        cur.execute(
            "SELECT deposit FROM user_account WHERE id=%s",
            (self.selected_account_id,)
        )
        balance = int(cur.fetchone()[0])

        if amount > balance:
            self.show_msg("Insufficient Balance", "red")
            return

        new_balance = balance - amount

        cur.execute(
            "UPDATE user_account SET deposit=%s WHERE id=%s",
            (new_balance, self.selected_account_id)
        )
        
        self.db.commit()

        cur.execute("SELECT * FROM user_account WHERE id=%s",(self.selected_account_id,))
        dat = cur.fetchone()
        account=dat[3]
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        rtime=now.strftime("%H-%M-%S")
        rdd=rdate+" "+rtime  
        cur.execute("SELECT max(id)+1 FROM event")
        maxid = cur.fetchone()[0]
        if maxid is None:
            maxid=1
        sql = "INSERT INTO event(id, name, accno, amount, rdate,user_id) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (maxid, "Withdraw", account, amount, rdd,self.user_id)
        cur.execute(sql, val)
        self.db.commit()

        #self.show_msg(f"Please Collect ₹ {amount}", "green")
        self.screen_processing(amount)
        #self.root.after(5000, self.screen_card)

    def screen_deposit_amount(self):
        self.clear_screen()
        self.draw_bg()

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Enter Deposit Amount",
            font=("Arial", 26, "bold"),
            fill="white"
        )

        self.deposit_entry = tk.Entry(
            self.root, font=("Arial", 20), justify="center"
        )
        self.deposit_entry.place(
            x=self.CENTER_X - 120, y=self.SY1 + 120, width=240
        )

        tk.Button(
            self.root, text="CONFIRM",
            font=("Arial", 16, "bold"),
            width=12,
            command=self.deposit_confirm
        ).place(x=self.CENTER_X - 70, y=self.SY1 + 200)

        self.add_back_button()

    def deposit_confirm(self):
        try:
            amount = int(self.deposit_entry.get())
            if amount <= 0:
                self.show_msg("Invalid Amount", "red")
                return
        except:
            self.show_msg("Enter Valid Amount", "red")
            return

        cur = self.db.cursor()

        # Get current balance
        cur.execute(
            "SELECT deposit FROM user_account WHERE id=%s",
            (self.selected_account_id,)
        )
        balance = int(cur.fetchone()[0])

        new_balance = balance + amount

        # Update balance
        cur.execute(
            "UPDATE user_account SET deposit=%s WHERE id=%s",
            (new_balance, self.selected_account_id)
        )
        self.db.commit()

        # Insert into event log
        cur.execute("SELECT * FROM user_account WHERE id=%s",
                    (self.selected_account_id,))
        dat = cur.fetchone()
        account = dat[3]

        import datetime
        now = datetime.datetime.now()
        rdate = now.strftime("%d-%m-%Y %H:%M:%S")

        cur.execute("SELECT max(id)+1 FROM event")
        maxid = cur.fetchone()[0]
        if maxid is None:
            maxid = 1

        sql = """INSERT INTO event(id, name, accno, amount, rdate, user_id)
                 VALUES (%s, %s, %s, %s, %s, %s)"""

        val = (maxid, "Deposit", account, amount, rdate, self.user_id)
        cur.execute(sql, val)
        self.db.commit()

        # Show processing screen
        self.screen_processing(amount)

    def screen_processing(self, amount):
        self.clear_screen()
        self.draw_bg()

        self.processing_amount = amount

        text_msg = "Processing Deposit" if self.tx_type == "deposit" else "Processing Transaction"

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 80,
            text=text_msg,
            font=("Arial", 26, "bold"),
            fill="white"
        )

        self.canvas.create_text(
            self.CENTER_X, (self.SY1 + self.SY2)//2,
            text="Please wait...",
            font=("Arial", 20),
            fill="yellow"
        )

        self.root.after(3000, self.screen_collect_cash if self.tx_type != "deposit" else self.screen_deposit_success)

    def screen_deposit_success(self):
        self.clear_screen()
        self.draw_bg()

        amt = self.processing_amount

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 100,
            text="Amount Deposited Successfully",
            font=("Arial", 28, "bold"),
            fill="lime"
        )

        self.canvas.create_text(
            self.CENTER_X, (self.SY1 + self.SY2)//2,
            text=f"₹ {amt}",
            font=("Arial", 40, "bold"),
            fill="white"
        )

        self.root.after(5000, self.screen_card)

        
    def screen_select_bank_fastcash(self):
        self.tx_type = "fastcash"
        self.screen_select_bank()

    def screen_select_bank_statement(self):
        self.tx_type = "statement"
        self.screen_select_bank()

    def screen_fast_cash(self):
        self.clear_screen()
        self.draw_bg()

        self.canvas.create_text(
            self.CENTER_X, self.SY1 + 40,
            text="Fast Cash",
            font=("Arial", 26, "bold"),
            fill="white"
        )

        amounts = [500, 1000, 2000, 5000]
        x_positions = [self.LEFT_X, self.RIGHT_X]

        y = self.SY1 + 130
        idx = 0
        for amt in amounts:
            tk.Button(
                self.root,
                text=f"₹ {amt}",
                font=("Arial", 16, "bold"),
                width=16,
                command=lambda a=amt: self.fast_cash_withdraw(a)
            ).place(x=x_positions[idx % 2] - 80, y=y)

            if idx % 2 == 1:
                y += 80
            idx += 1

        self.add_back_button()

    def fast_cash_withdraw(self, amount):
        cur = self.db.cursor()

        cur.execute(
            "SELECT deposit, account FROM user_account WHERE id=%s",
            (self.selected_account_id,)
        )
        balance, accno = cur.fetchone()

        if amount > int(balance):
            self.show_msg("Insufficient Balance", "red")
            return

        new_balance = int(balance) - amount

        cur.execute(
            "UPDATE user_account SET deposit=%s WHERE id=%s",
            (new_balance, self.selected_account_id)
        )

        # INSERT TRANSACTION
        cur.execute("SELECT * FROM user_account WHERE id=%s",(self.selected_account_id,))
        dat = cur.fetchone()
        account=dat[3]
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        rtime=now.strftime("%H-%M-%S")
        rdd=rdate+" "+rtime   
        cur.execute("SELECT max(id)+1 FROM event")
        maxid = cur.fetchone()[0]
        if maxid is None:
            maxid=1
        sql = "INSERT INTO event(id, name, accno, amount, rdate,user_id) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (maxid, "Withdraw", account, amount, rdd,self.user_id)
        cur.execute(sql, val)
        self.db.commit()

        #self.show_msg(f"Please Collect ₹ {amount}", "green")
        self.screen_processing(amount)
        #self.root.after(5000, self.screen_card)

    def screen_mini_statement(self):
        self.clear_screen()
        self.draw_bg()

        cur = self.db.cursor()
        cur.execute("""
            SELECT account
            FROM user_account
            WHERE id=%s AND rid=%s
        """, (self.selected_account_id, self.user_id))
        print("mini")
        print(self.selected_account_id)
        accno = cur.fetchone()[0]

        cur.execute("""
            SELECT name, amount, rdate
            FROM event
            WHERE accno=%s
            ORDER BY id DESC
            LIMIT 5
        """, (accno,))

        rows = cur.fetchall()

        heading_y = self.SY1 + 80   # move it down clearly

        self.canvas.create_text(
            self.CENTER_X,
            heading_y,
            text="MINI STATEMENT",
            font=("Arial", 26, "bold"),
            fill="white"
        )

        y = heading_y + 80

        self.canvas.create_text(
            self.CENTER_X,
            y,
            text="TYPE            AMOUNT           DATE",
            font=("Arial", 14, "bold"),
            fill="cyan"
        )

        y += 40
        for name, amt, date in rows:
            self.canvas.create_text(
                self.CENTER_X, y,
                text=f"       {name}            ₹{amt}           {date}",
                font=("Arial", 14),
                fill="white"
            )
            y += 35
        self.add_back_button()


    

    

# ------------------ START ------------------
if __name__ == "__main__":
    root = tk.Tk()
    ATM(root)
    root.mainloop()
