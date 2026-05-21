import torch
import timm
from torchvision import transforms
from PIL import Image
import io
from pathlib import Path

# ---- Load model once when server starts ----
device = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_PATH = Path(__file__).resolve().parents[1] / "model" / "best_model.pth"
checkpoint = torch.load(MODEL_PATH, map_location=device)
CLASS_NAMES = checkpoint["class_names"]

model = timm.create_model("efficientnet_b3", pretrained=False, num_classes=120)
model.load_state_dict(checkpoint["model_state"])
model = model.to(device)
model.eval()

print(f"✅ Model loaded on {device}")

# ---- Image preprocessing ----
transform = transforms.Compose([
    transforms.Resize((300, 300)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

def predict(image_bytes: bytes):
    # Convert bytes to PIL image
    image        = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(input_tensor)
        probs  = torch.softmax(output, dim=1)[0]

    # Top 5 predictions
    top5_probs, top5_idxs = torch.topk(probs, 5)

    results = []
    for i in range(5):
        results.append({
            "breed"     : CLASS_NAMES[top5_idxs[i].item()],
            "confidence": round(top5_probs[i].item() * 100, 2)
        })

    return results