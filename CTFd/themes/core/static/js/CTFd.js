var CTFd = (function () {

    var urlRoot = '';

    var challenges = {
        all: function(){
            return fetch(urlRoot + '/api/v1/challenges')
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    return data;
                });
        },
        get: function(challengeId){
            return fetch(urlRoot + '/api/v1/challenges/' + challengeId)
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    data.solves = function () {
                        return fetch(urlRoot + '/api/v1/challenges/' + this.id + '/solves')
                            .then(function (response) {
                                return response.json();
                            }).then(function (data) {
                                return data;
                            });
                    };
                    return data;
                });
        },
        types: function(){
            return fetch(urlRoot + '/api/v1/challenges/types')
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    return data;
                });
        },
        solves: function () {
            return fetch(urlRoot + '/api/v1/statistics/challenges/solves')
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    return data;
                });
        }
    };

    var scoreboard = function() {
        return fetch(urlRoot + '/api/v1/scoreboard')
            .then(function (response) {
                return response.json();
            }).then(function (data) {
                return data;
            });
    };

    var teams = {
        all: function () {
            return fetch(urlRoot + '/api/v1/teams')
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    return data;
                });
        },
        get: function (teamId) {
            return fetch(urlRoot + '/api/v1/teams/' + teamId)
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    data.solves = function () {

                    };
                    data.fails = function () {

                    };
                    data.awards = function () {

                    };
                    return data;
                });
        },
    };

    var users = {
        all: function () {
            return fetch(urlRoot + '/api/v1/users')
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    return data;
                });
        },
        get: function (userId) {
            return fetch(urlRoot + '/api/v1/users/' + userId)
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    data.solves = function () {

                    };
                    data.fails = function () {

                    };
                    data.awards = function () {

                    };
                    return data;
                });
        },
    };

    return {
        challenges: challenges,
        scoreboard: scoreboard,
        teams: teams,
        users: users,
    };
})();