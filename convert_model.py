import tensorflow as tf
import os

model_path = os.path.join("legacy", "facenet_keras.h5")
print(f"Loading {model_path} in Python 3.7...")
model = tf.keras.models.load_model(model_path, compile=False)
print("Loaded successfully. Saving as SavedModel...")
model.save(os.path.join("legacy", "facenet_savedmodel"))
print("Done!")
