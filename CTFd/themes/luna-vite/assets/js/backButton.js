export default function BackButtonInit() {
    const backButton = document.getElementById("backButton");
    if (backButton) {
        backButton.addEventListener("click", () => {
            if (window.history.length > 1) window.history.back();
            else window.location.href = "/";
        });
    }
}