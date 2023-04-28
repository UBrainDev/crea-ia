const dataElementsContainer = document.getElementById('dataElementsContainer');
const dataElementsCount = document.getElementById('dataElementsCount');

if (typeof modelId == 'undefined')
    alert('modelId n\'est pas défini (js/editor/data.js)');

/**
 * Récupère (et actualise) le jeu de données du modèle
 */
function getDataElements() {

    dataElementsContainer.innerHTML = 'Chargement des données...';

    fetch('/api/models/' + modelId + '/data')
        .then(response => response.json())
        .then(data => {
            console.log(data)
            dataElementsCount.innerHTML = data.data.length;
            displayDataElements(data);
        });
}

/**
 * Affiche les données du modèle
 */
async function displayDataElements(data) {

    dataElementsContainer.innerHTML = '';

    // si aucun élément n'est présent
    if (data.data.length == 0)
        return dataElementsContainer.innerHTML = `<div class="empty-dataset"><img src="${staticPath}assets/jeu_de_donnees_vide.png"><div class="text-center"><h1>Jeu de données vide</h1><p>Le jeu de données doit contenir tous les éléments (images, textes, etc.) qui seront étiquetées puis serviront à créer votre modèle. Cliquez sur le bouton 'Importer des éléments' pour ouvrir le dossier vers lequel vous devez déposer tous les fichiers de votre jeu de données, puis cliquez sur le bouton 'actualiser', vos fichiers seront déplacés et s'afficheront ici !</p><button class='btn-border btn-primary mtop-1' onclick='getDataElements()'>Actualiser</button></div></div>`;

    // éléments incorrects
    if (data.incorrect.length > 0) {
        data.incorrect.forEach(element => {
            const dataEl = document.createElement('div');
            dataEl.classList.add('data-element');
            dataEl.classList.add('data-element-incorrect');
            dataEl.innerHTML = "Impossible d'importer <span class='file-name'>" + element + "</span>.<br><br>Le fichier doit être au format .jpg ou .png. Supprimez-le ou convertissez-le.";
            dataElementsContainer.appendChild(dataEl);
        });
    }

    for (let dataElement of data.data) {

        const dataEl = document.createElement('div');
        dataEl.classList.add('data-element');
        dataEl.style.backgroundImage = 'url(' + staticPath + 'data/' + modelId + '/' + dataElement[0] + '.' + dataElement[1] + ')';

        const deleteButton = document.createElement('button');
        deleteButton.classList.add('delete-button');
        deleteButton.innerHTML = 'Supprimer';
        deleteButton.addEventListener('click', () => {
            if (confirm('Êtes-vous sûr de vouloir supprimer cette image ?')) {
                fetch('/api/models/' + modelId + '/data/' + dataElement[0], {
                    method: 'DELETE'
                }).then(() => {
                    dataEl.remove();
                });
            }
        });

        const dataElOverlay = document.createElement('div');
        dataElOverlay.classList.add('data-element-overlay');
        dataElOverlay.innerHTML = 'Image #' + dataElement[0];

        dataEl.appendChild(dataElOverlay);
        dataEl.appendChild(deleteButton);
        dataElementsContainer.appendChild(dataEl);

        // attendre 25ms pour éviter une surcharge si il y a beaucoup d'images
        await new Promise(resolve => setTimeout(resolve, 25));

    };
}

// Bouton d'importation de données
const openImportFolder = document.getElementById('openImportFolder');
openImportFolder.addEventListener('click', () => {
    fetch('/api/models/' + modelId + '/openImportFolder');
});