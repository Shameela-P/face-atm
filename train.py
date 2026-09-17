import os
import cv2
import numpy as np
import pickle
from mtcnn import MTCNN
from keras_facenet import FaceNet

detector = MTCNN()
embedder = FaceNet()

dataset_path = "dataset"
face_db = {}

for person in os.listdir(dataset_path):
    person_path = os.path.join(dataset_path, person)

    if not os.path.isdir(person_path):
        continue

    embeddings = []

    for img_name in os.listdir(person_path):
        img_path = os.path.join(person_path, img_name)

        img = cv2.imread(img_path)
        if img is None:
            continue

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = detector.detect_faces(rgb)

        if not faces:
            continue

        x, y, w, h = faces[0]['box']
        face = rgb[y:y+h, x:x+w]
        face = cv2.resize(face, (160, 160))

        emb = embedder.embeddings([face])[0]
        embeddings.append(emb)

    if embeddings:
        # Store AVERAGE embedding per person
        face_db[person] = np.mean(embeddings, axis=0)
        print(f"[OK] {person} registered")

with open("face_db.pkl", "wb") as f:
    pickle.dump(face_db, f)

print("Face embeddings saved (face_db.pkl)")
