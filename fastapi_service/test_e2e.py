import os
import requests
import base64
import json

base_url = "http://127.0.0.1:8000"
test_image = r"C:\Users\shame\OneDrive\ドキュメント\GitHub\face-atm\legacy\test_capture.jpg"

if not os.path.exists(test_image):
    print(f"Test image not found: {test_image}")
    exit(1)

with open(test_image, "rb") as f:
    b64_img = base64.b64encode(f.read()).decode("utf-8")

print("--- Testing /api/v1/ml/generate-embedding ---")
res = requests.post(f"{base_url}/api/v1/ml/generate-embedding", json={"image_b64": b64_img})
print(f"Status: {res.status_code}")
try:
    data = res.json()
    if data.get("success"):
        emb = data["embedding"]
        print(f"Success! Embedding generated.")
        print(f"Dimension: {len(emb)}")
        print(f"First 5 values: {emb[:5]}")
        # Verify L2 normalization
        l2_norm = sum([x**2 for x in emb])**0.5
        print(f"L2 Norm: {l2_norm:.4f}")
    else:
        print("Failed to generate embedding:", data)
except Exception as e:
    print("Error parsing response:", e)

print("\n--- Testing /api/v1/ml/check-liveness ---")
res = requests.post(f"{base_url}/api/v1/ml/check-liveness", json={"image_b64": b64_img})
print(f"Status: {res.status_code}")
try:
    print("Response:", res.json())
except Exception as e:
    print("Error parsing response:", e)
