import torch
import numpy as np
import cv2
from PIL import Image
import io
from backend.predictor import model, transform, CLASS_NAMES, device

class GradCAM:
    def __init__(self, model):
        self.model       = model
        self.gradients   = None
        self.activations = None

        target_layer = model.blocks[-1]
        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, input, output):
        self.activations = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, input_tensor, class_idx):
        output = self.model(input_tensor)
        self.model.zero_grad()
        output[0, class_idx].backward()

        weights  = self.gradients.mean(dim=(2, 3), keepdim=True)
        heatmap  = (weights * self.activations).sum(dim=1).squeeze()
        heatmap  = torch.relu(heatmap)
        heatmap  = heatmap - heatmap.min()
        heatmap  = heatmap / (heatmap.max() + 1e-8)

        return heatmap.cpu().numpy()

# Create one GradCAM instance
gradcam = GradCAM(model)

def generate_gradcam(image_bytes: bytes):
    # Load and preprocess image
    image        = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(device)
    input_tensor.requires_grad_()

    # Predict
    with torch.enable_grad():
        output   = model(input_tensor)
        probs    = torch.softmax(output, dim=1)[0]
        pred_idx = probs.argmax().item()

    # Generate heatmap
    heatmap = gradcam.generate(input_tensor, pred_idx)

    # Resize heatmap to original image size
    orig_w, orig_h = image.size
    heatmap_resized = cv2.resize(heatmap, (orig_w, orig_h))

    # Apply color map
    heatmap_color = cv2.applyColorMap(
        np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    # Overlay on original image
    original_array = np.array(image)
    overlaid       = cv2.addWeighted(
        original_array, 0.6, heatmap_color, 0.4, 0)

    # Convert back to bytes to send via API
    result_image = Image.fromarray(overlaid)
    img_bytes    = io.BytesIO()
    result_image.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes, CLASS_NAMES[pred_idx]