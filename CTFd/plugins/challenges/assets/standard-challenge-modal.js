window.challenge.data = undefined;

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


window.challenge.submit = function(cb, preview){
    var chal_id = $('#chal-id').val();
    var answer = $('#answer-input').val();
    var nonce = $('#nonce').val();

    var url = "/api/v1/submissions";
    // if (preview) {
    //     url = "/admin/chal/";
    // }

    $.post(script_root + url, {
        challenge_id: chal_id,
        submission: answer,
        nonce: nonce
    }, function (data) {
        cb(data);
    });
};