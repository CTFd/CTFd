var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);

socket.on('announcement', function (data) {
    ezal({
        title: data.title,
        body: data.content,
        button: "Got it!"
    });
});