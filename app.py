import os
import time
import uuid
import base64
from flask import Flask, render_template, request, jsonify

# Nouveau pipeline détection + classification
from detect_and_classify import detect_and_classify

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ===========================
# Page principale (upload PC)
# ===========================

@app.route("/", methods=["GET", "POST"])
def index():
    image_data = None

    if request.method == "POST":
        # 1) Upload depuis fichier
        if "file" in request.files:
            file = request.files["file"]
            if file and file.filename != "":
                filename = str(uuid.uuid4()) + ".png"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                print("📁 Image uploadée :", filepath)

                image_data = detect_and_classify(filepath)

        # 2) Upload depuis webcam (base64)
        elif "webcam_image" in request.form:
            data_url = request.form["webcam_image"]
            if data_url.startswith("data:image"):
                base64_str = data_url.split(",")[1]
                image_data_bytes = base64.b64decode(base64_str)
                filename = str(uuid.uuid4()) + ".png"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, "wb") as f:
                    f.write(image_data_bytes)

                print("📷 Image capturée depuis webcam :", filepath)

                image_data = detect_and_classify(filepath)

    return render_template("index.html", image_data=image_data)


# ===========================
# Route pour capture webcam (JS)
# ===========================

@app.route("/predict_webcam_frame", methods=["POST"])
def predict_webcam_frame():
    data = request.get_json()
    if data and "image" in data:
        try:
            image_data = base64.b64decode(data["image"].split(",")[1])
            if len(image_data) < 1000:
                return jsonify({"error": "image trop petite"}), 400

            filepath = os.path.join(UPLOAD_FOLDER, "frame.png")
            with open(filepath, "wb") as f:
                f.write(image_data)

            print("📷 Frame reçue pour prédiction live")

            annotated_img = detect_and_classify(filepath)

            return jsonify({"image": annotated_img})

        except Exception as e:
            print("❌ Erreur dans la prédiction live :", e)
            return jsonify({"error": "failed to process image"}), 500

    return jsonify({"error": "no image"}), 400


if __name__ == "__main__":
    app.run(debug=True)
