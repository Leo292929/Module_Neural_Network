from ultralytics import YOLO
import torch
import torchvision.transforms as transforms
from PIL import Image
import cv2
import os
import base64
from model import load_my_model, predict_image  # adapte si nécessaire

# === Chargement des modèles ===

# 1. Modèle YOLOv8 entraîné pour détecter des "cartes"
detector = YOLO("best.pt")

# 2. Modèle PyTorch pour classifier les cartes (52 classes)
classifier = load_my_model()

# 3. Liste des classes (dans le même ordre que l'entraînement)
labels = [
    "2_of_clubs", "3_of_clubs", "4_of_clubs", "5_of_clubs", "6_of_clubs", "7_of_clubs", "8_of_clubs", "9_of_clubs", "10_of_clubs", "jack_of_clubs", "queen_of_clubs", "king_of_clubs", "ace_of_clubs",
    "2_of_diamonds", "3_of_diamonds", "4_of_diamonds", "5_of_diamonds", "6_of_diamonds", "7_of_diamonds", "8_of_diamonds", "9_of_diamonds", "10_of_diamonds", "jack_of_diamonds", "queen_of_diamonds", "king_of_diamonds", "ace_of_diamonds",
    "2_of_hearts", "3_of_hearts", "4_of_hearts", "5_of_hearts", "6_of_hearts", "7_of_hearts", "8_of_hearts", "9_of_hearts", "10_of_hearts", "jack_of_hearts", "queen_of_hearts", "king_of_hearts", "ace_of_hearts",
    "2_of_spades", "3_of_spades", "4_of_spades", "5_of_spades", "6_of_spades", "7_of_spades", "8_of_spades", "9_of_spades", "10_of_spades", "jack_of_spades", "queen_of_spades", "king_of_spades", "ace_of_spades"
]

# === Transformations pour le classifieur ===
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

def preprocess_crop(pil_img):
    return transform(pil_img).unsqueeze(0)

# === Pipeline complet ===

def detect_and_classify(image_path):
    image = Image.open(image_path).convert("RGB")
    results = detector(image_path)
    img_cv = cv2.imread(image_path)

    if results[0].boxes is None:
        print("🛑 Aucune carte détectée.")
        return encode_image(img_cv)

    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        # Recadrage de la carte
        cropped = image.crop((x1, y1, x2, y2))

        # Classification
        input_tensor = preprocess_crop(cropped)
        class_id = int(predict_image(classifier, input_tensor))  # ✅ conversion assurée
        label = labels[class_id]

        # Dessiner la boîte + le label sur l'image d'origine
        cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img_cv, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2)

    return encode_image(img_cv)


def encode_image(img_cv):
    """Encode une image OpenCV en base64 pour affichage HTML."""
    _, buffer = cv2.imencode(".jpg", img_cv)
    img_base64 = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{img_base64}"
