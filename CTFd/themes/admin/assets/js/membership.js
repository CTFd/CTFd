import $ from "jquery";
import CTFd from "./compat/CTFd";
import { ezAlert } from "./compat/ezq";

// groups: { [name]: { label, add(box) -> Promise<bool>, remove(box) -> Promise<bool> } }
export function setupMembership(groups) {
  let saving = false;
  const boxes = (group) => $(`input[data-membership="${group}"]`);
  const rows = (group) =>
    $(`table[data-membership-table="${group}"] tr[data-membership-row]`);
  const visibleBoxes = (group) =>
    rows(group).filter(":visible").find(`input[data-membership="${group}"]`);

  function diff(group) {
    const add = [];
    const remove = [];
    boxes(group).each(function () {
      const initial = this.getAttribute("data-initial") === "1";
      if (this.checked !== initial) (this.checked ? add : remove).push(this);
    });
    return { add, remove };
  }

  function isDirty() {
    return Object.keys(groups).some((group) => {
      const { add, remove } = diff(group);
      return add.length || remove.length;
    });
  }

  function updateSelectAll(group) {
    const visible = visibleBoxes(group);
    const checked = visible.filter(":checked").length;
    $(`input[data-membership-select-all="${group}"]`).prop({
      checked: visible.length > 0 && checked === visible.length,
      indeterminate: checked > 0 && checked < visible.length,
    });
  }

  function refresh() {
    const parts = [];
    for (const [group, { label }] of Object.entries(groups)) {
      const { add, remove } = diff(group);
      if (add.length || remove.length) {
        parts.push(`${label} +${add.length} / −${remove.length}`);
      }
      $(`[data-membership-count="${group}"]`).text(
        boxes(group).filter(":checked").length,
      );
      updateSelectAll(group);
    }
    $("#membership-summary").text(parts.join(" · "));
    $("#membership-save-bar").toggle(parts.length > 0);
  }

  // Filters on current checkbox state, re-applied only when the filter or search changes
  function applyFilter(group) {
    const q = ($(`input[data-membership-search="${group}"]`).val() || "")
      .trim()
      .toLowerCase();
    const mode =
      $(`input[data-membership-filter="${group}"]:checked`).val() || "all";
    let shown = 0;
    rows(group).each(function () {
      const checked = $(this).find(`input[data-membership="${group}"]`)[0]
        .checked;
      const visible =
        (!q || this.getAttribute("data-search").includes(q)) &&
        (mode === "all" || (mode === "in") === checked);
      $(this).toggle(visible);
      if (visible) shown++;
    });
    $(
      `table[data-membership-table="${group}"] tr[data-membership-empty]`,
    ).toggle(shown === 0);
    updateSelectAll(group);
  }

  function discard() {
    for (const group of Object.keys(groups)) {
      boxes(group).each(function () {
        this.checked = this.getAttribute("data-initial") === "1";
      });
      applyFilter(group);
    }
    refresh();
  }

  function save() {
    const reqs = [];
    for (const [group, { add, remove }] of Object.entries(groups)) {
      const changes = diff(group);
      reqs.push(...changes.add.map((box) => add(box).catch(() => false)));
      reqs.push(...changes.remove.map((box) => remove(box).catch(() => false)));
    }

    saving = true;
    $("#membership-save, #membership-discard").prop("disabled", true);
    Promise.all(reqs).then((results) => {
      const failed = results.filter((ok) => !ok).length;
      if (failed) {
        ezAlert({
          title: "Error",
          body: `${failed} of ${results.length} changes failed.`,
          button: "OK",
          success: function () {
            window.location.reload();
          },
        });
      } else {
        window.location.reload();
      }
    });
  }

  for (const group of Object.keys(groups)) {
    boxes(group).on("change", refresh);
    rows(group).on("click", function (event) {
      if ($(event.target).closest("a, input, label").length) return;
      const box = $(this).find(`input[data-membership="${group}"]`)[0];
      box.checked = !box.checked;
      refresh();
    });
    $(`input[data-membership-select-all="${group}"]`).on("change", function () {
      visibleBoxes(group).prop("checked", this.checked);
      refresh();
    });
    $(`input[data-membership-search="${group}"]`).on("input", () =>
      applyFilter(group),
    );
    $(`input[data-membership-filter="${group}"]`).on("change", () =>
      applyFilter(group),
    );
    updateSelectAll(group);
  }
  $("#membership-discard").click(discard);
  $("#membership-save").click(save);

  window.addEventListener("beforeunload", function (event) {
    if (saving || !isDirty()) return;
    event.preventDefault();
    event.returnValue = "";
  });
}

// Resolves to whether the request succeeded
export function send(path, method, body) {
  return CTFd.fetch(path, {
    method: method,
    credentials: "same-origin",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  }).then((response) => response.ok);
}
