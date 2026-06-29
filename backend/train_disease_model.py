import os
import glob
import json
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
import torch.nn as nn
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_SAVE_PATH = os.path.join(BASE_DIR, 'backend', 'disease_model.pth')
CLASSES_SAVE_PATH = os.path.join(BASE_DIR, 'backend', 'class_names.json')

# Collect all image paths from both datasets
# Multi-Crop dataset is nested
MULTICROP_TRAIN_DIR = os.path.join(BASE_DIR, 'Multi-Crop Disease Dataset', 'Multicrop Disease Dataset', 'Multicrop Disease Dataset', 'train')
CROP_DATASET_DIR = os.path.join(BASE_DIR, 'crop disease dataset')

def gather_dataset():
    images = []
    labels = []
    class_name_to_id = {}
    current_id = 0
    
    # 1. Gather from crop disease dataset (22 classes directly in the folder)
    if os.path.exists(CROP_DATASET_DIR):
        print(f"Scanning {CROP_DATASET_DIR}...")
        for cls_name in os.listdir(CROP_DATASET_DIR):
            cls_dir = os.path.join(CROP_DATASET_DIR, cls_name)
            if not os.path.isdir(cls_dir): continue
            
            if cls_name not in class_name_to_id:
                class_name_to_id[cls_name] = current_id
                current_id += 1
                
            label_id = class_name_to_id[cls_name]
            # Just take max 30 images per class for fast POC training
            imgs = glob.glob(os.path.join(cls_dir, '*.jpg')) + glob.glob(os.path.join(cls_dir, '*.png')) + glob.glob(os.path.join(cls_dir, '*.JPG'))
            for img in imgs[:30]:
                images.append(img)
                labels.append(label_id)

    # 2. Gather from Multi-Crop dataset
    if os.path.exists(MULTICROP_TRAIN_DIR):
        print(f"Scanning {MULTICROP_TRAIN_DIR}...")
        for cls_name in os.listdir(MULTICROP_TRAIN_DIR):
            cls_dir = os.path.join(MULTICROP_TRAIN_DIR, cls_name)
            if not os.path.isdir(cls_dir): continue
            
            if cls_name not in class_name_to_id:
                class_name_to_id[cls_name] = current_id
                current_id += 1
                
            label_id = class_name_to_id[cls_name]
            imgs = glob.glob(os.path.join(cls_dir, '*.jpg')) + glob.glob(os.path.join(cls_dir, '*.png')) + glob.glob(os.path.join(cls_dir, '*.JPG'))
            for img in imgs[:30]: # Limit for speed
                images.append(img)
                labels.append(label_id)

    # Invert dictionary
    id_to_class_name = {v: k for k, v in class_name_to_id.items()}
    return images, labels, id_to_class_name


class CustomCropDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
        
    def __len__(self):
        return len(self.image_paths)
        
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        return image, label


def train_model():
    print("=== Gathering offline dataset ===")
    images, labels, id_to_class = gather_dataset()
    
    if len(images) == 0:
        print("Error: No images found!")
        return

    num_classes = len(id_to_class)
    print(f"Found {len(images)} images across {num_classes} classes.")
    
    # Save class mapping
    with open(CLASSES_SAVE_PATH, 'w') as f:
        json.dump(id_to_class, f)
    
    # Preprocessing transforms (MobileNetV2 expectations)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    dataset = CustomCropDataset(images, labels, transform=transform)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Setup MobileNetV2
    print("Initializing MobileNetV2...")
    model = models.mobilenet_v2(pretrained=True)
    
    # Freeze layers except the last logic
    for param in model.parameters():
        param.requires_grad = False
        
    # Replace classifier
    model.classifier[1] = nn.Linear(model.last_channel, num_classes)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.classifier.parameters(), lr=0.001)
    
    epochs = 1  # 1 Epoch just to prove end-to-end functionality offline
    print(f"Training for {epochs} epoch(s) on CPU...")
    model.train()
    
    for epoch in range(epochs):
        running_loss = 0.0
        for i, (inputs, targets) in enumerate(dataloader):
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            if i % 10 == 0:
                print(f"Epoch {epoch+1} | Batch {i}/{len(dataloader)} | Loss: {loss.item():.4f}")
                
    # Save the model
    print(f"Saving Offline ML model to {MODEL_SAVE_PATH}")
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print("Done! The offline dual-engine is ready.")


if __name__ == '__main__':
    train_model()
