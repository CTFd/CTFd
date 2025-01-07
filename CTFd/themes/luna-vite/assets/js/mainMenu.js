import { initModal } from './modal.js';

export default function MainMenuInit() {
    const menuButton = document.getElementById("mainMenuButton");

    if (menuButton) {
        const menuModal = document.getElementById("mainMenuModal");
        const menuClose = document.getElementById("mainMenuClose");

        initModal(menuModal, [menuButton], [menuClose]);

        const titleButton = document.getElementById("mainMenuTitleBtn");
        titleButton.addEventListener("click", (evt) => {
            window.localStorage.setItem("luna_showTitleScreen", "true");
        });
    }
}
