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
/******/ 		"pages/challenge": 0
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
/******/ 	__webpack_require__.p = "/themes/admin/static/js";
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
/******/ 	deferredModules.push(["./CTFd/themes/admin/assets/js/pages/challenge.js","helpers","vendor","default~pages/challenge~pages/configs~pages/editor~pages/main~pages/notifications~pages/pages~pages/~0fc9fcae"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./CTFd/themes/admin/assets/js/challenges/files.js":
/*!*********************************************************!*\
  !*** ./CTFd/themes/admin/assets/js/challenges/files.js ***!
  \*********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\nObject.defineProperty(exports, \"__esModule\", {\n  value: true\n});\nexports.addFile = addFile;\nexports.deleteFile = deleteFile;\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! core/CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _helpers = _interopRequireDefault(__webpack_require__(/*! core/helpers */ \"./CTFd/themes/core/assets/js/helpers.js\"));\n\nvar _ezq = __webpack_require__(/*! core/ezq */ \"./CTFd/themes/core/assets/js/ezq.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nfunction addFile(event) {\n  event.preventDefault();\n  var form = event.target;\n  var data = {\n    challenge: CHALLENGE_ID,\n    type: \"challenge\"\n  };\n\n  _helpers.default.files.upload(form, data, function (response) {\n    setTimeout(function () {\n      window.location.reload();\n    }, 700);\n  });\n}\n\nfunction deleteFile(event) {\n  var file_id = (0, _jquery.default)(this).attr(\"file-id\");\n  var row = (0, _jquery.default)(this).parent().parent();\n  (0, _ezq.ezQuery)({\n    title: \"Delete Files\",\n    body: \"Are you sure you want to delete this file?\",\n    success: function success() {\n      _CTFd.default.fetch(\"/api/v1/files/\" + file_id, {\n        method: \"DELETE\"\n      }).then(function (response) {\n        return response.json();\n      }).then(function (response) {\n        if (response.success) {\n          row.remove();\n        }\n      });\n    }\n  });\n}\n\n//# sourceURL=webpack:///./CTFd/themes/admin/assets/js/challenges/files.js?");

/***/ }),

