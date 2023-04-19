const nextButton = document.getElementById('next_btn');

if (typeof maxStepNb != 'undefined') {

    // Masquer/afficher le contenu de l'étape suivante
    let currentStep = 1;
    nextButton.addEventListener('click', () => {

        currentStep += 1;
        document.getElementById(`step_${currentStep - 1}`).classList.remove('active');
        document.getElementById(`step_${currentStep}`).classList.add('active');

        // Lorsque l'on arrive à la dernière étape, on cache le bouton
        if (currentStep === maxStepNb) nextButton.style.display = 'none';

    });

}

let selectedType = 1;
const typeInput = document.getElementById('type_input');
document.querySelectorAll('[data-type]').forEach((e) => {

    e.addEventListener('click', () => {
        e.classList.toggle('active');
        document.getElementById(`select_type_${selectedType}`).classList.remove('active');
        document.getElementById(`type_${selectedType}`).classList.remove('active');
        document.getElementById(`type_${e.dataset.type}`).classList.add('active');
        typeInput.value = e.dataset.type;
        selectedType = e.dataset.type;
    })

});