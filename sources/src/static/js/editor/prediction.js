// éléments du DOM
const prediction_screen = document.getElementById('prediction_screen');
const selection_screen = document.getElementById('selection_screen');

const model_name = document.getElementById('model_name');
const labels_results = document.getElementById('labels_results');
const import_image_container = document.getElementById('import_image_container');
const image_input = document.getElementById('image_input');
const image_preview = document.getElementById('image_preview');

// data
let modelName = null;

// remplacer les timestamps par des dates lisibles
const timestampElements = document.querySelectorAll('[data-timestamp]');
timestampElements.forEach((element) => {

    const timestamp = element.getAttribute('data-timestamp');
    const date = new Date(timestamp * 1000);
    const diff = Date.now() - date.getTime();

    element.innerHTML = diff > 86400000 ? (" le " + date.toLocaleString()) : (" il y a " + timeSince((diff) / 1000))

});

if (selectedFile != '') loadModel(selectedFile);

// affichage relatif d'une date
function timeSince(secs) {
    let temps = [['heure', 3600], ['minute', 60], ['seconde', 1]];
    for (let i = 0; i < temps.length; i++) {
        let val = Math.floor(secs / temps[i][1]);
        if (val > 0)
            return val + ' ' + temps[i][0] + (val > 1 ? 's' : '');
    }
}

// charger un modèle entrainé
function loadModel(nomModele) {

    prediction_screen.style.display = "flex";
    selection_screen.style.display = "none";
    import_image_container.style.display = "flex";

    model_name.innerHTML = nomModele;
    modelName = nomModele;

    // récupère les étiquettes du modèle
    fetch('/api/models/' + modelId + '/labelling')
        .then(response => response.json())
        .then(data => {

            data.labels.forEach((label) => {

                // créer l'élément HTML
                const labelElement = document.createElement('div');
                labelElement.classList.add('label');
                labelElement.setAttribute('data-label', label);
                labelElement.innerHTML = `<div class="prog-text"><h4>${label}</h4><h4>0%</h4></div>`;

                const innerProgress = document.createElement('div');
                innerProgress.classList.add('inner-progress');
                labelElement.appendChild(innerProgress);

                // ajouter l'élément à la liste
                labels_results.appendChild(labelElement);

            });

        });

}

// Charger une image (l'envoyer au serveur et la prédire)
function loadImage() {

    // afficher la prévisualisation de l'image
    image_preview.style.backgroundImage = "url('" + URL.createObjectURL(image_input.files[0]) + "')";
    image_preview.style.display = "flex";
    import_image_container.style.display = "none";

    // créer un objet FormData pour envoyer l'image au serveur
    const formData = new FormData();
    formData.append('image', image_input.files[0]);

    // envoyer l'image au serveur
    fetch('/api/models/' + modelId + '/prediction/' + modelName, {
        method: 'POST',
        body: formData
    }).then(response => response.json())
        .then(data => {

            console.log(data)

            // afficher les résultats
            data.predictions.forEach((result) => {

                const labelElement = document.querySelector('[data-label="' + result.label + '"]');
                const innerProgress = labelElement.querySelector('.inner-progress');
                const progText = labelElement.querySelector('.prog-text');

                const proba = result.proba * 100;
                innerProgress.style.width = proba + "%";
                progText.innerHTML = `<h4>${result.label}</h4><h4>${Math.round(proba)}%</h4>`;

            });

        });


}

function autreImage() {

    image_input.value = '';
    image_preview.style.display = "none";
    import_image_container.style.display = "flex";

    // réinitialiser les résultats
    const labelElements = document.querySelectorAll('[data-label]');
    labelElements.forEach((labelElement) => {

        const innerProgress = labelElement.querySelector('.inner-progress');
        const progText = labelElement.querySelector('.prog-text');

        innerProgress.style.width = "0%";
        progText.innerHTML = `<h4>${labelElement.getAttribute('data-label')}</h4><h4>0%</h4>`;

    });

}

function deleteModel(nomModele) {

    if (confirm("Êtes-vous sûr de vouloir supprimer ce modèle ? Cette action est irréversible."))

        fetch('/api/models/' + modelId + '/prediction/' + nomModele, {
            method: 'DELETE'
        }).then(() => {

            // supprimer l'élément de la liste
            document.querySelector('[data-model="' + nomModele + '"]').remove();

        });

}