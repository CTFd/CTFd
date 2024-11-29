import $ from "jquery";

$.fn.serializeJSON = function (omit_nulls) {
  let params = {};
  let form = $(this);
  let values = form.serializeArray();

  values = values.concat(
    form
      .find("input[type=checkbox]:checked")
      .map(function () {
        return { name: this.name, value: true };
      })
      .get(),
  );
  values = values.concat(
    form
      .find("input[type=checkbox]:not(:checked)")
      .map(function () {
        return { name: this.name, value: false };
      })
      .get(),
  );
  values.map((x) => {
    if (omit_nulls) {
      if (x.value !== null && x.value !== "") {
        params[x.name] = x.value;
      } else {
        let input = form.find(`:input[name='${x.name}']`);
        if (input.data("initial") !== input.val()) {
          params[x.name] = x.value;
        }
      }
    } else {
      params[x.name] = x.value;
    }
  });
  return params;
};
