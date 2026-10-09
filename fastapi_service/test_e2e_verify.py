import os
import requests
import base64
import json

base_url = "http://127.0.0.1:8000"
test_image = r"C:\Users\shame\OneDrive\ドキュメント\GitHub\face-atm\legacy\test_capture.jpg"
other_image = r"C:\Users\shame\OneDrive\ドキュメント\GitHub\face-atm\legacy\getimg.jpg"

def get_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

b64_img = get_b64(test_image)
b64_other = get_b64(other_image)

# Get embedding for the target
res = requests.post(f"{base_url}/api/v1/ml/generate-embedding", json={"image_b64": b64_img})
target_emb = res.json()["embedding"]

print("--- Testing /api/v1/ml/verify-authentication (SAME IMAGE) ---")
res = requests.post(f"{base_url}/api/v1/ml/verify-authentication", json={
    "image_b64": b64_img,
    "target_embedding": target_emb
})
print(f"Status: {res.status_code}")
try:
    data = res.json()
    print("Response:", data)
    print(f"Match: {data.get('match')}, Distance: {data.get('distance')}, Similarity: {data.get('similarity')}")
except Exception as e:
    print("Error parsing response:", e)

print("\n--- Testing /api/v1/ml/verify-authentication (DIFFERENT IMAGE) ---")
res2 = requests.post(f"{base_url}/api/v1/ml/verify-authentication", json={
    "image_b64": b64_other,
    "target_embedding": target_emb
})
print(f"Status: {res2.status_code}")
try:
    data2 = res2.json()
    print("Response:", data2)
    print(f"Match: {data2.get('match')}, Distance: {data2.get('distance')}, Similarity: {data2.get('similarity')}")
except Exception as e:
    print("Error parsing response:", e)

