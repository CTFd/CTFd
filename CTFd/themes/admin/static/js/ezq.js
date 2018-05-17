var modal = '<div class="modal fade" tabindex="-1" role="dialog">' +
    '  <div class="modal-dialog" role="document">' +
    '    <div class="modal-content">' +
    '      <div class="modal-header">' +
    '        <h5 class="modal-title">\{0\}</h5>' +
    '        <button type="button" class="close" data-dismiss="modal" aria-label="Close">' +
    '          <span aria-hidden="true">&times;</span>' +
    '        </button>' +
    '      </div>' +
    '      <div class="modal-body">' +
    '        <p>\{1\}</p>' +
    '      </div>' +
    '      <div class="modal-footer">' +
    '      </div>' +
    '    </div>' +
    '  </div>' +
    '</div>';

var progress = '<div class="progress">' +
    '  <div class="progress-bar progress-bar-success progress-bar-striped progress-bar-animated" role="progressbar" style="width: \{0\}%">' +
    '  </div>' +
    '</div>';

function ezal(args){
    var res = modal.format(args.title, args.body);
    var obj = $(res);
    var button = '<button type="button" class="btn btn-primary" data-dismiss="modal">{0}</button>'.format(args.button);

    obj.find('.modal-footer').append(button);
    $('main').append(obj);

    obj.modal('show');

    $(obj).on('hidden.bs.modal', function (e) {
        $(this).modal('dispose');
    });

    return obj;
}

function ezq(args){
    var res = modal.format(args.title, args.body);
    var obj = $(res);
    var deny = '<button type="button" class="btn btn-danger" data-dismiss="modal">No</button>';
    var confirm = $('<button type="button" class="btn btn-primary" data-dismiss="modal">Yes</button>');

    obj.find('.modal-footer').append(deny);
    obj.find('.modal-footer').append(confirm);

    $('main').append(obj);

    $(obj).on('hidden.bs.modal', function (e) {
        $(this).modal('dispose');
    });

    $(confirm).click(function(){
        args.success();
    });

    obj.modal('show');

    return obj;
}

function ezpg(args){
    var bar = progress.format(args.width);
    var res = modal.format(args.title, bar);

    var obj = $(res);
    $('main').append(obj);

    return obj.modal('show');
}