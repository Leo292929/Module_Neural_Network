import os
import uuid
import base64
import random
from flask import Flask, render_template, request, jsonify, session

# ---------------------------------------------------------
# 1) Paramètres généraux
# ---------------------------------------------------------
UPLOAD_FOLDER = "uploads"
ASSETS_SUBFOLDER = "assets"          # images de fond dans  static/assets/
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = os.environ.get("SECRET_KEY", "dev-change-me")  # clé pour la session

# ---------------------------------------------------------
# 2) Pipeline “détection + classification”
# ---------------------------------------------------------
# Adapte ce chemin/nom selon ton projet
from detect_and_classify import detect_and_classify


# ---------------------------------------------------------
# 3) Route principale  (upload depuis disque ou webcam)
# ---------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    image_data = None   # image annotée (base64) renvoyée au template

    # ----------- Sélection / mémorisation du fond aléatoire -----------
    if "bg_image" not in session:
        assets_dir = os.path.join(app.static_folder, ASSETS_SUBFOLDER)
        images = [
            f for f in os.listdir(assets_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))
        ]
        session["bg_image"] = random.choice(images) if images else None
    bg_image = session.get("bg_image")
    # -------------------------------------------------------------------

    if request.method == "POST":
        # 1) Upload d'un fichier depuis le PC
        if "file" in request.files:
            file = request.files["file"]
            if file and file.filename:
                filename = f"{uuid.uuid4()}.png"
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)

                print("📁 Image uploadée :", filepath)
                image_data = detect_and_classify(filepath)

        # 2) Upload d'une image encodée en base64 (webcam)
        elif "webcam_image" in request.form:
            data_url = request.form["webcam_image"]
            if data_url.startswith("data:image"):
                base64_str = data_url.split(",")[1]
                image_bytes = base64.b64decode(base64_str)

                filename = f"{uuid.uuid4()}.png"
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                with open(filepath, "wb") as f:
                    f.write(image_bytes)

                print("📷 Image capturée depuis webcam :", filepath)
                image_data = detect_and_classify(filepath)

    # On envoie     image_data (peut être None) et bg_image     au template
    return render_template("index.html",
                           image_data=image_data,
                           bg_image=bg_image)


# ---------------------------------------------------------
# 4) Prédiction “live” pour la webcam (appelé en AJAX)
# ---------------------------------------------------------
@app.route("/predict_webcam_frame", methods=["POST"])
def predict_webcam_frame():
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "no image"}), 400

    try:
        image_data = base64.b64decode(data["image"].split(",")[1])
        if len(image_data) < 1000:
            return jsonify({"error": "image trop petite"}), 400

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], "frame.png")
        with open(filepath, "wb") as f:
            f.write(image_data)

        print("📷 Frame reçue pour prédiction live")
        annotated_img = detect_and_classify(filepath)

        return jsonify({"image": annotated_img})

    except Exception as e:
        print("❌ Erreur dans la prédiction live :", e)
        return jsonify({"error": "failed to process image"}), 500


# ---------------------------------------------------------
# 5) Lancement de l’application
# ---------------------------------------------------------
if __name__ == "__main__":
    # debug=True = auto‑reload + tracebacks lisibles
    app.run(debug=True)
