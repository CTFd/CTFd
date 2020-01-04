import Q from "q";
import { API } from "./api";

function mergeQueryParams(parameters, queryParameters) {
  return { ...parameters, ...queryParameters };
}

function serializeQueryParams(parameters) {
  let str = [];
  for (let p in parameters) {
    if (parameters.hasOwnProperty(p)) {
      str.push(encodeURIComponent(p) + "=" + encodeURIComponent(parameters[p]));
    }
  }
  return str.join("&");
}

API.prototype.requestRaw = function(
  method,
  url,
  parameters,
  body,
  headers,
  queryParameters,
  form,
  deferred
) {
  const queryParams =
    queryParameters && Object.keys(queryParameters).length
      ? serializeQueryParams(queryParameters)
      : null;
  const urlWithParams = url + (queryParams ? "?" + queryParams : "");

  if (body && !Object.keys(body).length) {
    body = undefined;
  }

  fetch(urlWithParams, {
    method,
    headers,
    body: body
  })
    .then(response => {
      return response.json();
    })
    .then(body => {
      deferred.resolve(body);
    })
    .catch(error => {
      deferred.reject(error);
    });
};

API.prototype.patch_user_public = function(parameters, body) {
  if (parameters === undefined) {
    parameters = {};
  }
  let deferred = Q.defer();
  let domain = this.domain,
    path = "/users/{user_id}";
  let queryParameters = {},
    headers = {},
    form = {};

  headers["Accept"] = ["application/json"];
  headers["Content-Type"] = ["application/json"];

  path = path.replace("{user_id}", parameters["userId"]);

  if (parameters["userId"] === undefined) {
    deferred.reject(new Error("Missing required  parameter: userId"));
    return deferred.promise;
  }

  this.request(
    "PATCH",
    domain + path,
    parameters,
    body,
    headers,
    queryParameters,
    form,
    deferred
  );

  return deferred.promise;
};

API.prototype.patch_user_private = function(parameters, body) {
  if (parameters === undefined) {
    parameters = {};
  }
  let deferred = Q.defer();
  let domain = this.domain,
    path = "/users/me";
  let headers = {},
    form = {};

  headers["Accept"] = ["application/json"];
  headers["Content-Type"] = ["application/json"];

  this.request(
    "PATCH",
    domain + path,
    parameters,
    body,
    headers,
    {},
    form,
    deferred
  );

  return deferred.promise;
};
API.prototype.post_unlock_list = function(parameters, body) {
  let deferred = Q.defer();
  let domain = this.domain,
    path = "/unlocks";
  let headers = {},
    form = {};

  headers["Accept"] = ["application/json"];
  headers["Content-Type"] = ["application/json"];

  this.request(
    "POST",
    domain + path,
    parameters,
    body,
    headers,
    {},
    form,
    deferred
  );

  return deferred.promise;
};

API.prototype.post_notification_list = function(parameters, body) {
  if (parameters === undefined) {
    parameters = {};
  }
  let deferred = Q.defer();
  let domain = this.domain,
    path = "/notifications";
  let queryParameters = {},
    headers = {},
    form = {};

  headers["Accept"] = ["application/json"];
  headers["Content-Type"] = ["application/json"];

  this.request(
    "POST",
    domain + path,
    parameters,
    body,
    headers,
    queryParameters,
    form,
    deferred
  );

  return deferred.promise;
};

API.prototype.post_files_list = function(parameters, body) {
  let deferred = Q.defer();
  let domain = this.domain,
    path = "/files";
  let queryParameters = {},
    headers = {},
    form = {};

  headers["Accept"] = ["application/json"];
  headers["Content-Type"] = ["application/json"];

  this.requestRaw(
    "POST",
    domain + path,
    parameters,
    body,
    headers,
    queryParameters,
    form,
    deferred
  );

  return deferred.promise;
};

