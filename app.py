# app.py
import os
import uuid
import base64
from flask import Flask, render_template, request
from model import load_my_model, preprocess_image, predict_image
import time
from flask import jsonify

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = load_my_model()

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    if request.method == "POST":
        # 1) upload depuis PC
        if "file" in request.files:
            file = request.files["file"]
            if file.filename != "":
                filename = str(uuid.uuid4()) + ".png"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                tensor_img = preprocess_image(filepath)
                prediction = predict_image(model, tensor_img)

        # 2) image webcam (base64)
        elif "webcam_image" in request.form:
            data_url = request.form["webcam_image"]
            # data_url = "data:image/png;base64,...."
            base64_str = data_url.split(",")[1]
            image_data = base64.b64decode(base64_str)
            filename = str(uuid.uuid4()) + ".png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, "wb") as f:
                f.write(image_data)

            tensor_img = preprocess_image(filepath)
            t0 = time.time()
            prediction = predict_image(model, tensor_img)
            print(f"✅ Prédiction faite en {time.time() - t0:.2f} sec")

    return render_template("index.html", prediction=prediction)


@app.route("/predict_webcam_frame", methods=["POST"])
def predict_webcam_frame():
    data = request.get_json()
    if data and "image" in data:
        image_data = base64.b64decode(data["image"].split(",")[1])
        filename = "frame.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, "wb") as f:
            f.write(image_data)

        tensor_img = preprocess_image(filepath)
        prediction = predict_image(model, tensor_img)

        return jsonify({"prediction": prediction})

    return jsonify({"error": "no image"}), 400


if __name__ == "__main__":
    app.run(debug=True)