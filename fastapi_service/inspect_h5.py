import h5py
import json

model_path = r"C:\Users\shame\OneDrive\ドキュメント\GitHub\face-atm\legacy\facenet_keras.h5"
with h5py.File(model_path, "r") as f:
    model_config = f.attrs.get("model_config")
    if model_config is None:
        print("No model_config found")
    else:
        # It's a JSON string
        config = json.loads(model_config)
        # Find Lambda layers
        for layer in config["config"]["layers"]:
            if layer["class_name"] == "Lambda":
                print(f"Found Lambda layer: {layer['name']}")
                print(f"Config: {layer['config']}")
