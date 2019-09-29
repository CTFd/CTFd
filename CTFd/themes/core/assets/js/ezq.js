import "bootstrap/js/dist/modal";
import $ from "jquery";

const modalTpl =
  '<div class="modal fade" tabindex="-1" role="dialog">' +
  '  <div class="modal-dialog" role="document">' +
  '    <div class="modal-content">' +
  '      <div class="modal-header">' +
  '        <h5 class="modal-title">{0}</h5>' +
  '        <button type="button" class="close" data-dismiss="modal" aria-label="Close">' +
  '          <span aria-hidden="true">&times;</span>' +
  "        </button>" +
  "      </div>" +
  '      <div class="modal-body">' +
  "        <p>{1}</p>" +
  "      </div>" +
  '      <div class="modal-footer">' +
  "      </div>" +
  "    </div>" +
  "  </div>" +
  "</div>";

<<<<<<< HEAD:CTFd/themes/core/assets/js/ezq.js
const progressTpl =
=======
  var toast =
 ' <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">'+
  '<div class="toast-header">'+
   ' <img src="..." class="rounded mr-2" alt="...">'+
   '<strong class="mr-auto">{0}</strong>'+
   '<small>11 mins ago</small>'+
   '<button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">'+
   '  <span aria-hidden="true">&times;</span>'+
   '</button>'+
   '</div>'+
   '<div class="toast-body">'+
   '{1}'+
   '</div>'+
   '</div>';
  

var progress =
>>>>>>> feature-toast:CTFd/themes/core/static/js/ezq.js
  '<div class="progress">' +
  '  <div class="progress-bar progress-bar-success progress-bar-striped progress-bar-animated" role="progressbar" style="width: {0}%">' +
  "  </div>" +
  "</div>";

const errorTpl =
  '<div class="alert alert-danger alert-dismissable" role="alert">\n' +
  '  <span class="sr-only">Error:</span>\n' +
  "  {0}\n" +
  '  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>\n' +
  "</div>";

const successTpl =
  '<div class="alert alert-success alert-dismissable submit-row" role="alert">\n' +
  "  <strong>Success!</strong>\n" +
  "  {0}\n" +
  '  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>\n' +
  "</div>";

const buttonTpl =
  '<button type="button" class="btn btn-primary" data-dismiss="modal">{0}</button>';
const noTpl =
  '<button type="button" class="btn btn-danger" data-dismiss="modal">No</button>';
const yesTpl =
  '<button type="button" class="btn btn-primary" data-dismiss="modal">Yes</button>';

export function ezAlert(args) {
  const modal = modalTpl.format(args.title, args.body);
  const obj = $(modal);
  const button = buttonTpl.format(args.button);

  obj.find(".modal-footer").append(button);
  $("main").append(obj);

  obj.modal("show");

  $(obj).on("hidden.bs.modal", function() {
    $(this).modal("dispose");
  });

  return obj;
}

<<<<<<< HEAD:CTFd/themes/core/assets/js/ezq.js
export function ezQuery(args) {
  const modal = modalTpl.format(args.title, args.body);
  const obj = $(modal);
=======
function ezt(args) {
  var res = toast.format(args.title, args.body);
  var obj = $(res);
  obj.toast('show');
  return obj;
}

function ezq(args) {
  var res = modal.format(args.title, args.body);
  var obj = $(res);
  var deny =
    '<button type="button" class="btn btn-danger" data-dismiss="modal">No</button>';
  var confirm = $(
    '<button type="button" class="btn btn-primary" data-dismiss="modal">Yes</button>'
  );
>>>>>>> feature-toast:CTFd/themes/core/static/js/ezq.js

  const yes = $(yesTpl);
  const no = $(noTpl);

  obj.find(".modal-footer").append(no);
  obj.find(".modal-footer").append(yes);

  $("main").append(obj);

  $(obj).on("hidden.bs.modal", function() {
    $(this).modal("dispose");
  });

  $(yes).click(function() {
    args.success();
  });

  obj.modal("show");

  return obj;
}

export function ezProgressBar(args) {
  if (args.target) {
    const obj = $(args.target);
    const pbar = obj.find(".progress-bar");
    pbar.css("width", args.width + "%");
    return obj;
  }

  const progress = progressTpl.format(args.width);
  const modal = modalTpl.format(args.title, progress);

  const obj = $(modal);
  $("main").append(obj);

  return obj.modal("show");
}

export function ezBadge(args) {
  const mapping = {
    success: successTpl,
    error: errorTpl
  };

  const tpl = mapping[args.type].format(args.body);
  return $(tpl);
}
