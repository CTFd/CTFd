var source = new EventSource(script_root + "/events");

source.addEventListener('notification', function (event) {
    var data = JSON.parse(event.data);
    ezal({
        title: data.title,
        body: data.content,
        button: "Got it!"
    });
}, false);