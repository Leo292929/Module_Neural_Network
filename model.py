import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import time
# Les mêmes normalisations et resize que dans le script d'entraînement
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

labels = [  'ace of clubs','ace of diamonds','ace of hearts','ace of spades', 
            'eight of clubs', 'eight of diamonds', 'eight of hearts','eight of spades', 
            'five of clubs', 'five of diamonds', 'five of hearts', 'five of spades', 
            'four of clubs', 'four of diamonds', 'four of hearts', 'four of spades', 
            'jack of clubs', 'jack of diamonds', 'jack of hearts', 'jack of spades', 
            'joker',
            'king of clubs', 'king of diamonds', 'king of hearts', 'king of spades', 
            'nine of clubs', 'nine of diamonds', 'nine of hearts', 'nine of spades', 
            'queen of clubs', 'queen of diamonds', 'queen of hearts', 'queen of spades', 
            'seven of clubs', 'seven of diamonds', 'seven of hearts', 'seven of spades', 
            'six of clubs',  'six of diamonds', 'six of hearts', 'six of spades', 
            'ten of clubs', 'ten of diamonds', 'ten of hearts', 'ten of spades', 
            'three of clubs', 'three of diamonds', 'three of hearts', 'three of spades', 
            'two of clubs', 'two of diamonds', 'two of hearts', 'two of spades'
        ]


import time

def load_my_model():
    print("🟡 Chargement du modèle...")
    t0 = time.time()

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(labels))
    model.load_state_dict(torch.load("mon_modele_cartes.pt", map_location="cpu"))
    model.eval()

    print(f"✅ Modèle chargé en {time.time() - t0:.2f} sec")
    return model


def preprocess_image(img_path):
    # Ou bien on reçoit un objet PIL déjà ouvert
    img = Image.open(img_path).convert("RGB")
    img_t = transform(img)
    return img_t.unsqueeze(0)  # shape [1, 3, 224, 224]

def predict_image(model, tensor_img):
    with torch.no_grad():
        outputs = model(tensor_img)
        _, predicted = torch.max(outputs, 1)
    predicted_idx = predicted.item()  # index de classe (0..51)
    return labels[predicted_idx]