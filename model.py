# model.py
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image

class MonReseau(nn.Module):
    def __init__(self, num_classes=10):
        super(MonReseau, self).__init__()
        # Exemple : un petit CNN minimaliste ou un ResNet
        # ICI on met un module fictif
        self.conv = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1)
        self.pool = nn.AdaptiveAvgPool2d((1,1))
        self.fc = nn.Linear(16, num_classes)

    def forward(self, x):
        x = self.conv(x)         # [batch, 16, H, W]
        x = nn.functional.relu(x)
        x = self.pool(x)         # [batch, 16, 1, 1]
        x = x.view(x.size(0), -1) # [batch, 16]
        x = self.fc(x)           # [batch, num_classes]
        return x

# Charger le modèle
def load_my_model():
    # on instance le même réseau que lors de l'entraînement
    model = MonReseau(num_classes=10)
    # on charge les poids
    model.load_state_dict(torch.load("mon_modele_cartes.pt", map_location=torch.device('cpu')))
    model.eval()  # mode évaluation
    return model

# Prétraitement de l'image
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

def preprocess_image(img_path):
    img = Image.open(img_path).convert("RGB")
    return transform(img).unsqueeze(0)  # shape [1, 3, 224, 224]

# Effectuer la prédiction
def predict_image(model, input_tensor):
    # input_tensor : shape [1, 3, 224, 224]
    with torch.no_grad():
        outputs = model(input_tensor)
        predicted_class = outputs.argmax(dim=1).item()
    return predicted_class
