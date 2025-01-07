import dialogPolyfill from 'dialog-polyfill';
import { _ } from './utils/i18n.js';

export function initModal(modalNode, openButtons, closeButtons, closeCallback = () => { }) {
    dialogPolyfill.registerDialog(modalNode);

    openButtons.forEach(button => {
        button.addEventListener("click", () => {
            modalNode.showModal();
        });
    });

    const modalHideAnimationEndCallback = () => {
        modalNode.classList.remove('hide');
        modalNode.close();
        modalNode.removeEventListener('webkitAnimationEnd', modalHideAnimationEndCallback, false);
        closeCallback();
    }

    const hideModal = () => {
        modalNode.classList.add('hide');
        modalNode.addEventListener('webkitAnimationEnd', modalHideAnimationEndCallback, false);
    }

    closeButtons.forEach(button => {
        button.addEventListener("click", (e) => {
            e.preventDefault();
            hideModal();
        });
    })

    modalNode.addEventListener("click", (e) => {
        var rect = modalNode.getBoundingClientRect();
        var minX = rect.left + modalNode.clientLeft;
        var minY = rect.top + modalNode.clientTop;
        if (e.clientX !== 0 && e.clientY !== 0 && 
            ((e.clientX < minX || e.clientX >= minX + modalNode.clientWidth) ||
            (e.clientY < minY || e.clientY >= minY + modalNode.clientHeight))) {
            hideModal();
        }
    });

    return hideModal;
}

export function generateModal(title, content, closeCallback = () => {}) {
    const modal = document.createElement("dialog");
    modal.className = "modal fit";
    const modalTitle = document.createElement("div");
    modalTitle.className = "modalHeader";
    modalTitle.innerHTML = title;
    modal.appendChild(modalTitle);
    const modalBody = document.createElement("div");
    modalBody.className = "modalBody text";
    modalBody.innerHTML = content;
    modal.appendChild(modalBody);
    const modalFooter = document.createElement("div");
    modalFooter.className = "modalFooter";
    modal.appendChild(modalFooter);
    const closeButton = document.createElement("button");
    closeButton.className = "button textButton shade";
    closeButton.innerHTML = `<span>${_("Close")}</span>`;
    modalFooter.appendChild(closeButton);

    initModal(modal, [], [closeButton], () => {
        modal.remove();
        closeCallback();
    });

    document.body.appendChild(modal);
    modal.showModal();
}
