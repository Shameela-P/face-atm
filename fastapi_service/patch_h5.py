import h5py
import json
import shutil
import os
import sys

# Ensure stdout can handle utf-8 on Windows
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

model_path = r"C:\Users\shame\OneDrive\ドキュメント\GitHub\face-atm\legacy\facenet_keras.h5"
backup_path = r"C:\Users\shame\OneDrive\ドキュメント\GitHub\face-atm\legacy\facenet_keras.h5.bak"

if not os.path.exists(backup_path):
    shutil.copy2(model_path, backup_path)
    print(f"Created backup.")

with h5py.File(model_path, "r+") as f:
    model_config_str = f.attrs.get("model_config")
    if type(model_config_str) == bytes:
        model_config_str = model_config_str.decode('utf-8')
    
    config = json.loads(model_config_str)
    
    for layer in config["config"]["layers"]:
        if layer["class_name"] == "Lambda" and layer["name"].endswith("ScaleSum"):
            scale_val = layer["config"].get("arguments", {}).get("scale", 1.0)
            layer["class_name"] = "ScaleSumLayer"
            # Replace lambda config with custom layer config
            layer["config"] = {
                "name": layer["config"]["name"],
                "trainable": layer["config"]["trainable"],
                "dtype": "float32",
                "scale": scale_val
            }

    new_config_str = json.dumps(config).encode('utf-8')
    f.attrs.modify("model_config", new_config_str)

print("Successfully patched model_config in facenet_keras.h5 to use ScaleSumLayer.")