API.prototype.patch_config = function(parameters, body) {
  if (parameters === undefined) {
    parameters = {};
  }
  let deferred = Q.defer();
  let domain = this.domain,
    path = "/configs/{config_key}";
  let queryParameters = {},
    headers = {},
    form = {};

  headers["Accept"] = ["application/json"];
  headers["Content-Type"] = ["application/json"];

  path = path.replace("{config_key}", parameters["configKey"]);

  if (parameters["configKey"] === undefined) {
    deferred.reject(new Error("Missing required  parameter: configKey"));
    return deferred.promise;
  }

  this.request(
    "PATCH",
    domain + path,
    parameters,
    body,
    headers,
    queryParameters,
    form,
    deferred
  );

  return deferred.promise;
};

API.prototype.patch_config_list = function(parameters, body) {
  if (parameters === undefined) {
    parameters = {};
  }
  let deferred = Q.defer();
  let domain = this.domain,
    path = "/configs";
  let queryParameters = {},
    headers = {},
    form = {};

  headers["Accept"] = ["application/json"];
  headers["Content-Type"] = ["application/json"];

  queryParameters = mergeQueryParams(parameters, queryParameters);

  this.request(
    "PATCH",
    domain + path,
    parameters,
    body,
    headers,
    queryParameters,
    form,
    deferred
  );

  return deferred.promise;
};
API.prototype.post_tag_list = function(parameters, body) {
  if (parameters === undefined) {
    parameters = {};
  }
  let deferred = Q.defer();
  let domain = this.domain,
    path = "/tags";
  let queryParameters = {},
    headers = {},
    form = {};

  headers["Accept"] = ["application/json"];
  headers["Content-Type"] = ["application/json"];

  queryParameters = mergeQueryParams(parameters, queryParameters);

  this.request(
    "POST",
    domain + path,
    parameters,
    body,
    headers,
    queryParameters,
    form,
    deferred
  );

  return deferred.promise;
};
API.prototype.patch_team_public = function(parameters, body) {
  if (parameters === undefined) {
    parameters = {};
  }
  let deferred = Q.defer();
  let domain = this.domain,
    path = "/teams/{team_id}";
  let queryParameters = {},
    headers = {},
    form = {};

  headers["Accept"] = ["application/json"];
  headers["Content-Type"] = ["application/json"];

  path = path.replace("{team_id}", parameters["teamId"]);

  if (parameters["teamId"] === undefined) {
    deferred.reject(new Error("Missing required  parameter: teamId"));
    return deferred.promise;
  }

  queryParameters = mergeQueryParams(parameters, queryParameters);

  this.request(
    "PATCH",
    domain + path,
    parameters,
    body,
    headers,
    queryParameters,
    form,
    deferred
  );

  return deferred.promise;
};
API.prototype.post_challenge_attempt = function(parameters, body) {
  if (parameters === undefined) {
    parameters = {};
  }
  let deferred = Q.defer();
  let domain = this.domain,
    path = "/challenges/attempt";
  let queryParameters = {},
    headers = {},
    form = {};

  headers["Accept"] = ["application/json"];
  headers["Content-Type"] = ["application/json"];

  queryParameters = mergeQueryParams(parameters, queryParameters);

  this.request(
    "POST",
    domain + path,
    parameters,
    body,
    headers,
    queryParameters,
    form,
    deferred
  );

  return deferred.promise;
};
API.prototype.get_hint = function(parameters) {
  if (parameters === undefined) {
    parameters = {};
  }
  let deferred = Q.defer();
  let domain = this.domain,
    path = "/hints/{hint_id}";
  let body = {},
    queryParameters = {},
    headers = {},
    form = {};

  headers["Accept"] = ["application/json"];
  headers["Content-Type"] = ["application/json"];

  path = path.replace("{hint_id}", parameters["hintId"]);

  if (parameters["hintId"] === undefined) {
    deferred.reject(new Error("Missing required  parameter: hintId"));
    return deferred.promise;
  }
  delete parameters["hintId"];

  queryParameters = mergeQueryParams(parameters, queryParameters);

  this.request(
    "GET",
    domain + path,
    parameters,
    body,
    headers,
    queryParameters,
    form,
    deferred
  );

  return deferred.promise;
};
