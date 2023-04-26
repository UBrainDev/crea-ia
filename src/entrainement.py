import os
from PIL import Image
import torch
import torchvision
import torchvision.transforms as transforms

from db import get_db


def train_model(modelid):

    # récupérer le jeu de données du modèle
    bdd = get_db()
    jeu_de_donnees = bdd.execute(
        'SELECT id, ext, tags FROM data_elements WHERE model_id = ?', (modelid,)).fetchall()

    # associer à chaque image ses labels
    labels = {}
    images = []
    for element in jeu_de_donnees:
        labels[element['id']] = element['tags'].split(',')
        images.append(element['id'] + '.' + element['ext'])

    # paramètres de transformation des images du jeu d'entrainement
    # toutes les images doivent avoir le même format
    # on compresse donc les images en 224x224 pixels
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ]
    )

    dataset = JeuDeDonnees('src/static/data/1', labels,
                           images, transform=transform)
    trainloader = torch.utils.data.DataLoader(
        dataset, batch_size=1, shuffle=True)

    model = torchvision.models.resnet18(pretrained=True)
    model.fc = torch.nn.Linear(512, 2)

    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

    for epoch in range(10):
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data
            optimizer.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            if i % 10 == 9:
                print(f'[{epoch + 1}, {i + 1}] loss: {running_loss / 10}')
                running_loss = 0.0

    print('Finished Training')


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
        label_str = self.labels[self.images[idx].split('.')[0]]
        # convert label string to integer label
        label = self.label_map[label_str]
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
