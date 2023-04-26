const imageViewerEl = document.getElementById("imageViewer");
const currentDocumentId = document.getElementById("currentDocumentId");
const labelsList = document.getElementById("labelsList");
const confirmButton = document.getElementById("confirmButton");

// écrans
const etiquetageCompleted = document.getElementById("etiquetageCompleted");
const etiquetageMain = document.getElementById("etiquetageMain");

// editeur d'étiquettes
const addLabelNextStepButton = document.getElementById("addLabelNextStepButton");
const labelsListEditor = document.getElementById("labelsListEditor");
const leditorAddLabelButton = document.getElementById("labelEditor_addLabelButton");
const leditorAddLabelInput = document.getElementById("labelEditor_labelName");
const labelEditorValider = document.getElementById("labelEditor_valider");

// données
let labels = []; // liste des étiquettes du modèle
let currentDocument = {}; // document à étiqueter
let selectedLabels = []; // étiquettes sélectionnées pour le document courrant

/**
 * Récupère les données d'étiquetage du modèle (étiquettes, document, etc.)
 */
function getLabellingData() {

    fetch('/api/models/' + modelId + '/labelling')
        .then(response => response.json())
        .then(data => {
            console.log(data);

            // si le jeu de données du modèle est vide, afficher le modal d'ajout de document
            if (data.labels.length == 0 && data.next_data.code == 1)
                return openModal("aucunDocument");

            // si il n'y a aucune étiquette, afficher le modal d'ajout d'étiquette
            if (data.labels.length == 0)
                openModal("labelEditor");

            labels = data.labels;
            currentDocument = data.next_data.data;
            updateLabels();
            updateDocument(data.next_data.code);

        });
}

/**
 * Met à jour le document à étiqueter
 */
function updateDocument(code = 0) {

    if (code == 1) {
        // tous les documents ont été étiquetés
        etiquetageCompleted.style.display = "flex";
        etiquetageMain.style.display = "none";
    } else {
        // afficher le document
        imageViewerEl.style.backgroundImage = "url('" + staticPath + "data/" + modelId + "/" + currentDocument.id + "." + currentDocument.ext + "')";
        currentDocumentId.innerHTML = currentDocument.id;
    }
}

/**
 * Met à jour la liste des étiquettes
 */
const addLabel = (label, container) => {
    const labelElement = document.createElement("div");
    labelElement.classList.add("label");
    labelElement.innerText = label;
    container.appendChild(labelElement);
    if (container == labelsList) labelElement.addEventListener("click", () => selectLabel(labelElement));
}
function updateLabels(updateEditor = false) {

    if (updateEditor) {
        labelsListEditor.innerHTML = "";
        labels.forEach((l) => addLabel(l, labelsListEditor));
    }

    labelsList.innerHTML = "";
    labels.forEach((l) => addLabel(l, labelsList));

}

// ajouter/retirer une étiquette du document courrant
function selectLabel(labelElement) {

    if (labelElement.classList.contains("selected")) {
        labelElement.classList.remove("selected");
        selectedLabels.splice(selectedLabels.indexOf(labelElement.innerText), 1);
    } else {
        labelElement.classList.add("selected");
        selectedLabels.push(labelElement.innerText);
    }

    if (selectedLabels.length > 0) confirmButton.classList.add('valid');
    else confirmButton.classList.remove('valid');

}

// Ajouter une étiquette
leditorAddLabelButton.addEventListener("click", () => {

    const labelName = leditorAddLabelInput.value;
    if (labelName == "") return alert("Vous devez entrer un nom pour l'étiquette");

    addLabel(labelName, labelsListEditor);

    // envoyer une requete POST à l'API
    fetch('/api/models/' + modelId + '/labelling', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            labels: [labelName]
        })
    }).then(response => response.json())
        .then(data => {

            leditorAddLabelInput.value = "";
            labels.push([labelName, data.label_ids[0]]);
            addLabel(labelName, labelsList);

            if (labels.length > 1) labelEditorValider.style.display = "block";

        });

});

addLabelNextStepButton.addEventListener("click", () => {
    document.getElementById("labelEditor_1").style.display = "none";
    document.getElementById("labelEditor_2").style.display = "block";
    updateLabels(true);
    if (labels.length > 1) labelEditorValider.style.display = "block";
});

// valider l'étiquetage
confirmButton.addEventListener("click", () => {
    if (selectLabel.length == 0) return;
    fetch('/api/models/' + modelId + '/data/' + currentDocument.id + '/labels', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            labels: selectedLabels
        })
    }).then(response => response.json())
        .then(data => {

            // déselectionner tous les labels
            selectedLabels = [];
            confirmButton.classList.remove('valid')
            labelsList.childNodes.forEach((l) => {
                if (l.classList.contains("selected")) l.classList.remove("selected");
            });

            // charger le nouveau document
            currentDocument = data.next_data.data;
            updateDocument(data.next_data.code);

        });
});