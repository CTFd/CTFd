$('#submit-key').click(function (e) {
    submitkey($('#chal-id').val(), $('#answer-input').val(), $('#nonce').val())
});