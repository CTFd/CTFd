import $ from "jquery";

export function htmlEntities(string) {
  return $("<div/>")
    .text(string)
    .html();
}
