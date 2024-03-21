import fetch from "./fetch";
/*jshint esversion: 6 */
// eslint-disable-next-line no-redeclare, no-unused-vars
/*global fetch, btoa */
import Q from "q";
/**
 *
 * @class API
 * @param {(string|object)} [domainOrOptions] - The project domain or options object. If object, see the object's optional properties.
 * @param {string} [domainOrOptions.domain] - The project domain
 * @param {object} [domainOrOptions.token] - auth token - object with value property and optional headerOrQueryName and isQuery properties
 */
let API = (function () {
  "use strict";

  function API(options) {
    let domain = typeof options === "object" ? options.domain : options;
    this.domain = domain ? domain : "";
    if (this.domain.length === 0) {
      throw new Error("Domain parameter must be specified as a string.");
    }
  }

  function serializeQueryParams(parameters) {
    let str = [];
    for (let p in parameters) {
      // eslint-disable-next-line no-prototype-builtins
      if (parameters.hasOwnProperty(p)) {
        str.push(
          encodeURIComponent(p) + "=" + encodeURIComponent(parameters[p]),
        );
      }
    }
    return str.join("&");
  }

  function mergeQueryParams(parameters, queryParameters) {
    if (parameters.$queryParameters) {
      Object.keys(parameters.$queryParameters).forEach(
        function (parameterName) {
          let parameter = parameters.$queryParameters[parameterName];
          queryParameters[parameterName] = parameter;
        },
      );
    }
    return queryParameters;
  }

  /**
   * HTTP Request
   * @method
   * @name API#request
   * @param {string} method - http method
   * @param {string} url - url to do request
   * @param {object} parameters
   * @param {object} body - body parameters / object
   * @param {object} headers - header parameters
   * @param {object} queryParameters - querystring parameters
   * @param {object} form - form data object
   * @param {object} deferred - promise object
   */
  API.prototype.request = function (
    method,
    url,
    parameters,
    body,
    headers,
    queryParameters,
    form,
    deferred,
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
      body: JSON.stringify(body),
    })
      .then((response) => {
        return response.json();
      })
      .then((body) => {
        deferred.resolve(body);
      })
      .catch((error) => {
        deferred.reject(error);
      });
  };

  /**
   *
   * @method
   * @name API#post_award_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_award_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/awards";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#delete_award
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.awardId - An Award ID
   */
  API.prototype.delete_award = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/awards/{award_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{award_id}", parameters["awardId"]);

    if (parameters["awardId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: awardId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "DELETE",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_award
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.awardId - An Award ID
   */
  API.prototype.get_award = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/awards/{award_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{award_id}", parameters["awardId"]);

    if (parameters["awardId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: awardId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_challenge_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_challenge_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_challenge_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_challenge_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_challenge_attempt
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_challenge_attempt = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges/attempt";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_challenge_types
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_challenge_types = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges/types";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#patch_challenge
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.challengeId - A Challenge ID
   */
  API.prototype.patch_challenge = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges/{challenge_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{challenge_id}", parameters["challengeId"]);

    if (parameters["challengeId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: challengeId"));
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#delete_challenge
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.challengeId - A Challenge ID
   */
  API.prototype.delete_challenge = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges/{challenge_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{challenge_id}", parameters["challengeId"]);

    if (parameters["challengeId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: challengeId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "DELETE",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_challenge
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.challengeId - A Challenge ID
   */
  API.prototype.get_challenge = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges/{challenge_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{challenge_id}", parameters["challengeId"]);

    if (parameters["challengeId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: challengeId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_challenge_files
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.id - A Challenge ID
   * @param {string} parameters.challengeId -
   */
  API.prototype.get_challenge_files = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges/{challenge_id}/files";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    if (parameters["id"] !== undefined) {
      queryParameters["id"] = parameters["id"];
    }

    path = path.replace("{challenge_id}", parameters["challengeId"]);

    if (parameters["challengeId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: challengeId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_challenge_flags
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.id - A Challenge ID
   * @param {string} parameters.challengeId -
   */
  API.prototype.get_challenge_flags = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges/{challenge_id}/flags";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    if (parameters["id"] !== undefined) {
      queryParameters["id"] = parameters["id"];
    }

    path = path.replace("{challenge_id}", parameters["challengeId"]);

    if (parameters["challengeId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: challengeId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_challenge_hints
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.id - A Challenge ID
   * @param {string} parameters.challengeId -
   */
  API.prototype.get_challenge_hints = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges/{challenge_id}/hints";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    if (parameters["id"] !== undefined) {
      queryParameters["id"] = parameters["id"];
    }

    path = path.replace("{challenge_id}", parameters["challengeId"]);

    if (parameters["challengeId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: challengeId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_challenge_solves
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.id - A Challenge ID
   * @param {string} parameters.challengeId -
   */
  API.prototype.get_challenge_solves = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges/{challenge_id}/solves";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    if (parameters["id"] !== undefined) {
      queryParameters["id"] = parameters["id"];
    }

    path = path.replace("{challenge_id}", parameters["challengeId"]);

    if (parameters["challengeId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: challengeId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_challenge_tags
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.id - A Challenge ID
   * @param {string} parameters.challengeId -
   */
  API.prototype.get_challenge_tags = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges/{challenge_id}/tags";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    if (parameters["id"] !== undefined) {
      queryParameters["id"] = parameters["id"];
    }

    path = path.replace("{challenge_id}", parameters["challengeId"]);

    if (parameters["challengeId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: challengeId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_config_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_config_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/configs";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#patch_config_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.patch_config_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/configs";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_config_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_config_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/configs";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#patch_config
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.configKey -
   */
  API.prototype.patch_config = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/configs/{config_key}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{config_key}", parameters["configKey"]);

    if (parameters["configKey"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: configKey"));
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#delete_config
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.configKey -
   */
  API.prototype.delete_config = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/configs/{config_key}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{config_key}", parameters["configKey"]);

    if (parameters["configKey"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: configKey"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "DELETE",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_config
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.configKey -
   */
  API.prototype.get_config = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/configs/{config_key}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{config_key}", parameters["configKey"]);

    if (parameters["configKey"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: configKey"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_files_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_files_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/files";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_files_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_files_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/files";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#delete_files_detail
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.fileId -
   */
  API.prototype.delete_files_detail = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/files/{file_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{file_id}", parameters["fileId"]);

    if (parameters["fileId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: fileId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "DELETE",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_files_detail
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.fileId -
   */
  API.prototype.get_files_detail = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/files/{file_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{file_id}", parameters["fileId"]);

    if (parameters["fileId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: fileId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_flag_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_flag_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/flags";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_flag_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_flag_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/flags";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_flag_types
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_flag_types = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/flags/types";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_flag_types_1
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.typeName -
   */
  API.prototype.get_flag_types_1 = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/flags/types/{type_name}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{type_name}", parameters["typeName"]);

    if (parameters["typeName"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: typeName"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#patch_flag
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.flagId -
   */
  API.prototype.patch_flag = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/flags/{flag_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{flag_id}", parameters["flagId"]);

    if (parameters["flagId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: flagId"));
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#delete_flag
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.flagId -
   */
  API.prototype.delete_flag = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/flags/{flag_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{flag_id}", parameters["flagId"]);

    if (parameters["flagId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: flagId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "DELETE",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_flag
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.flagId -
   */
  API.prototype.get_flag = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/flags/{flag_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{flag_id}", parameters["flagId"]);

    if (parameters["flagId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: flagId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_hint_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_hint_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/hints";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_hint_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_hint_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/hints";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#patch_hint
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.hintId -
   */
  API.prototype.patch_hint = function (parameters) {
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

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "PATCH",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#delete_hint
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.hintId -
   */
  API.prototype.delete_hint = function (parameters) {
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

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "DELETE",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_hint
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.hintId -
   */
  API.prototype.get_hint = function (parameters) {
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

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_notification_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_notification_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/notifications";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_notification_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_notification_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/notifications";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#delete_notification
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.notificationId - A Notification ID
   */
  API.prototype.delete_notification = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/notifications/{notification_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{notification_id}", parameters["notificationId"]);

    if (parameters["notificationId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: notificationId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "DELETE",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_notification
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.notificationId - A Notification ID
   */
  API.prototype.get_notification = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/notifications/{notification_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{notification_id}", parameters["notificationId"]);

    if (parameters["notificationId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: notificationId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_page_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_page_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/pages";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_page_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_page_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/pages";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#patch_page_detail
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.pageId -
   */
  API.prototype.patch_page_detail = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/pages/{page_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{page_id}", parameters["pageId"]);

    if (parameters["pageId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: pageId"));
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#delete_page_detail
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.pageId -
   */
  API.prototype.delete_page_detail = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/pages/{page_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{page_id}", parameters["pageId"]);

    if (parameters["pageId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: pageId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "DELETE",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_page_detail
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.pageId -
   */
  API.prototype.get_page_detail = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/pages/{page_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{page_id}", parameters["pageId"]);

    if (parameters["pageId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: pageId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_scoreboard_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_scoreboard_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/scoreboard";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_scoreboard_detail
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.count - How many top teams to return
   */
  API.prototype.get_scoreboard_detail = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/scoreboard/top/{count}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{count}", parameters["count"]);

    if (parameters["count"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: count"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_challenge_solve_statistics
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_challenge_solve_statistics = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/statistics/challenges/solves";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_challenge_solve_percentages
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_challenge_solve_percentages = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/statistics/challenges/solves/percentages";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_challenge_property_counts
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.column -
   */
  API.prototype.get_challenge_property_counts = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/statistics/challenges/{column}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{column}", parameters["column"]);

    if (parameters["column"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: column"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_submission_property_counts
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.column -
   */
  API.prototype.get_submission_property_counts = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/statistics/submissions/{column}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{column}", parameters["column"]);

    if (parameters["column"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: column"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_team_statistics
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_team_statistics = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/statistics/teams";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_user_statistics
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_user_statistics = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/statistics/users";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_user_property_counts
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.column -
   */
  API.prototype.get_user_property_counts = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/statistics/users/{column}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{column}", parameters["column"]);

    if (parameters["column"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: column"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_submissions_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_submissions_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/submissions";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_submissions_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_submissions_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/submissions";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#delete_submission
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.submissionId - A Submission ID
   */
  API.prototype.delete_submission = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/submissions/{submission_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{submission_id}", parameters["submissionId"]);

    if (parameters["submissionId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: submissionId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "DELETE",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_submission
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.submissionId - A Submission ID
   */
  API.prototype.get_submission = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/submissions/{submission_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{submission_id}", parameters["submissionId"]);

    if (parameters["submissionId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: submissionId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_tag_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_tag_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/tags";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_tag_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_tag_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/tags";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#patch_tag
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.tagId - A Tag ID
   */
  API.prototype.patch_tag = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/tags/{tag_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{tag_id}", parameters["tagId"]);

    if (parameters["tagId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: tagId"));
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#delete_tag
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.tagId - A Tag ID
   */
  API.prototype.delete_tag = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/tags/{tag_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{tag_id}", parameters["tagId"]);

    if (parameters["tagId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: tagId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "DELETE",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_tag
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.tagId - A Tag ID
   */
  API.prototype.get_tag = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/tags/{tag_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{tag_id}", parameters["tagId"]);

    if (parameters["tagId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: tagId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_team_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_team_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/teams";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_team_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_team_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/teams";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#patch_team_private
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.teamId - Current Team
   */
  API.prototype.patch_team_private = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/teams/me";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    if (parameters["teamId"] !== undefined) {
      queryParameters["team_id"] = parameters["teamId"];
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_team_private
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.teamId - Current Team
   */
  API.prototype.get_team_private = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/teams/me";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    if (parameters["teamId"] !== undefined) {
      queryParameters["team_id"] = parameters["teamId"];
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#patch_team_public
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.teamId - Team ID
   */
  API.prototype.patch_team_public = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/teams/{team_id}";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#delete_team_public
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.teamId - Team ID
   */
  API.prototype.delete_team_public = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/teams/{team_id}";
    let body = {},
      queryParameters = {},
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
      "DELETE",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_team_public
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.teamId - Team ID
   */
  API.prototype.get_team_public = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/teams/{team_id}";
    let body = {},
      queryParameters = {},
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
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_team_awards
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.teamId - Team ID or 'me'
   */
  API.prototype.get_team_awards = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/teams/{team_id}/awards";
    let body = {},
      queryParameters = {},
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
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_team_fails
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.teamId - Team ID or 'me'
   */
  API.prototype.get_team_fails = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/teams/{team_id}/fails";
    let body = {},
      queryParameters = {},
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
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_team_solves
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.teamId - Team ID or 'me'
   */
  API.prototype.get_team_solves = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/teams/{team_id}/solves";
    let body = {},
      queryParameters = {},
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
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_unlock_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_unlock_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/unlocks";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_unlock_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_unlock_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/unlocks";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#post_user_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.post_user_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/users";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_user_list
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_user_list = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/users";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#patch_user_private
   * @param {object} parameters - method options and parameters
   */
  API.prototype.patch_user_private = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/users/me";
    let body = {},
      queryParameters = {},
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_user_private
   * @param {object} parameters - method options and parameters
   */
  API.prototype.get_user_private = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/users/me";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#patch_user_public
   * @param {object} parameters - method options and parameters
   * @param {integer} parameters.userId - User ID
   */
  API.prototype.patch_user_public = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/users/{user_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{user_id}", parameters["userId"]);

    if (parameters["userId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: userId"));
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
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#delete_user_public
   * @param {object} parameters - method options and parameters
   * @param {integer} parameters.userId - User ID
   */
  API.prototype.delete_user_public = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/users/{user_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{user_id}", parameters["userId"]);

    if (parameters["userId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: userId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "DELETE",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_user_public
   * @param {object} parameters - method options and parameters
   * @param {integer} parameters.userId - User ID
   */
  API.prototype.get_user_public = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/users/{user_id}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{user_id}", parameters["userId"]);

    if (parameters["userId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: userId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_user_awards
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.userId - User ID or 'me'
   */
  API.prototype.get_user_awards = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/users/{user_id}/awards";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{user_id}", parameters["userId"]);

    if (parameters["userId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: userId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_user_fails
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.userId - User ID or 'me'
   */
  API.prototype.get_user_fails = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/users/{user_id}/fails";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{user_id}", parameters["userId"]);

    if (parameters["userId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: userId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_user_solves
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.userId - User ID or 'me'
   */
  API.prototype.get_user_solves = function (parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/users/{user_id}/solves";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    path = path.replace("{user_id}", parameters["userId"]);

    if (parameters["userId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: userId"));
      return deferred.promise;
    }

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred,
    );

    return deferred.promise;
  };

  return API;
})();

// eslint-disable-next-line no-undef
// exports.API = API;
export default API;
