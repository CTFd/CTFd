var wc = new WindowController();

var sound = new Howl({
    src: [script_root + "/themes/core/static/sounds/notification.mp3"]
});

function connect() {
    window.ctfEventSource = new EventSource(script_root + "/events");

    window.ctfEventSource.addEventListener('notification', function (event) {
        var data = JSON.parse(event.data);
        wc.broadcast('notification', data);
        render(data);
    }, false);
}

function disconnect() {
    if (window.ctfEventSource) {
        window.ctfEventSource.close();
    }
}

function render(data) {
    ezal({
        title: data.title,
        body: data.content,
        button: "Got it!"
    });
    sound.play();
}

wc.notification = function(data) {
    render(data);
};

wc.masterDidChange = function () {
    console.log(this.isMaster);
    if (this.isMaster) {
        connect();
    } else {
        disconnect();
    }
};
