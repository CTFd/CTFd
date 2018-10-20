var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);

socket.on('announcement', function (data) {
    ezal({
        title: "Announcement!",
        body: data.message,
        button: "Got it!"
    });
});