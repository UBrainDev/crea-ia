import os
from PIL import Image
import torch
import torchvision.transforms as transforms


class JeuDeDonnees(torch.utils.data.Dataset):
    def __init__(self, root: str, labels: dict, images: list[str], transform: transforms.Compose = None):
        """
        Jeu de données pour l'entrainement du modèle
        """
        self.root = root
        self.labels = labels  # dictionnaire {nom_image: [labels]}
        self.transform = transform
        self.images = images  # liste d'images (nom + extension)
        self.label_map = make_label_map(labels)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = os.path.join(self.root, self.images[idx])
        image = Image.open(img_path).convert("RGB")
        label_str: list[str] = self.labels[self.images[idx].split('.')[0]]
        label = self.label_map[label_str[0]]
        if self.transform:
            image = self.transform(image)
        return image, label


def make_label_map(labels: dict):
    """
    Créer une map des labels
    Une map des labels associe à chaque label un entier unique
    """
    label_map = {}
    for key, value in labels.items():
        for label in value:
            if label not in label_map:
                label_map[label] = len(label_map)
    return label_map
