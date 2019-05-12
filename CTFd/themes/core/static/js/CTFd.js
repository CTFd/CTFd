var CTFd = (function() {
  var options = {
    urlRoot: "",
    csrfNonce: "",
    start: null,
    end: null
  };

  var challenges = {};

  var scoreboard = function() {};

  var teams = {};

  var users = {};

  var fetch = function(url, options) {
    if (options === undefined) {
      options = {
        method: "GET",
        credentials: "same-origin",
        headers: {}
      };
    }
    url = this.options.urlRoot + url;

    if (options.headers === undefined) {
      options.headers = {};
    }
    options.credentials = "same-origin";
    options.headers["Accept"] = "application/json";
    options.headers["Content-Type"] = "application/json";
    options.headers["CSRF-Token"] = this.options.csrfNonce;

    return window.fetch(url, options);
  };

  return {
    challenges: challenges,
    scoreboard: scoreboard,
    teams: teams,
    users: users,
    fetch: fetch,
    options: options
  };
})();