/***/ "./CTFd/themes/admin/assets/js/challenges/flags.js":
/*!*********************************************************!*\
  !*** ./CTFd/themes/admin/assets/js/challenges/flags.js ***!
  \*********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\nObject.defineProperty(exports, \"__esModule\", {\n  value: true\n});\nexports.deleteFlag = deleteFlag;\nexports.addFlagModal = addFlagModal;\nexports.editFlagModal = editFlagModal;\nexports.flagTypeSelect = flagTypeSelect;\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! core/CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _nunjucks = _interopRequireDefault(__webpack_require__(/*! nunjucks */ \"./node_modules/nunjucks/browser/nunjucks.js\"));\n\nvar _ezq = __webpack_require__(/*! core/ezq */ \"./CTFd/themes/core/assets/js/ezq.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nfunction deleteFlag(event) {\n  event.preventDefault();\n  var flag_id = (0, _jquery.default)(this).attr(\"flag-id\");\n  var row = (0, _jquery.default)(this).parent().parent();\n  (0, _ezq.ezQuery)({\n    title: \"Delete Flag\",\n    body: \"Are you sure you want to delete this flag?\",\n    success: function success() {\n      _CTFd.default.fetch(\"/api/v1/flags/\" + flag_id, {\n        method: \"DELETE\"\n      }).then(function (response) {\n        return response.json();\n      }).then(function (response) {\n        if (response.success) {\n          row.remove();\n        }\n      });\n    }\n  });\n}\n\nfunction addFlagModal(event) {\n  _jquery.default.get(_CTFd.default.config.urlRoot + \"/api/v1/flags/types\", function (response) {\n    var data = response.data;\n    var flag_type_select = (0, _jquery.default)(\"#flags-create-select\");\n    flag_type_select.empty();\n    var option = (0, _jquery.default)(\"<option> -- </option>\");\n    flag_type_select.append(option);\n\n    for (var key in data) {\n      if (data.hasOwnProperty(key)) {\n        option = (0, _jquery.default)(\"<option value='{0}'>{1}</option>\".format(key, data[key].name));\n        flag_type_select.append(option);\n      }\n    }\n\n    (0, _jquery.default)(\"#flag-edit-modal\").modal();\n  });\n\n  (0, _jquery.default)(\"#flag-edit-modal form\").submit(function (event) {\n    event.preventDefault();\n    var params = (0, _jquery.default)(this).serializeJSON(true);\n    params[\"challenge\"] = CHALLENGE_ID;\n\n    _CTFd.default.fetch(\"/api/v1/flags\", {\n      method: \"POST\",\n      credentials: \"same-origin\",\n      headers: {\n        Accept: \"application/json\",\n        \"Content-Type\": \"application/json\"\n      },\n      body: JSON.stringify(params)\n    }).then(function (response) {\n      return response.json();\n    }).then(function (response) {\n      window.location.reload();\n    });\n  });\n  (0, _jquery.default)(\"#flag-edit-modal\").modal();\n}\n\nfunction editFlagModal(event) {\n  event.preventDefault();\n  var flag_id = (0, _jquery.default)(this).attr(\"flag-id\");\n  var row = (0, _jquery.default)(this).parent().parent();\n\n  _jquery.default.get(_CTFd.default.config.urlRoot + \"/api/v1/flags/\" + flag_id, function (response) {\n    var data = response.data;\n\n    _jquery.default.get(_CTFd.default.config.urlRoot + data.templates.update, function (template_data) {\n      (0, _jquery.default)(\"#edit-flags form\").empty();\n      (0, _jquery.default)(\"#edit-flags form\").off();\n\n      var template = _nunjucks.default.compile(template_data);\n\n      (0, _jquery.default)(\"#edit-flags form\").append(template.render(data));\n      (0, _jquery.default)(\"#edit-flags form\").submit(function (event) {\n        event.preventDefault();\n        var params = (0, _jquery.default)(\"#edit-flags form\").serializeJSON();\n\n        _CTFd.default.fetch(\"/api/v1/flags/\" + flag_id, {\n          method: \"PATCH\",\n          credentials: \"same-origin\",\n          headers: {\n            Accept: \"application/json\",\n            \"Content-Type\": \"application/json\"\n          },\n          body: JSON.stringify(params)\n        }).then(function (response) {\n          return response.json();\n        }).then(function (response) {\n          if (response.success) {\n            (0, _jquery.default)(row).find(\".flag-content\").text(response.data.content);\n            (0, _jquery.default)(\"#edit-flags\").modal(\"toggle\");\n          }\n        });\n      });\n      (0, _jquery.default)(\"#edit-flags\").modal();\n    });\n  });\n}\n\nfunction flagTypeSelect(event) {\n  event.preventDefault();\n  var flag_type_name = (0, _jquery.default)(this).find(\"option:selected\").text();\n\n  _jquery.default.get(_CTFd.default.config.urlRoot + \"/api/v1/flags/types/\" + flag_type_name, function (response) {\n    var data = response.data;\n\n    _jquery.default.get(_CTFd.default.config.urlRoot + data.templates.create, function (template_data) {\n      var template = _nunjucks.default.compile(template_data);\n\n      (0, _jquery.default)(\"#create-keys-entry-div\").html(template.render());\n      (0, _jquery.default)(\"#create-keys-button-div\").show();\n    });\n  });\n}\n\n//# sourceURL=webpack:///./CTFd/themes/admin/assets/js/challenges/flags.js?");

/***/ }),

