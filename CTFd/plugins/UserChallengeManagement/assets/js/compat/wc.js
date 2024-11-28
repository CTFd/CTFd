import $ from "jquery";

// https://gist.github.com/neilj/4146038
// https://fastmail.blog/2012/11/26/inter-tab-communication-using-local-storage/
export function WindowController() {
  this.id = Math.random();
  this.isMaster = false;
  this.others = {};

  window.addEventListener("storage", this, false);
  window.addEventListener("unload", this, false);

  this.broadcast("hello");

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

  window.removeEventListener("storage", this, false);
  window.removeEventListener("unload", this, false);

  this.broadcast("bye");
};

WindowController.prototype.handleEvent = function (event) {
  if (event.type === "unload") {
    this.destroy();
  } else if (event.key === "broadcast") {
    try {
      var data = JSON.parse(event.newValue);
      if (data.id !== this.id) {
        this[data.type](data);
      }
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error);
    }
  }
};

WindowController.prototype.sendPing = function () {
  this.broadcast("ping");
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

WindowController.prototype.check = function (_event) {
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

WindowController.prototype.masterDidChange = function () {};

WindowController.prototype.broadcast = function (type, data) {
  var event = {
    id: this.id,
    type: type,
  };
  for (var x in data) {
    event[x] = data[x];
  }
  try {
    localStorage.setItem("broadcast", JSON.stringify(event));
  } catch (error) {
    // eslint-disable-next-line no-console
    console.log(error);
  }
};

// https://gist.github.com/0x263b/2bdd90886c2036a1ad5bcf06d6e6fb37
export function colorHash(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
    hash = hash & hash;
  }
  // Range calculation
  // diff = max - min;
  // x = ((hash % diff) + diff) % diff;
  // return x + min;
  // Calculate HSL values
  // Range from 0 to 360
  let h = ((hash % 360) + 360) % 360;
  // Range from 75 to 100
  let s = (((hash % 25) + 25) % 25) + 75;
  // Range from 40 to 60
  let l = (((hash % 20) + 20) % 20) + 40;
  return `hsl(${h}, ${s}%, ${l}%)`;
}

const storage = window.localStorage;
const counter_key = "unread_notifications";

export function init_notification_counter() {
  let count = storage.getItem(counter_key);
  if (count === null) {
    storage.setItem(counter_key, 0);
  } else {
    if (count > 0) {
      $(".badge-notification").text(count);
    }
  }
}

export function set_notification_counter(count) {
  storage.setItem(counter_key, count);
}

export function inc_notification_counter() {
  let count = storage.getItem(counter_key) || 0;
  storage.setItem(counter_key, ++count);
  $(".badge-notification").text(count);
}

export function dec_notification_counter() {
  let count = storage.getItem(counter_key) || 0;
  if (count > 0) {
    storage.setItem(counter_key, --count);
    $(".badge-notification").text(count);
  }
  // Always clear if count is 0
  if (count == 0) {
    clear_notification_counter();
  }
}

export function clear_notification_counter() {
  storage.setItem(counter_key, 0);
  $(".badge-notification").empty();
}
