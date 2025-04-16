# app.py
import os
import uuid
import base64

from flask import Flask, render_template, request
from model import load_my_model, predict_image, preprocess_image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Charger le modèle au démarrage
model = load_my_model()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Cas 1: Upload depuis PC
        if "file" in request.files:
            file = request.files["file"]
            if file.filename != "":
                filename = str(uuid.uuid4()) + ".png"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                # Prétraitement et prédiction
                tensor_img = preprocess_image(filepath)
                prediction = predict_image(model, tensor_img)

                return render_template("index.html", prediction=prediction)

        # Cas 2: Image webcam (base64)
        if "webcam_image" in request.form:
            data_url = request.form["webcam_image"]
            # data_url a la forme "data:image/png;base64,...."
            base64_str = data_url.split(",")[1]  # séparer l'en-tête
            image_data = base64.b64decode(base64_str)

            filename = str(uuid.uuid4()) + ".png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, "wb") as f:
                f.write(image_data)

            # Prétraitement et prédiction
            tensor_img = preprocess_image(filepath)
            prediction = predict_image(model, tensor_img)

            return render_template("index.html", prediction=prediction)

    return render_template("index.html", prediction=None)

if __name__ == "__main__":
    # En local
    app.run(debug=True, host="0.0.0.0", port=5000)
