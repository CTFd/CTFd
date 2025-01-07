var socket = io.connect(
    window.location.protocol + '//' + document.domain + ':' + location.port,
    {
        path: script_root + '/socket.io'
    }
);

socket.on('notification', function (data) {
    ezal({
        title: data.title,
        body: data.content,
        button: "Got it!"
    });
});