/***/ "./CTFd/themes/admin/assets/js/challenges/hints.js":
/*!*********************************************************!*\
  !*** ./CTFd/themes/admin/assets/js/challenges/hints.js ***!
  \*********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\nObject.defineProperty(exports, \"__esModule\", {\n  value: true\n});\nexports.showHintModal = showHintModal;\nexports.showEditHintModal = showEditHintModal;\nexports.deleteHint = deleteHint;\nexports.editHint = editHint;\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! core/CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _ezq = __webpack_require__(/*! core/ezq */ \"./CTFd/themes/core/assets/js/ezq.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nfunction hint(id) {\n  return _CTFd.default.fetch(\"/api/v1/hints/\" + id + \"?preview=true\", {\n    method: \"GET\",\n    credentials: \"same-origin\",\n    headers: {\n      Accept: \"application/json\",\n      \"Content-Type\": \"application/json\"\n    }\n  });\n}\n\nfunction loadhint(hintid) {\n  var md = _CTFd.default.lib.markdown();\n\n  hint(hintid).then(function (response) {\n    if (response.data.content) {\n      (0, _ezq.ezAlert)({\n        title: \"Hint\",\n        body: md.render(response.data.content),\n        button: \"Got it!\"\n      });\n    } else {\n      (0, _ezq.ezAlert)({\n        title: \"Error\",\n        body: \"Error loading hint!\",\n        button: \"OK\"\n      });\n    }\n  });\n}\n\nfunction showHintModal(event) {\n  event.preventDefault();\n  (0, _jquery.default)(\"#hint-edit-modal form\").find(\"input, textarea\").val(\"\"); // Markdown Preview\n\n  (0, _jquery.default)(\"#new-hint-edit\").on(\"shown.bs.tab\", function (event) {\n    if (event.target.hash == \"#hint-preview\") {\n      var renderer = _CTFd.default.lib.markdown();\n\n      var editor_value = (0, _jquery.default)(\"#hint-write textarea\").val();\n      (0, _jquery.default)(event.target.hash).html(renderer.render(editor_value));\n    }\n  });\n  (0, _jquery.default)(\"#hint-edit-modal\").modal();\n}\n\nfunction showEditHintModal(event) {\n  event.preventDefault();\n  var hint_id = (0, _jquery.default)(this).attr(\"hint-id\");\n\n  _CTFd.default.fetch(\"/api/v1/hints/\" + hint_id + \"?preview=true\", {\n    method: \"GET\",\n    credentials: \"same-origin\",\n    headers: {\n      Accept: \"application/json\",\n      \"Content-Type\": \"application/json\"\n    }\n  }).then(function (response) {\n    return response.json();\n  }).then(function (response) {\n    if (response.success) {\n      (0, _jquery.default)(\"#hint-edit-form input[name=content],textarea[name=content]\").val(response.data.content);\n      (0, _jquery.default)(\"#hint-edit-form input[name=cost]\").val(response.data.cost);\n      (0, _jquery.default)(\"#hint-edit-form input[name=id]\").val(response.data.id); // Markdown Preview\n\n      (0, _jquery.default)(\"#new-hint-edit\").on(\"shown.bs.tab\", function (event) {\n        if (event.target.hash == \"#hint-preview\") {\n          var renderer = _CTFd.default.lib.markdown();\n\n          var editor_value = (0, _jquery.default)(\"#hint-write textarea\").val();\n          (0, _jquery.default)(event.target.hash).html(renderer.render(editor_value));\n        }\n      });\n      (0, _jquery.default)(\"#hint-edit-modal\").modal();\n    }\n  });\n}\n\nfunction deleteHint(event) {\n  event.preventDefault();\n  var hint_id = (0, _jquery.default)(this).attr(\"hint-id\");\n  var row = (0, _jquery.default)(this).parent().parent();\n  (0, _ezq.ezQuery)({\n    title: \"Delete Hint\",\n    body: \"Are you sure you want to delete this hint?\",\n    success: function success() {\n      _CTFd.default.fetch(\"/api/v1/hints/\" + hint_id, {\n        method: \"DELETE\"\n      }).then(function (response) {\n        return response.json();\n      }).then(function (data) {\n        if (data.success) {\n          row.remove();\n        }\n      });\n    }\n  });\n}\n\nfunction editHint(event) {\n  event.preventDefault();\n  var params = (0, _jquery.default)(this).serializeJSON(true);\n  params[\"challenge\"] = CHALLENGE_ID;\n  var method = \"POST\";\n  var url = \"/api/v1/hints\";\n\n  if (params.id) {\n    method = \"PATCH\";\n    url = \"/api/v1/hints/\" + params.id;\n  }\n\n  _CTFd.default.fetch(url, {\n    method: method,\n    credentials: \"same-origin\",\n    headers: {\n      Accept: \"application/json\",\n      \"Content-Type\": \"application/json\"\n    },\n    body: JSON.stringify(params)\n  }).then(function (response) {\n    return response.json();\n  }).then(function (data) {\n    if (data.success) {\n      // TODO: Refresh hints on submit.\n      window.location.reload();\n    }\n  });\n}\n\n//# sourceURL=webpack:///./CTFd/themes/admin/assets/js/challenges/hints.js?");

/***/ }),

