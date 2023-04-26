const modalContainer = document.getElementById('modalContainer');

function openModal(modalName) {
    const modal = document.getElementById(`modal_${modalName}`);
    modal.classList.add('actif');
    modalContainer.style.display = 'flex';
}

function closeModal(modalName) {
    const modal = document.getElementById(`modal_${modalName}`);
    modal.classList.remove('actif');
    modalContainer.style.display = 'none';
}