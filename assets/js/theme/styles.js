export default () => {
  document.querySelectorAll(".form-control").forEach($el => {
    $el.addEventListener("onfocus", () => {
      $el.classList.remove("input-filled-invalid");
      $el.classList.add("input-filled-valid");
    });

    $el.addEventListener("onblur", () => {
      if ($el.nodeValue === "") {
        $el.classList.remove("input-filled-valid");
        $el.classList.remove("input-filled-invalid");
      }
    });

    if ($el.nodeValue) {
      $el.classList.add("input-filled-valid");
    }
  });

  document.querySelectorAll(".page-select").forEach($el => {
    if ($el.nodeValue) {
      const url = new URL(window.location);
      url.searchParams.set("page", $el.nodeValue);
      window.location.href = url.toString();
    }
  });
};