/***/ "./CTFd/themes/admin/assets/js/challenges/requirements.js":
/*!****************************************************************!*\
  !*** ./CTFd/themes/admin/assets/js/challenges/requirements.js ***!
  \****************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\nObject.defineProperty(exports, \"__esModule\", {\n  value: true\n});\nexports.addRequirement = addRequirement;\nexports.deleteRequirement = deleteRequirement;\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! core/CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nfunction addRequirement(event) {\n  event.preventDefault();\n  var requirements = (0, _jquery.default)(\"#prerequisite-add-form\").serializeJSON(); // Shortcut if there's no prerequisite\n\n  if (!requirements[\"prerequisite\"]) {\n    return;\n  }\n\n  CHALLENGE_REQUIREMENTS.prerequisites.push(parseInt(requirements[\"prerequisite\"]));\n  var params = {\n    requirements: CHALLENGE_REQUIREMENTS\n  };\n\n  _CTFd.default.fetch(\"/api/v1/challenges/\" + CHALLENGE_ID, {\n    method: \"PATCH\",\n    credentials: \"same-origin\",\n    headers: {\n      Accept: \"application/json\",\n      \"Content-Type\": \"application/json\"\n    },\n    body: JSON.stringify(params)\n  }).then(function (response) {\n    return response.json();\n  }).then(function (data) {\n    if (data.success) {\n      // TODO: Make this refresh requirements\n      window.location.reload();\n    }\n  });\n}\n\nfunction deleteRequirement(event) {\n  var challenge_id = (0, _jquery.default)(this).attr(\"challenge-id\");\n  var row = (0, _jquery.default)(this).parent().parent();\n  CHALLENGE_REQUIREMENTS.prerequisites.pop(challenge_id);\n  var params = {\n    requirements: CHALLENGE_REQUIREMENTS\n  };\n\n  _CTFd.default.fetch(\"/api/v1/challenges/\" + CHALLENGE_ID, {\n    method: \"PATCH\",\n    credentials: \"same-origin\",\n    headers: {\n      Accept: \"application/json\",\n      \"Content-Type\": \"application/json\"\n    },\n    body: JSON.stringify(params)\n  }).then(function (response) {\n    return response.json();\n  }).then(function (data) {\n    if (data.success) {\n      row.remove();\n    }\n  });\n}\n\n//# sourceURL=webpack:///./CTFd/themes/admin/assets/js/challenges/requirements.js?");

/***/ }),

/***/ "./CTFd/themes/admin/assets/js/challenges/tags.js":
/*!********************************************************!*\
  !*** ./CTFd/themes/admin/assets/js/challenges/tags.js ***!
  \********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\nObject.defineProperty(exports, \"__esModule\", {\n  value: true\n});\nexports.deleteTag = deleteTag;\nexports.addTag = addTag;\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! core/CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nfunction deleteTag(event) {\n  var $elem = (0, _jquery.default)(this);\n  var tag_id = $elem.attr(\"tag-id\");\n\n  _CTFd.default.api.delete_tag({\n    tagId: tag_id\n  }).then(function (response) {\n    if (response.success) {\n      $elem.parent().remove();\n    }\n  });\n}\n\nfunction addTag(event) {\n  if (event.keyCode != 13) {\n    return;\n  }\n\n  var $elem = (0, _jquery.default)(this);\n  var tag = $elem.val();\n  var params = {\n    value: tag,\n    challenge: CHALLENGE_ID\n  };\n\n  _CTFd.default.api.post_tag_list({}, params).then(function (response) {\n    if (response.success) {\n      var tpl = \"<span class='badge badge-primary mx-1 challenge-tag'>\" + \"<span>{0}</span>\" + \"<a class='btn-fa delete-tag' tag-id='{1}'>&times;</a></span>\";\n\n      var _tag = (0, _jquery.default)(tpl.format(response.data.value, response.data.id));\n\n      (0, _jquery.default)(\"#challenge-tags\").append(_tag); // TODO: tag deletion not working on freshly created tags\n\n      _tag.click(deleteTag);\n    }\n  });\n\n  $elem.val(\"\");\n}\n\n//# sourceURL=webpack:///./CTFd/themes/admin/assets/js/challenges/tags.js?");

/***/ }),

