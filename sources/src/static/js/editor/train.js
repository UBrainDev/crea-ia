let socket = io();

// envoyer une poignée de main (handshake) au serveur
socket.on('connect', function () {
    sendMessage('handshake:' + modelId);
});

// lorsque le serveur envoie un message
socket.on('message', function (msg) {

    console.log("%c[<SOCKET] %c" + msg, "color: #00ff00", "color: #ffffff")

    let [nom, message] = msg.split(':');
    let data = message.split(',');

    switch (nom) {
        case 'connect':
            if (data[0] == 'ok') {

                loadingScreen.style.display = 'none';

                if (data[1] == '0') {
                    isTraining = false;
                    startTaskTimestamp = -1;
                    entrainementScreen.style.display = 'none';
                    configScreen.style.display = 'block';
                    document.getElementById("labeled_count").innerText = (data[2] || 0);
                    document.getElementById("qualite_rank").innerText = qualiteRank[Math.round(parseInt(data[2]) / 50)] || "S+";
                    document.getElementById("qualite_rank_text").innerText = qualiteRankText[Math.round(parseInt(data[2]) / 150)] || "Votre jeu de données contient suffisamment d'éléments pour entrainer un modèle très fiable !";
                    if (parseInt(data[2]) < 5) openModal('aucunDocument');
                } else {
                    loadingTrainScreen.style.display = 'flex';
                    epochNbTotal.innerText = data[3];
                    startTaskTimestamp = data[2];
                    totalEpochs = data[3];
                }

            } else {

                // si un autre modèle est en cours d'entrainement
                openModal('train_occupe');
                socket.disconnect();

            }

            break;

        case 'update':

            if (!isTraining) {
                isTraining = true;
                loadingTrainScreen.style.display = 'none';
                entrainementScreen.style.display = 'flex';
                startTaskTimestamp = startTaskTimestamp < 0 ? (Date.now() / 1000) : startTaskTimestamp;
            }

            const [epoch, iteration, successIterations, totalEls] = data;
            epochNbCurrent.innerText = epoch;
            epochProgress.style.width = (iteration / totalEls * 100) + '%';
            accuracyProgress.style.width = (successIterations / iteration * 100) + '%';
            epochProgressText.innerText = iteration + ' / ' + totalEls;
            accuracyProgressText.innerText = (successIterations / iteration * 100).toFixed(2) + '%';
            remainingTime.innerHTML = formatTime(Math.round(((Date.now() / 1000) - startTaskTimestamp) / ((epoch - 1) + (iteration / totalEls)) * (totalEpochs) - ((Date.now() / 1000) - startTaskTimestamp)));

        case 'train':

            if (data[0] == 'ok') {

                // réinitialiser les écrans
                isTraining = false;
                startTaskTimestamp = -1;
                entrainementScreen.style.display = 'none';
                configScreen.style.display = 'block';

                openModal('training_done');
                trained_model_file.innerText = data[1];

                splitPath = (data[1]).split('/');
                document.getElementById('try_model').onclick = () =>
                    window.location.href = '/models/' + modelId + '/prediction/' + splitPath[splitPath.length - 1];

            }

    }

});

const formatTime = (temps_s) => {
    let hours = Math.floor(temps_s / 3600);
    let minutes = Math.floor((temps_s - (hours * 3600)) / 60);
    let seconds = temps_s - (hours * 3600) - (minutes * 60);
    return ('0' + hours).slice(-2) + 'h ' + ('0' + minutes).slice(-2) + 'm ' + ('0' + seconds).slice(-2) + 's';
}


// envoie un message au serveur
function sendMessage(msg) {
    socket.send(msg);
    console.log("%c[>SOCKET] %c" + msg, "color: #ff0000", "color: #ffffff");
}

// éléments du DOM
const loadingScreen = document.getElementById('ecran_attente_connexion');
const configScreen = document.getElementById('ecran_configuration');
const entrainementScreen = document.getElementById('ecran_entrainement');
const loadingTrainScreen = document.getElementById('ecran_attente_train');

