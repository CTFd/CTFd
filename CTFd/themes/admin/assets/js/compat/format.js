//http://stackoverflow.com/a/2648463 - wizardry!
String.prototype.format = String.prototype.f = function () {
  let s = this,
    i = arguments.length;

  while (i--) {
    s = s.replace(new RegExp("\\{" + i + "\\}", "gm"), arguments[i]);
  }
  return s;
};
