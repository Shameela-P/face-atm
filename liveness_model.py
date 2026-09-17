import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ---------------- Prepare data ----------------
train_datagen = ImageDataGenerator(rescale=1./255)
train_generator = train_datagen.flow_from_directory(
    "dataset/user1",  # folder with subfolders 'real' and 'spoof'
    target_size=(64,64),
    batch_size=32,
    class_mode='binary'
)

# ---------------- Build model ----------------
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(64,64,3)),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# ---------------- Train ----------------
model.fit(train_generator, epochs=10)

# ---------------- Save model ----------------
model.save("liveness_model.h5")
print("Model saved as liveness_model.h5")
