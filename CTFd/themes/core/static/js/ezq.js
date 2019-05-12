var modal =
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

var progress =
  '<div class="progress">' +
  '  <div class="progress-bar progress-bar-success progress-bar-striped progress-bar-animated" role="progressbar" style="width: {0}%">' +
  "  </div>" +
  "</div>";

var error_template =
  '<div class="alert alert-danger alert-dismissable" role="alert">\n' +
  '  <span class="sr-only">Error:</span>\n' +
  "  {0}\n" +
  '  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>\n' +
  "</div>";

var success_template =
  '<div class="alert alert-success alert-dismissable submit-row" role="alert">\n' +
  "  <strong>Success!</strong>\n" +
  "  {0}\n" +
  '  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>\n' +
  "</div>";

function ezal(args) {
  var res = modal.format(args.title, args.body);
  var obj = $(res);
  var button = '<button type="button" class="btn btn-primary" data-dismiss="modal">{0}</button>'.format(
    args.button
  );

  obj.find(".modal-footer").append(button);
  $("main").append(obj);

  obj.modal("show");

  $(obj).on("hidden.bs.modal", function(e) {
    $(this).modal("dispose");
  });

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

  obj.find(".modal-footer").append(deny);
  obj.find(".modal-footer").append(confirm);

  $("main").append(obj);

  $(obj).on("hidden.bs.modal", function(e) {
    $(this).modal("dispose");
  });

  $(confirm).click(function() {
    args.success();
  });

  obj.modal("show");

  return obj;
}

function ezpg(args) {
  if (args.target) {
    var obj = $(args.target);
    var pbar = obj.find(".progress-bar");
    pbar.css("width", args.width + "%");
    return obj;
  }
  var bar = progress.format(args.width);
  var res = modal.format(args.title, bar);

  var obj = $(res);
  $("main").append(obj);
  obj.modal("show");

  return obj;
}

function ezbadge(args) {
  var type = args.type;
  var body = args.body;
  var tpl = undefined;
  if (type === "success") {
    tpl = success_template;
  } else if (type === "error") {
    tpl = error_template;
  }

  tpl = tpl.format(body);
  var obj = $(tpl);
  return obj;
}