const epochNbCurrent = document.getElementById('epoch_nb_current');
const epochNbTotal = document.getElementById('epoch_nb_total');
const epochProgress = document.getElementById('epoch_progress_inner');
const accuracyProgress = document.getElementById('accuracy_progress_inner');
const epochProgressText = document.getElementById('epoch_progress_text');
const accuracyProgressText = document.getElementById('accuracy_progress_text');
const remainingTime = document.getElementById('remaining_time');
const trained_model_file = document.getElementById('trained_model_file');

const hyperparametres = {
    'epochs': document.getElementById('hyperinput_epochs'),
    'batch_size': document.getElementById('hyperinput_batch_size'),
    'learning_rate': document.getElementById('hyperinput_learning_rate'),
    'momentum': document.getElementById('hyperinput_momentum'),
    'weight_decay': document.getElementById('hyperinput_weight_decay'),
    'image_size': document.getElementById('hyperinput_image_size'),
}

const hyperparametresArray = [hyperparametres.epochs, hyperparametres.batch_size, hyperparametres.learning_rate,
hyperparametres.momentum, hyperparametres.weight_decay, hyperparametres.image_size];

// data
let startTaskTimestamp = -1;
let isTraining = false;
let totalEpochs = 0;

// préconfigurations
const preconfigurations = {

    // NOM    : [epochs, batch_size, learning_rate, momentum, weight_decay, image_size]
    'standard': [10, 2, 0.001, 0.9, 0.0001, 224],
    'rapide': [10, 64, 0.005, 0.95, 0.0001, 128],
    'élaboré': [20, 6, 0.01, 0.9, 0.0005, 256],
    'léger': [10, 1, 0.001, 0.9, 0.0001, 224],
    'profond': [50, 64, 0.01, 0.95, 0.0001, 256],

}

// qualité rank
const qualiteRank =
    ["F-", "F", "F+" /* 150 */, "D-", "D", "D+" /* 300 */, "C-", "C", "C+" /* 450 */, "B-", "B", "B+" /* 600 */, "A-", "A", "A+" /* 750 */, "S-", "S", "S+" /* 900 */];

const qualiteRankText = [
    "Le jeu d'entrainement comporte trop peu d'éléments pour pouvoir entrainer un modèle fiable.", // F- à F+
    "Le jeu d'entrainement est insuffisant pour entrainer un modèle fiable, mais vous pouvez obtenir des résultats satisfaisants.", // D- à D+
    "Vous disposez de suffisamment de données pour entrainer un modèle fiable, mais vous pouvez obtenir de meilleurs résultats avec plus de données.", // C- à C+
    "Vous disposez d'un jeu de données suffisant pour entrainer un modèle fiable.", // B- à B+
    "Votre jeu de données contient suffisamment d'éléments pour entrainer un modèle très fiable !", // A- à A+
    "Vous pouvez produire un modèle renforcé et très fiable avec votre jeu de données !", // S- à S+
]

/**
 * Applique/Charge une préconfiguration
 */
function chargerPreconfiguration(nom) {
    let preconfig = preconfigurations[nom];
    hyperparametresArray.forEach((hyperparametre, index) => {
        hyperparametre.value = preconfig[index];
    });
}

// récupère tous les éléments avec l'attribut data-preconfig
let preconfigButtons = document.querySelectorAll('[data-preconfig]');
preconfigButtons.forEach(button => {
    button.addEventListener('click', () => {

        // enlève la classe active à tous les boutons
        preconfigButtons.forEach(button => {
            button.classList.remove('active');
        });

        // ajoute la classe active à la préconfiguration sélectionnée
        button.classList.add('active');

        // charge la préconfiguration
        chargerPreconfiguration(button.getAttribute('data-preconfig'));

    });
});

/**
 * Lance l'entrainement du modèle
 */
function lancerEntrainement() {
    sendMessage('train:' + modelId + ',' + hyperparametresArray.map(hyperparametre => hyperparametre.value).join(','));
    configScreen.style.display = 'none';
    loadingTrainScreen.style.display = 'flex';
    epochNbTotal.innerText = hyperparametres.epochs.value;
    totalEpochs = hyperparametres.epochs.value;
}