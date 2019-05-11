//http://stackoverflow.com/a/1186309
$.fn.serializeObject = function() {
  var o = {};
  var a = this.serializeArray();
  $.each(a, function() {
    if (o[this.name] !== undefined) {
      if (!o[this.name].push) {
        o[this.name] = [o[this.name]];
      }
      o[this.name].push(this.value || "");
    } else {
      o[this.name] = this.value || "";
    }
  });
  return o;
};

$.fn.serializeJSON = function(omit_nulls) {
  var params = {};
  var form = $(this);
  var values = form.serializeArray();

  values = values.concat(
    form
      .find("input[type=checkbox]:checked")
      .map(function() {
        return { name: this.name, value: true };
      })
      .get()
  );
  values = values.concat(
    form
      .find("input[type=checkbox]:not(:checked)")
      .map(function() {
        return { name: this.name, value: false };
      })
      .get()
  );
  values.map(function(x) {
    if (omit_nulls) {
      if (x.value !== null && x.value !== "") {
        params[x.name] = x.value;
      }
    } else {
      params[x.name] = x.value;
    }
  });
  return params;
};

//http://stackoverflow.com/a/2648463 - wizardry!
String.prototype.format = String.prototype.f = function() {
  var s = this,
    i = arguments.length;

  while (i--) {
    s = s.replace(new RegExp("\\{" + i + "\\}", "gm"), arguments[i]);
  }
  return s;
};

//http://stackoverflow.com/a/7616484
String.prototype.hashCode = function() {
  var hash = 0,
    i,
    chr,
    len;
  if (this.length == 0) return hash;
  for (i = 0, len = this.length; i < len; i++) {
    chr = this.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
};

function colorhash(str) {
  var hash = 0;
  for (var i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  var colour = "#";
  for (var i = 0; i < 3; i++) {
    var value = (hash >> (i * 8)) & 0xff;
    colour += ("00" + value.toString(16)).substr(-2);
  }
  return colour;
}

function htmlentities(string) {
  return $("<div/>")
    .text(string)
    .html();
}

function cumulativesum(arr) {
  var result = arr.concat();
  for (var i = 0; i < arr.length; i++) {
    result[i] = arr.slice(0, i + 1).reduce(function(p, i) {
      return p + i;
    });
  }
  return result;
}

// http://stepansuvorov.com/blog/2014/04/jquery-put-and-delete/
jQuery.each(["patch", "put", "delete"], function(i, method) {
  jQuery[method] = function(url, data, callback, type) {
    if (jQuery.isFunction(data)) {
      type = type || callback;
      callback = data;
      data = undefined;
    }

    return jQuery.ajax({
      url: url,
      type: method,
      dataType: type,
      data: data,
      success: callback
    });
  };
});
