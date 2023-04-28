import json
import time
from src.db import get_db
import torch
import torchvision.transforms as transforms
import torchvision
import os

from src.interne.jeu_de_donnees import JeuDeDonnees


def register_ws_events(socketio):

    # informations sur la tâche/job en cours
    current_task = {
        'model_id': None,
        'etape': 0,
        'debut_timestamp': None,
        'epochs': 0,
    }

    @socketio.on('message')
    def handle_message(message):

        # on décompose le message
        split_msg = message.split(':')
        nom, contenu = split_msg[0], split_msg[1]
        data = contenu.split(',')

        bdd = get_db()

        match nom:
            case 'handshake':
                if data[0] == current_task['model_id']:
                    socketio.emit('message', 'connect:ok,' +
                                  current_task['etape'] + ',' + current_task['debut_timestamp'] + ',' + current_task['epochs'])

                elif current_task['model_id'] is None:
                    # récupère le nombre d'éléments étiquetés
                    nb_data_elms = bdd.execute(
                        'SELECT COUNT(*) FROM data_elements WHERE model_id = ? AND tags IS NOT NULL', (data[0],)).fetchone()[0]

                    socketio.emit('message', 'connect:ok,0,' +
                                  str(nb_data_elms))

                else:
                    socketio.emit('message', 'connect:occupe')

            case 'train':

                if current_task['model_id'] is None:

                    # met à jour les informations sur la tâche en cours
                    current_task['model_id'] = data[0]
                    current_task['etape'] = '1'
                    current_task['debut_timestamp'] = str(int(time.time()))
                    current_task['epochs'] = str(data[1])

                    train_model(data[0], data, socketio)

                else:
                    socketio.emit('message', 'train:occupe')

    def train_model(modelid, data, socketio):

        # hyperparamètres to float
        _, epochs, batch_size, learning_rate, momentum, weight_decay, image_size = map(
            float, data)
        epochs, batch_size, image_size = int(
            epochs), int(batch_size), int(image_size)

        # récupérer le jeu de données du modèle
        bdd = get_db()
        jeu_de_donnees = bdd.execute(
            'SELECT id, ext, tags FROM data_elements WHERE model_id = ? AND tags IS NOT NULL', (modelid,)).fetchall()

        # associer à chaque image ses labels
        labels = {}
        images = []
        for element in jeu_de_donnees:
            labels[str(element['id'])] = element['tags'].split(',')
            images.append(str(element['id']) + '.' + element['ext'])

        # vérifier que les hyperparamètres sont valides
        if epochs <= 0 or batch_size <= 0 or image_size <= 0 or learning_rate <= 0 or momentum < 0 or weight_decay < 0:
            socketio.emit('message', 'erreur:valeurs nulles ou negatives')
            drop_task()
            return

        elif weight_decay > 1 or momentum > 1 or learning_rate > 1 or image_size > 4096:
            socketio.emit(
                'message', 'erreur:valeurs incorrectes, trop grandes')
            drop_task()
            return

        # si le nombre d'images est inférieur au batch_size
        if len(images) < batch_size:
            batch_size = len(images)

        # paramètres de transformation des images du jeu d'entrainement
        # toutes les images doivent avoir le même format
        transform = transforms.Compose(
            [
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
            ]
        )

        # compatible avec les GPU?
        device = torch.device(
            "cuda:0" if torch.cuda.is_available() else "cpu")

        # créer le jeu de données
        dataset = JeuDeDonnees('src/static/data/' + str(modelid), labels,
                               images, transform=transform)
        trainloader = torch.utils.data.DataLoader(
            dataset, batch_size=batch_size, shuffle=True)

        # créer le modèle
        model = torchvision.models.resnet18(pretrained=True)
        model.fc = torch.nn.Linear(512, len(dataset.label_map))
        model = model.to(device)

        # critère de perte et optimiseur
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate,
                                    momentum=momentum, weight_decay=weight_decay)

        modulo_cap = (6 - batch_size) if batch_size < 6 else 1

        for epoch in range(epochs):
            running_loss = 0.0
            correct = 0
            for i, data in enumerate(trainloader, 0):
                inputs, labels = data
                inputs, labels = inputs.to(device), labels.to(device)

                optimizer.zero_grad()

                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                running_loss += loss.item()
                correct += (outputs.argmax(1) == labels).sum().item()

                if i % modulo_cap == 0:
                    print(
                        f'[{epoch + 1}, {i + 1}] loss: {running_loss / 10}, correct: {correct}')
                    running_loss = 0.0

                    # envoie un message au socket
                    socketio.emit('message', 'update:'+str(epoch + 1) +
                                  ',' + str((i + 1) * batch_size) + ',' + str(correct) + ',' + str(len(trainloader) * batch_size))

        print("Entrainement terminé")

        # sauvegarde le modèle
        path = 'output/' + str(modelid) + '/' + \
            'modele' + str(int(time.time()))

        if not os.path.exists('output/' + str(modelid) + '/'):
            os.makedirs('output/' + str(modelid) + '/')

        torch.save(model.state_dict(), path + '.pth')

        # créer un fichier .json contenant les informations sur le modèle
        with open(path + '.json', 'w') as f:
            json.dump({
                'model_id': modelid,
                'epochs': epochs,
                'batch_size': batch_size,
                'learning_rate': learning_rate,
                'momentum': momentum,
                'weight_decay': weight_decay,
                'image_size': image_size,
                'label_map': {v: k for k, v in dataset.label_map.items()}
            }, f)

        # envoie un message au socket
        socketio.emit('message', 'train:ok,' + path + '.pth')

        # met à jour les informations sur la tâche en cours
        drop_task()

    def drop_task():
        current_task['model_id'] = None
        current_task['etape'] = 0
        current_task['debut_timestamp'] = None
        current_task['epochs'] = 0
