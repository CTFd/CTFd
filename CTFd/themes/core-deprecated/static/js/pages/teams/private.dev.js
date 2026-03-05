/******/ (function(modules) { // webpackBootstrap
/******/ 	// install a JSONP callback for chunk loading
/******/ 	function webpackJsonpCallback(data) {
/******/ 		var chunkIds = data[0];
/******/ 		var moreModules = data[1];
/******/ 		var executeModules = data[2];
/******/
/******/ 		// add "moreModules" to the modules object,
/******/ 		// then flag all "chunkIds" as loaded and fire callback
/******/ 		var moduleId, chunkId, i = 0, resolves = [];
/******/ 		for(;i < chunkIds.length; i++) {
/******/ 			chunkId = chunkIds[i];
/******/ 			if(installedChunks[chunkId]) {
/******/ 				resolves.push(installedChunks[chunkId][0]);
/******/ 			}
/******/ 			installedChunks[chunkId] = 0;
/******/ 		}
/******/ 		for(moduleId in moreModules) {
/******/ 			if(Object.prototype.hasOwnProperty.call(moreModules, moduleId)) {
/******/ 				modules[moduleId] = moreModules[moduleId];
/******/ 			}
/******/ 		}
/******/ 		if(parentJsonpFunction) parentJsonpFunction(data);
/******/
/******/ 		while(resolves.length) {
/******/ 			resolves.shift()();
/******/ 		}
/******/
/******/ 		// add entry modules from loaded chunk to deferred list
/******/ 		deferredModules.push.apply(deferredModules, executeModules || []);
/******/
/******/ 		// run deferred modules when all chunks ready
/******/ 		return checkDeferredModules();
/******/ 	};
/******/ 	function checkDeferredModules() {
/******/ 		var result;
/******/ 		for(var i = 0; i < deferredModules.length; i++) {
/******/ 			var deferredModule = deferredModules[i];
/******/ 			var fulfilled = true;
/******/ 			for(var j = 1; j < deferredModule.length; j++) {
/******/ 				var depId = deferredModule[j];
/******/ 				if(installedChunks[depId] !== 0) fulfilled = false;
/******/ 			}
/******/ 			if(fulfilled) {
/******/ 				deferredModules.splice(i--, 1);
/******/ 				result = __webpack_require__(__webpack_require__.s = deferredModule[0]);
/******/ 			}
/******/ 		}
/******/ 		return result;
/******/ 	}
/******/
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// object to store loaded and loading chunks
/******/ 	// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 	// Promise = chunk loading, 0 = chunk loaded
/******/ 	var installedChunks = {
/******/ 		"pages/teams/private": 0
/******/ 	};
/******/
/******/ 	var deferredModules = [];
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "/themes/core/static/js";
/******/
/******/ 	var jsonpArray = window["webpackJsonp"] = window["webpackJsonp"] || [];
/******/ 	var oldJsonpFunction = jsonpArray.push.bind(jsonpArray);
/******/ 	jsonpArray.push = webpackJsonpCallback;
/******/ 	jsonpArray = jsonpArray.slice();
/******/ 	for(var i = 0; i < jsonpArray.length; i++) webpackJsonpCallback(jsonpArray[i]);
/******/ 	var parentJsonpFunction = oldJsonpFunction;
/******/
/******/
/******/ 	// add entry module to deferred list
/******/ 	deferredModules.push(["./CTFd/themes/core/assets/js/pages/teams/private.js","helpers","vendor","default~pages/challenges~pages/main~pages/notifications~pages/scoreboard~pages/settings~pages/setup~~6822bf1f"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./CTFd/themes/core/assets/js/pages/teams/private.js":
/*!***********************************************************!*\
  !*** ./CTFd/themes/core/assets/js/pages/teams/private.js ***!
  \***********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\n__webpack_require__(/*! ../main */ \"./CTFd/themes/core/assets/js/pages/main.js\");\n\nvar _utils = __webpack_require__(/*! ../../utils */ \"./CTFd/themes/core/assets/js/utils.js\");\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! ../../CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\n__webpack_require__(/*! bootstrap/js/dist/modal */ \"./node_modules/bootstrap/js/dist/modal.js\");\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _ezq = __webpack_require__(/*! ../../ezq */ \"./CTFd/themes/core/assets/js/ezq.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { \"default\": obj }; }\n\n(0, _jquery[\"default\"])(function () {\n  if (window.team_captain) {\n    (0, _jquery[\"default\"])(\".edit-team\").click(function () {\n      (0, _jquery[\"default\"])(\"#team-edit-modal\").modal();\n    });\n    (0, _jquery[\"default\"])(\".edit-captain\").click(function () {\n      (0, _jquery[\"default\"])(\"#team-captain-modal\").modal();\n    });\n    (0, _jquery[\"default\"])(\".invite-members\").click(function () {\n      _CTFd[\"default\"].fetch(\"/api/v1/teams/me/members\", {\n        method: \"POST\",\n        credentials: \"same-origin\",\n        headers: {\n          Accept: \"application/json\",\n          \"Content-Type\": \"application/json\"\n        }\n      }).then(function (response) {\n        return response.json();\n      }).then(function (response) {\n        if (response.success) {\n          var code = response.data.code;\n          var url = \"\".concat(window.location.origin).concat(_CTFd[\"default\"].config.urlRoot, \"/teams/invite?code=\").concat(code);\n          (0, _jquery[\"default\"])(\"#team-invite-modal input[name=link]\").val(url);\n          (0, _jquery[\"default\"])(\"#team-invite-modal\").modal();\n        }\n      });\n    });\n    (0, _jquery[\"default\"])(\"#team-invite-link-copy\").click(function (event) {\n      (0, _utils.copyToClipboard)(event, \"#team-invite-link\");\n    });\n    (0, _jquery[\"default\"])(\".disband-team\").click(function () {\n      (0, _ezq.ezQuery)({\n        title: \"Disband Team\",\n        body: \"Are you sure you want to disband your team?\",\n        success: function success() {\n          _CTFd[\"default\"].fetch(\"/api/v1/teams/me\", {\n            method: \"DELETE\"\n          }).then(function (response) {\n            return response.json();\n          }).then(function (response) {\n            if (response.success) {\n              window.location.reload();\n            } else {\n              (0, _ezq.ezAlert)({\n                title: \"Error\",\n                body: response.errors[\"\"].join(\" \"),\n                button: \"Got it!\"\n              });\n            }\n          });\n        }\n      });\n    });\n  }\n\n  var form = (0, _jquery[\"default\"])(\"#team-info-form\");\n  form.submit(function (e) {\n    e.preventDefault();\n    (0, _jquery[\"default\"])(\"#results\").empty();\n    var params = (0, _jquery[\"default\"])(this).serializeJSON();\n    params.fields = [];\n\n    for (var property in params) {\n      if (property.match(/fields\\[\\d+\\]/)) {\n        var field = {};\n        var id = parseInt(property.slice(7, -1));\n        field[\"field_id\"] = id;\n        field[\"value\"] = params[property];\n        params.fields.push(field);\n        delete params[property];\n      }\n    }\n\n    var method = \"PATCH\";\n    var url = \"/api/v1/teams/me\";\n\n    _CTFd[\"default\"].fetch(url, {\n      method: method,\n      credentials: \"same-origin\",\n      headers: {\n        Accept: \"application/json\",\n        \"Content-Type\": \"application/json\"\n      },\n      body: JSON.stringify(params)\n    }).then(function (response) {\n      if (response.status === 400) {\n        response.json().then(function (object) {\n          if (!object.success) {\n            var error_template = '<div class=\"alert alert-danger alert-dismissable\" role=\"alert\">\\n' + '  <span class=\"sr-only\">Error:</span>\\n' + \"  {0}\\n\" + '  <button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-label=\"Close\"><span aria-hidden=\"true\">×</span></button>\\n' + \"</div>\";\n            Object.keys(object.errors).map(function (error) {\n              var i = form.find(\"input[name={0}]\".format(error));\n              var input = (0, _jquery[\"default\"])(i);\n              input.addClass(\"input-filled-invalid\");\n              input.removeClass(\"input-filled-valid\");\n              var error_msg = object.errors[error];\n              var alert = error_template.format(error_msg);\n              (0, _jquery[\"default\"])(\"#results\").append(alert);\n            });\n          }\n        });\n      } else if (response.status === 200) {\n        response.json().then(function (object) {\n          if (object.success) {\n            window.location.reload();\n          }\n        });\n      }\n    });\n  });\n  (0, _jquery[\"default\"])(\"#team-captain-form\").submit(function (e) {\n    e.preventDefault();\n    var params = (0, _jquery[\"default\"])(\"#team-captain-form\").serializeJSON(true);\n\n    _CTFd[\"default\"].fetch(\"/api/v1/teams/me\", {\n      method: \"PATCH\",\n      credentials: \"same-origin\",\n      headers: {\n        Accept: \"application/json\",\n        \"Content-Type\": \"application/json\"\n      },\n      body: JSON.stringify(params)\n    }).then(function (response) {\n      return response.json();\n    }).then(function (response) {\n      if (response.success) {\n        window.location.reload();\n      } else {\n        (0, _jquery[\"default\"])(\"#team-captain-form > #results\").empty();\n        Object.keys(response.errors).forEach(function (key, _index) {\n          (0, _jquery[\"default\"])(\"#team-captain-form > #results\").append((0, _ezq.ezBadge)({\n            type: \"error\",\n            body: response.errors[key]\n          }));\n          var i = (0, _jquery[\"default\"])(\"#team-captain-form\").find(\"select[name={0}]\".format(key));\n          var input = (0, _jquery[\"default\"])(i);\n          input.addClass(\"input-filled-invalid\");\n          input.removeClass(\"input-filled-valid\");\n        });\n      }\n    });\n  });\n});\n\n//# sourceURL=webpack:///./CTFd/themes/core/assets/js/pages/teams/private.js?");

/***/ })

/******/ });