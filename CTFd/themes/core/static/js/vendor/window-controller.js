// https://gist.github.com/neilj/4146038
// https://fastmail.blog/2012/11/26/inter-tab-communication-using-local-storage/
function WindowController() {
    this.id = Math.random();
    this.isMaster = false;
    this.others = {};

    window.addEventListener('storage', this, false);
    window.addEventListener('unload', this, false);

    this.broadcast('hello');

    var that = this;
    var check = function check() {
        that.check();
        that._checkTimeout = setTimeout(check, 9000);
    };
    var ping = function ping() {
        that.sendPing();
        that._pingTimeout = setTimeout(ping, 17000);
    };
    this._checkTimeout = setTimeout(check, 500);
    this._pingTimeout = setTimeout(ping, 17000);
}

WindowController.prototype.destroy = function () {
    clearTimeout(this._pingTimeout);
    clearTimeout(this._checkTimeout);

    window.removeEventListener('storage', this, false);
    window.removeEventListener('unload', this, false);

    this.broadcast('bye');
};

WindowController.prototype.handleEvent = function (event) {
    if (event.type === 'unload') {
        this.destroy();
    } else if (event.key === 'broadcast') {
        try {
            var data = JSON.parse(event.newValue);
            if (data.id !== this.id) {
                this[data.type](data);
            }
        } catch (error) {
        }
    }
};

WindowController.prototype.sendPing = function () {
    this.broadcast('ping');
};

WindowController.prototype.hello = function (event) {
    this.ping(event);
    if (event.id < this.id) {
        this.check();
    } else {
        this.sendPing();
    }
};

WindowController.prototype.ping = function (event) {
    this.others[event.id] = +new Date();
};

WindowController.prototype.bye = function (event) {
    delete this.others[event.id];
    this.check();
};

WindowController.prototype.check = function (event) {
    var now = +new Date(),
        takeMaster = true,
        id;
    for (id in this.others) {
        if (this.others[id] + 23000 < now) {
            delete this.others[id];
        } else if (id < this.id) {
            takeMaster = false;
        }
    }
    if (this.isMaster !== takeMaster) {
        this.isMaster = takeMaster;
        this.masterDidChange();
    }
};

WindowController.prototype.masterDidChange = function () {
};

WindowController.prototype.broadcast = function (type, data) {
    var event = {
        id: this.id,
        type: type
    };
    for (var x in data) {
        event[x] = data[x];
    }
    try {
        localStorage.setItem('broadcast', JSON.stringify(event));
    } catch (error) {
        console.log(error);
    }
};