/***/ "./CTFd/themes/admin/assets/js/pages/challenge.js":
/*!********************************************************!*\
  !*** ./CTFd/themes/admin/assets/js/pages/challenge.js ***!
  \********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\n__webpack_require__(/*! ./main */ \"./CTFd/themes/admin/assets/js/pages/main.js\");\n\nvar _utils = __webpack_require__(/*! core/utils */ \"./CTFd/themes/core/assets/js/utils.js\");\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\n__webpack_require__(/*! bootstrap/js/dist/tab */ \"./node_modules/bootstrap/js/dist/tab.js\");\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! core/CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _ezq = __webpack_require__(/*! core/ezq */ \"./CTFd/themes/core/assets/js/ezq.js\");\n\nvar _nunjucks = _interopRequireDefault(__webpack_require__(/*! nunjucks */ \"./node_modules/nunjucks/browser/nunjucks.js\"));\n\nvar _helpers = _interopRequireDefault(__webpack_require__(/*! core/helpers */ \"./CTFd/themes/core/assets/js/helpers.js\"));\n\nvar _files = __webpack_require__(/*! ../challenges/files */ \"./CTFd/themes/admin/assets/js/challenges/files.js\");\n\nvar _tags = __webpack_require__(/*! ../challenges/tags */ \"./CTFd/themes/admin/assets/js/challenges/tags.js\");\n\nvar _requirements = __webpack_require__(/*! ../challenges/requirements */ \"./CTFd/themes/admin/assets/js/challenges/requirements.js\");\n\nvar _hints = __webpack_require__(/*! ../challenges/hints */ \"./CTFd/themes/admin/assets/js/challenges/hints.js\");\n\nvar _flags = __webpack_require__(/*! ../challenges/flags */ \"./CTFd/themes/admin/assets/js/challenges/flags.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nvar md = _CTFd.default.lib.markdown();\n\nvar displayHint = function displayHint(data) {\n  (0, _ezq.ezAlert)({\n    title: \"Hint\",\n    body: md.render(data.content),\n    button: \"Got it!\"\n  });\n};\n\nvar loadHint = function loadHint(id) {\n  _CTFd.default.api.get_hint({\n    hintId: id,\n    preview: true\n  }).then(function (response) {\n    if (response.data.content) {\n      displayHint(response.data);\n      return;\n    }\n\n    displayUnlock(id);\n  });\n};\n\nfunction renderSubmissionResponse(response, cb) {\n  var result = response.data;\n  var result_message = (0, _jquery.default)(\"#result-message\");\n  var result_notification = (0, _jquery.default)(\"#result-notification\");\n  var answer_input = (0, _jquery.default)(\"#submission-input\");\n  result_notification.removeClass();\n  result_message.text(result.message);\n\n  if (result.status === \"authentication_required\") {\n    window.location = _CTFd.default.config.urlRoot + \"/login?next=\" + _CTFd.default.config.urlRoot + window.location.pathname + window.location.hash;\n    return;\n  } else if (result.status === \"incorrect\") {\n    // Incorrect key\n    result_notification.addClass(\"alert alert-danger alert-dismissable text-center\");\n    result_notification.slideDown();\n    answer_input.removeClass(\"correct\");\n    answer_input.addClass(\"wrong\");\n    setTimeout(function () {\n      answer_input.removeClass(\"wrong\");\n    }, 3000);\n  } else if (result.status === \"correct\") {\n    // Challenge Solved\n    result_notification.addClass(\"alert alert-success alert-dismissable text-center\");\n    result_notification.slideDown();\n    (0, _jquery.default)(\".challenge-solves\").text(parseInt((0, _jquery.default)(\".challenge-solves\").text().split(\" \")[0]) + 1 + \" Solves\");\n    answer_input.val(\"\");\n    answer_input.removeClass(\"wrong\");\n    answer_input.addClass(\"correct\");\n  } else if (result.status === \"already_solved\") {\n    // Challenge already solved\n    result_notification.addClass(\"alert alert-info alert-dismissable text-center\");\n    result_notification.slideDown();\n    answer_input.addClass(\"correct\");\n  } else if (result.status === \"paused\") {\n    // CTF is paused\n    result_notification.addClass(\"alert alert-warning alert-dismissable text-center\");\n    result_notification.slideDown();\n  } else if (result.status === \"ratelimited\") {\n    // Keys per minute too high\n    result_notification.addClass(\"alert alert-warning alert-dismissable text-center\");\n    result_notification.slideDown();\n    answer_input.addClass(\"too-fast\");\n    setTimeout(function () {\n      answer_input.removeClass(\"too-fast\");\n    }, 3000);\n  }\n\n  setTimeout(function () {\n    (0, _jquery.default)(\".alert\").slideUp();\n    (0, _jquery.default)(\"#submit-key\").removeClass(\"disabled-button\");\n    (0, _jquery.default)(\"#submit-key\").prop(\"disabled\", false);\n  }, 3000);\n\n  if (cb) {\n    cb(result);\n  }\n}\n\nfunction loadChalTemplate(challenge) {\n  _CTFd.default._internal.challenge = {};\n\n  _jquery.default.getScript(_CTFd.default.config.urlRoot + challenge.scripts.view, function () {\n    _jquery.default.get(_CTFd.default.config.urlRoot + challenge.templates.create, function (template_data) {\n      var template = _nunjucks.default.compile(template_data);\n\n      (0, _jquery.default)(\"#create-chal-entry-div\").html(template.render({\n        nonce: _CTFd.default.config.csrfNonce,\n        script_root: _CTFd.default.config.urlRoot\n      }));\n\n      _jquery.default.getScript(_CTFd.default.config.urlRoot + challenge.scripts.create, function () {\n        (0, _jquery.default)(\"#create-chal-entry-div form\").submit(function (event) {\n          event.preventDefault();\n          var params = (0, _jquery.default)(\"#create-chal-entry-div form\").serializeJSON();\n\n          _CTFd.default.fetch(\"/api/v1/challenges\", {\n            method: \"POST\",\n            credentials: \"same-origin\",\n            headers: {\n              Accept: \"application/json\",\n              \"Content-Type\": \"application/json\"\n            },\n            body: JSON.stringify(params)\n          }).then(function (response) {\n            return response.json();\n          }).then(function (response) {\n            if (response.success) {\n              (0, _jquery.default)(\"#challenge-create-options #challenge_id\").val(response.data.id);\n              (0, _jquery.default)(\"#challenge-create-options\").modal();\n            }\n          });\n        });\n      });\n    });\n  });\n}\n\nfunction handleChallengeOptions(event) {\n  event.preventDefault();\n  var params = (0, _jquery.default)(event.target).serializeJSON(true);\n  var flag_params = {\n    challenge_id: params.challenge_id,\n    content: params.flag || \"\",\n    type: params.flag_type,\n    data: params.flag_data ? params.flag_data : \"\"\n  }; // Define a save_challenge function\n\n  var save_challenge = function save_challenge() {\n    _CTFd.default.fetch(\"/api/v1/challenges/\" + params.challenge_id, {\n      method: \"PATCH\",\n      credentials: \"same-origin\",\n      headers: {\n        Accept: \"application/json\",\n        \"Content-Type\": \"application/json\"\n      },\n      body: JSON.stringify({\n        state: params.state\n      })\n    }).then(function (response) {\n      return response.json();\n    }).then(function (data) {\n      if (data.success) {\n        setTimeout(function () {\n          window.location = _CTFd.default.config.urlRoot + \"/admin/challenges/\" + params.challenge_id;\n        }, 700);\n      }\n    });\n  };\n\n  Promise.all([// Save flag\n  new Promise(function (resolve, reject) {\n    if (flag_params.content.length == 0) {\n      resolve();\n      return;\n    }\n\n    _CTFd.default.fetch(\"/api/v1/flags\", {\n      method: \"POST\",\n      credentials: \"same-origin\",\n      headers: {\n        Accept: \"application/json\",\n        \"Content-Type\": \"application/json\"\n      },\n      body: JSON.stringify(flag_params)\n    }).then(function (response) {\n      resolve(response.json());\n    });\n  }), // Upload files\n  new Promise(function (resolve, reject) {\n    var form = event.target;\n    var data = {\n      challenge: params.challenge_id,\n      type: \"challenge\"\n    };\n    var filepath = (0, _jquery.default)(form.elements[\"file\"]).val();\n\n    if (filepath) {\n      _helpers.default.files.upload(form, data);\n    }\n\n    resolve();\n  })]).then(function (responses) {\n    save_challenge();\n  });\n}\n\nfunction createChallenge(event) {\n  var challenge = (0, _jquery.default)(this).find(\"option:selected\").data(\"meta\");\n\n  if (challenge === undefined) {\n    (0, _jquery.default)(\"#create-chal-entry-div\").empty();\n    return;\n  }\n\n  loadChalTemplate(challenge);\n}\n\n(0, _jquery.default)(function () {\n  (0, _jquery.default)(\".preview-challenge\").click(function (e) {\n    window.challenge = new Object();\n    _CTFd.default._internal.challenge = {};\n\n    _jquery.default.get(_CTFd.default.config.urlRoot + \"/api/v1/challenges/\" + CHALLENGE_ID, function (response) {\n      var challenge = _CTFd.default._internal.challenge;\n      var challenge_data = response.data;\n      challenge_data[\"solves\"] = null;\n\n      _jquery.default.getScript(_CTFd.default.config.urlRoot + challenge_data.type_data.scripts.view, function () {\n        _jquery.default.get(_CTFd.default.config.urlRoot + challenge_data.type_data.templates.view, function (template_data) {\n          (0, _jquery.default)(\"#challenge-window\").empty();\n\n          var template = _nunjucks.default.compile(template_data); // window.challenge.data = challenge_data;\n          // window.challenge.preRender();\n\n\n          challenge.data = challenge_data;\n          challenge.preRender();\n          challenge_data[\"description\"] = challenge.render(challenge_data[\"description\"]);\n          challenge_data[\"script_root\"] = _CTFd.default.config.urlRoot;\n          (0, _jquery.default)(\"#challenge-window\").append(template.render(challenge_data));\n          (0, _jquery.default)(\".challenge-solves\").click(function (e) {\n            getsolves((0, _jquery.default)(\"#challenge-id\").val());\n          });\n          (0, _jquery.default)(\".nav-tabs a\").click(function (e) {\n            e.preventDefault();\n            (0, _jquery.default)(this).tab(\"show\");\n          }); // Handle modal toggling\n\n          (0, _jquery.default)(\"#challenge-window\").on(\"hide.bs.modal\", function (event) {\n            (0, _jquery.default)(\"#submission-input\").removeClass(\"wrong\");\n            (0, _jquery.default)(\"#submission-input\").removeClass(\"correct\");\n            (0, _jquery.default)(\"#incorrect-key\").slideUp();\n            (0, _jquery.default)(\"#correct-key\").slideUp();\n            (0, _jquery.default)(\"#already-solved\").slideUp();\n            (0, _jquery.default)(\"#too-fast\").slideUp();\n          });\n          (0, _jquery.default)(\".load-hint\").on(\"click\", function (event) {\n            loadHint((0, _jquery.default)(this).data(\"hint-id\"));\n          });\n          (0, _jquery.default)(\"#submit-key\").click(function (e) {\n            e.preventDefault();\n            (0, _jquery.default)(\"#submit-key\").addClass(\"disabled-button\");\n            (0, _jquery.default)(\"#submit-key\").prop(\"disabled\", true);\n\n            _CTFd.default._internal.challenge.submit(true).then(renderSubmissionResponse); // Preview passed as true\n\n          });\n          (0, _jquery.default)(\"#submission-input\").keyup(function (event) {\n            if (event.keyCode == 13) {\n              (0, _jquery.default)(\"#submit-key\").click();\n            }\n          });\n          (0, _jquery.default)(\".input-field\").bind({\n            focus: function focus() {\n              (0, _jquery.default)(this).parent().addClass(\"input--filled\");\n              $label = (0, _jquery.default)(this).siblings(\".input-label\");\n            },\n            blur: function blur() {\n              if ((0, _jquery.default)(this).val() === \"\") {\n                (0, _jquery.default)(this).parent().removeClass(\"input--filled\");\n                $label = (0, _jquery.default)(this).siblings(\".input-label\");\n                $label.removeClass(\"input--hide\");\n              }\n            }\n          });\n          challenge.postRender();\n          window.location.replace(window.location.href.split(\"#\")[0] + \"#preview\");\n          (0, _jquery.default)(\"#challenge-window\").modal();\n        });\n      });\n    });\n  });\n  (0, _jquery.default)(\".delete-challenge\").click(function (e) {\n    (0, _ezq.ezQuery)({\n      title: \"Delete Challenge\",\n      body: \"Are you sure you want to delete {0}\".format(\"<strong>\" + (0, _utils.htmlEntities)(CHALLENGE_NAME) + \"</strong>\"),\n      success: function success() {\n        _CTFd.default.fetch(\"/api/v1/challenges/\" + CHALLENGE_ID, {\n          method: \"DELETE\"\n        }).then(function (response) {\n          return response.json();\n        }).then(function (response) {\n          if (response.success) {\n            window.location = _CTFd.default.config.urlRoot + \"/admin/challenges\";\n          }\n        });\n      }\n    });\n  });\n  (0, _jquery.default)(\"#challenge-update-container > form\").submit(function (e) {\n    e.preventDefault();\n    var params = (0, _jquery.default)(e.target).serializeJSON(true);\n\n    _CTFd.default.fetch(\"/api/v1/challenges/\" + CHALLENGE_ID + \"/flags\", {\n      method: \"GET\",\n      credentials: \"same-origin\",\n      headers: {\n        Accept: \"application/json\",\n        \"Content-Type\": \"application/json\"\n      }\n    }).then(function (response) {\n      return response.json();\n    }).then(function (response) {\n      var update_challenge = function update_challenge() {\n        _CTFd.default.fetch(\"/api/v1/challenges/\" + CHALLENGE_ID, {\n          method: \"PATCH\",\n          credentials: \"same-origin\",\n          headers: {\n            Accept: \"application/json\",\n            \"Content-Type\": \"application/json\"\n          },\n          body: JSON.stringify(params)\n        }).then(function (response) {\n          return response.json();\n        }).then(function (data) {\n          if (data.success) {\n            (0, _ezq.ezToast)({\n              title: \"Success\",\n              body: \"Your challenge has been updated!\"\n            });\n          }\n        });\n      }; // Check if the challenge doesn't have any flags before marking visible\n\n\n      if (response.data.length === 0 && params.state === \"visible\") {\n        (0, _ezq.ezQuery)({\n          title: \"Missing Flags\",\n          body: \"This challenge does not have any flags meaning it is unsolveable. Are you sure you'd like to update this challenge?\",\n          success: update_challenge\n        });\n      } else {\n        update_challenge();\n      }\n    });\n  });\n  (0, _jquery.default)(\"#challenge-create-options form\").submit(handleChallengeOptions);\n  (0, _jquery.default)(\".nav-tabs a\").click(function (e) {\n    (0, _jquery.default)(this).tab(\"show\");\n    window.location.hash = this.hash;\n  });\n\n  if (window.location.hash) {\n    var hash = window.location.hash.replace(\"<>[]'\\\"\", \"\");\n    (0, _jquery.default)('nav a[href=\"' + hash + '\"]').tab(\"show\");\n  }\n\n  (0, _jquery.default)(\"#tags-add-input\").keyup(_tags.addTag);\n  (0, _jquery.default)(\".delete-tag\").click(_tags.deleteTag);\n  (0, _jquery.default)(\"#prerequisite-add-form\").submit(_requirements.addRequirement);\n  (0, _jquery.default)(\".delete-requirement\").click(_requirements.deleteRequirement);\n  (0, _jquery.default)(\"#file-add-form\").submit(_files.addFile);\n  (0, _jquery.default)(\".delete-file\").click(_files.deleteFile);\n  (0, _jquery.default)(\"#hint-add-button\").click(_hints.showHintModal);\n  (0, _jquery.default)(\".delete-hint\").click(_hints.deleteHint);\n  (0, _jquery.default)(\".edit-hint\").click(_hints.showEditHintModal);\n  (0, _jquery.default)(\"#hint-edit-form\").submit(_hints.editHint);\n  (0, _jquery.default)(\"#flag-add-button\").click(_flags.addFlagModal);\n  (0, _jquery.default)(\".delete-flag\").click(_flags.deleteFlag);\n  (0, _jquery.default)(\"#flags-create-select\").change(_flags.flagTypeSelect);\n  (0, _jquery.default)(\".edit-flag\").click(_flags.editFlagModal);\n\n  _jquery.default.get(_CTFd.default.config.urlRoot + \"/api/v1/challenges/types\", function (response) {\n    (0, _jquery.default)(\"#create-chals-select\").empty();\n    var data = response.data;\n    var chal_type_amt = Object.keys(data).length;\n\n    if (chal_type_amt > 1) {\n      var option = \"<option> -- </option>\";\n      (0, _jquery.default)(\"#create-chals-select\").append(option);\n\n      for (var key in data) {\n        var challenge = data[key];\n\n        var _option = (0, _jquery.default)(\"<option/>\");\n\n        _option.attr(\"value\", challenge.type);\n\n        _option.text(challenge.name);\n\n        _option.data(\"meta\", challenge);\n\n        (0, _jquery.default)(\"#create-chals-select\").append(_option);\n      }\n\n      (0, _jquery.default)(\"#create-chals-select-div\").show();\n      (0, _jquery.default)(\"#create-chals-select\").val(\"standard\");\n      loadChalTemplate(data[\"standard\"]);\n    } else if (chal_type_amt == 1) {\n      var _key = Object.keys(data)[0];\n      (0, _jquery.default)(\"#create-chals-select\").empty();\n      loadChalTemplate(data[_key]);\n    }\n  });\n\n  (0, _jquery.default)(\"#create-chals-select\").change(createChallenge);\n});\n\n//# sourceURL=webpack:///./CTFd/themes/admin/assets/js/pages/challenge.js?");

/***/ })

/******/ });