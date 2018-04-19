window.challenge.renderer = new markdownit({
    html: true,
});

window.challenge.preRender = function(){

};

window.challenge.render = function(markdown){
    return window.challenge.renderer.render(markdown);
};


window.challenge.postRender = function(){

};


window.challenge.submit = function(cb){
    var chal_id = $('#chal-id').val();
    var answer = $('#answer-input').val();
    var nonce = $('#nonce').val();

    $.post(script_root + "/chal/" + chal_id, {
        key: answer,
        nonce: nonce
    }, function (data) {
        cb(data);
    });
};