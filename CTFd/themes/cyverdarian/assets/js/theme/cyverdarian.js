// Resolve active navigation using URL objects so subdirectory deployments work.
const currentPath = window.location.pathname.replace(/\/$/, "") || "/";
document.querySelectorAll(".navbar a.nav-link").forEach(link => {
  if (
    new URL(link.href).pathname.replace(/\/$/, "") === currentPath.replace(/\/$/, "")
  ) {
    link.setAttribute("aria-current", "page");
  }
});
