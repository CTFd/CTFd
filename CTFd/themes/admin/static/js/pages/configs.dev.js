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
/******/ 		"pages/configs": 0
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
/******/ 	deferredModules.push(["./CTFd/themes/admin/assets/js/pages/configs.js","helpers","vendor","default~pages/challenge~pages/challenges~pages/configs~pages/editor~pages/main~pages/notifications~p~d5a3cc0a"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./CTFd/themes/admin/assets/js/pages/configs.js":
/*!******************************************************!*\
  !*** ./CTFd/themes/admin/assets/js/pages/configs.js ***!
  \******************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\n__webpack_require__(/*! ./main */ \"./CTFd/themes/admin/assets/js/pages/main.js\");\n\n__webpack_require__(/*! core/utils */ \"./CTFd/themes/core/assets/js/utils.js\");\n\n__webpack_require__(/*! bootstrap/js/dist/tab */ \"./node_modules/bootstrap/js/dist/tab.js\");\n\nvar _momentTimezone = _interopRequireDefault(__webpack_require__(/*! moment-timezone */ \"./node_modules/moment-timezone/index.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! core/CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _helpers = _interopRequireDefault(__webpack_require__(/*! core/helpers */ \"./CTFd/themes/core/assets/js/helpers.js\"));\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _ezq = __webpack_require__(/*! core/ezq */ \"./CTFd/themes/core/assets/js/ezq.js\");\n\nvar _codemirror = _interopRequireDefault(__webpack_require__(/*! codemirror */ \"./node_modules/codemirror/lib/codemirror.js\"));\n\n__webpack_require__(/*! codemirror/mode/htmlmixed/htmlmixed.js */ \"./node_modules/codemirror/mode/htmlmixed/htmlmixed.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nfunction loadTimestamp(place, timestamp) {\n  if (typeof timestamp == \"string\") {\n    timestamp = parseInt(timestamp, 10);\n  }\n\n  var m = (0, _momentTimezone.default)(timestamp * 1000);\n  (0, _jquery.default)(\"#\" + place + \"-month\").val(m.month() + 1); // Months are zero indexed (http://momentjs.com/docs/#/get-set/month/)\n\n  (0, _jquery.default)(\"#\" + place + \"-day\").val(m.date());\n  (0, _jquery.default)(\"#\" + place + \"-year\").val(m.year());\n  (0, _jquery.default)(\"#\" + place + \"-hour\").val(m.hour());\n  (0, _jquery.default)(\"#\" + place + \"-minute\").val(m.minute());\n  loadDateValues(place);\n}\n\nfunction loadDateValues(place) {\n  var month = (0, _jquery.default)(\"#\" + place + \"-month\").val();\n  var day = (0, _jquery.default)(\"#\" + place + \"-day\").val();\n  var year = (0, _jquery.default)(\"#\" + place + \"-year\").val();\n  var hour = (0, _jquery.default)(\"#\" + place + \"-hour\").val();\n  var minute = (0, _jquery.default)(\"#\" + place + \"-minute\").val();\n  var timezone = (0, _jquery.default)(\"#\" + place + \"-timezone\").val();\n  var utc = convertDateToMoment(month, day, year, hour, minute);\n\n  if (isNaN(utc.unix())) {\n    (0, _jquery.default)(\"#\" + place).val(\"\");\n    (0, _jquery.default)(\"#\" + place + \"-local\").val(\"\");\n    (0, _jquery.default)(\"#\" + place + \"-zonetime\").val(\"\");\n  } else {\n    (0, _jquery.default)(\"#\" + place).val(utc.unix());\n    (0, _jquery.default)(\"#\" + place + \"-local\").val(utc.local().format(\"dddd, MMMM Do YYYY, h:mm:ss a zz\"));\n    (0, _jquery.default)(\"#\" + place + \"-zonetime\").val(utc.tz(timezone).format(\"dddd, MMMM Do YYYY, h:mm:ss a zz\"));\n  }\n}\n\nfunction convertDateToMoment(month, day, year, hour, minute) {\n  var month_num = month.toString();\n\n  if (month_num.length == 1) {\n    month_num = \"0\" + month_num;\n  }\n\n  var day_str = day.toString();\n\n  if (day_str.length == 1) {\n    day_str = \"0\" + day_str;\n  }\n\n  var hour_str = hour.toString();\n\n  if (hour_str.length == 1) {\n    hour_str = \"0\" + hour_str;\n  }\n\n  var min_str = minute.toString();\n\n  if (min_str.length == 1) {\n    min_str = \"0\" + min_str;\n  } // 2013-02-08 24:00\n\n\n  var date_string = year.toString() + \"-\" + month_num + \"-\" + day_str + \" \" + hour_str + \":\" + min_str + \":00\";\n  return (0, _momentTimezone.default)(date_string, _momentTimezone.default.ISO_8601);\n}\n\nfunction updateConfigs(event) {\n  event.preventDefault();\n  var obj = (0, _jquery.default)(this).serializeJSON();\n  var params = {};\n\n  if (obj.mail_useauth === false) {\n    obj.mail_username = null;\n    obj.mail_password = null;\n  } else {\n    if (obj.mail_username === \"\") {\n      delete obj.mail_username;\n    }\n\n    if (obj.mail_password === \"\") {\n      delete obj.mail_password;\n    }\n  }\n\n  Object.keys(obj).forEach(function (x) {\n    if (obj[x] === \"true\") {\n      params[x] = true;\n    } else if (obj[x] === \"false\") {\n      params[x] = false;\n    } else {\n      params[x] = obj[x];\n    }\n  });\n\n  _CTFd.default.api.patch_config_list({}, params).then(function (_response) {\n    window.location.reload();\n  });\n}\n\nfunction uploadLogo(event) {\n  event.preventDefault();\n  var form = event.target;\n\n  _helpers.default.files.upload(form, {}, function (response) {\n    var f = response.data[0];\n    var params = {\n      value: f.location\n    };\n\n    _CTFd.default.fetch(\"/api/v1/configs/ctf_logo\", {\n      method: \"PATCH\",\n      body: JSON.stringify(params)\n    }).then(function (response) {\n      return response.json();\n    }).then(function (response) {\n      if (response.success) {\n        window.location.reload();\n      } else {\n        (0, _ezq.ezAlert)({\n          title: \"Error!\",\n          body: \"Logo uploading failed!\",\n          button: \"Okay\"\n        });\n      }\n    });\n  });\n}\n\nfunction removeLogo() {\n  (0, _ezq.ezQuery)({\n    title: \"Remove logo\",\n    body: \"Are you sure you'd like to remove the CTF logo?\",\n    success: function success() {\n      var params = {\n        value: null\n      };\n\n      _CTFd.default.api.patch_config({\n        configKey: \"ctf_logo\"\n      }, params).then(function (_response) {\n        window.location.reload();\n      });\n    }\n  });\n}\n\nfunction importConfig(event) {\n  event.preventDefault();\n  var import_file = document.getElementById(\"import-file\").files[0];\n  var form_data = new FormData();\n  form_data.append(\"backup\", import_file);\n  form_data.append(\"nonce\", _CTFd.default.config.csrfNonce);\n  var pg = (0, _ezq.ezProgressBar)({\n    width: 0,\n    title: \"Upload Progress\"\n  });\n\n  _jquery.default.ajax({\n    url: _CTFd.default.config.urlRoot + \"/admin/import\",\n    type: \"POST\",\n    data: form_data,\n    processData: false,\n    contentType: false,\n    statusCode: {\n      500: function _(resp) {\n        alert(resp.responseText);\n      }\n    },\n    xhr: function xhr() {\n      var xhr = _jquery.default.ajaxSettings.xhr();\n\n      xhr.upload.onprogress = function (e) {\n        if (e.lengthComputable) {\n          var width = e.loaded / e.total * 100;\n          pg = (0, _ezq.ezProgressBar)({\n            target: pg,\n            width: width\n          });\n        }\n      };\n\n      return xhr;\n    },\n    success: function success(_data) {\n      pg = (0, _ezq.ezProgressBar)({\n        target: pg,\n        width: 100\n      });\n      setTimeout(function () {\n        pg.modal(\"hide\");\n      }, 500);\n      setTimeout(function () {\n        window.location.reload();\n      }, 700);\n    }\n  });\n}\n\nfunction exportConfig(event) {\n  event.preventDefault();\n  window.location.href = (0, _jquery.default)(this).attr(\"href\");\n}\n\nfunction insertTimezones(target) {\n  var current = (0, _jquery.default)(\"<option>\").text(_momentTimezone.default.tz.guess());\n  (0, _jquery.default)(target).append(current);\n\n  var tz_names = _momentTimezone.default.tz.names();\n\n  for (var i = 0; i < tz_names.length; i++) {\n    var tz = (0, _jquery.default)(\"<option>\").text(tz_names[i]);\n    (0, _jquery.default)(target).append(tz);\n  }\n}\n\n(0, _jquery.default)(function () {\n  var theme_header_editor = _codemirror.default.fromTextArea(document.getElementById(\"theme-header\"), {\n    lineNumbers: true,\n    lineWrapping: true,\n    mode: \"htmlmixed\",\n    htmlMode: true\n  });\n\n  var theme_footer_editor = _codemirror.default.fromTextArea(document.getElementById(\"theme-footer\"), {\n    lineNumbers: true,\n    lineWrapping: true,\n    mode: \"htmlmixed\",\n    htmlMode: true\n  });\n\n  var theme_settings_editor = _codemirror.default.fromTextArea(document.getElementById(\"theme-settings\"), {\n    lineNumbers: true,\n    lineWrapping: true,\n    mode: {\n      name: \"javascript\",\n      json: true\n    }\n  }); // Handle refreshing codemirror when switching tabs.\n  // Better than the autorefresh approach b/c there's no flicker\n\n\n  (0, _jquery.default)(\"a[href='#theme']\").on(\"shown.bs.tab\", function (_e) {\n    theme_header_editor.refresh();\n    theme_footer_editor.refresh();\n    theme_settings_editor.refresh();\n  });\n  (0, _jquery.default)(\"#theme-settings-modal form\").submit(function (e) {\n    e.preventDefault();\n    theme_settings_editor.getDoc().setValue(JSON.stringify((0, _jquery.default)(this).serializeJSON(), null, 2));\n    (0, _jquery.default)(\"#theme-settings-modal\").modal(\"hide\");\n  });\n  (0, _jquery.default)(\"#theme-settings-button\").click(function () {\n    var form = (0, _jquery.default)(\"#theme-settings-modal form\");\n    var data; // Ignore invalid JSON data\n\n    try {\n      data = JSON.parse(theme_settings_editor.getValue());\n    } catch (e) {\n      data = {};\n    }\n\n    _jquery.default.each(data, function (key, value) {\n      var ctrl = form.find(\"[name='\".concat(key, \"']\"));\n\n      switch (ctrl.prop(\"type\")) {\n        case \"radio\":\n        case \"checkbox\":\n          ctrl.each(function () {\n            if ((0, _jquery.default)(this).attr(\"value\") == value) {\n              (0, _jquery.default)(this).attr(\"checked\", value);\n            }\n          });\n          break;\n\n        default:\n          ctrl.val(value);\n      }\n    });\n\n    (0, _jquery.default)(\"#theme-settings-modal\").modal();\n  });\n  insertTimezones((0, _jquery.default)(\"#start-timezone\"));\n  insertTimezones((0, _jquery.default)(\"#end-timezone\"));\n  insertTimezones((0, _jquery.default)(\"#freeze-timezone\"));\n  (0, _jquery.default)(\".config-section > form:not(.form-upload)\").submit(updateConfigs);\n  (0, _jquery.default)(\"#logo-upload\").submit(uploadLogo);\n  (0, _jquery.default)(\"#remove-logo\").click(removeLogo);\n  (0, _jquery.default)(\"#export-button\").click(exportConfig);\n  (0, _jquery.default)(\"#import-button\").click(importConfig);\n  (0, _jquery.default)(\"#config-color-update\").click(function () {\n    var hex_code = (0, _jquery.default)(\"#config-color-picker\").val();\n    var user_css = theme_header_editor.getValue();\n    var new_css;\n\n    if (user_css.length) {\n      var css_vars = \"theme-color: \".concat(hex_code, \";\");\n      new_css = user_css.replace(/theme-color: (.*);/, css_vars);\n    } else {\n      new_css = \"<style id=\\\"theme-color\\\">\\n\" + \":root {--theme-color: \".concat(hex_code, \";}\\n\") + \".navbar{background-color: var(--theme-color) !important;}\\n\" + \".jumbotron{background-color: var(--theme-color) !important;}\\n\" + \"</style>\\n\";\n    }\n\n    theme_header_editor.getDoc().setValue(new_css);\n  });\n  (0, _jquery.default)(\".start-date\").change(function () {\n    loadDateValues(\"start\");\n  });\n  (0, _jquery.default)(\".end-date\").change(function () {\n    loadDateValues(\"end\");\n  });\n  (0, _jquery.default)(\".freeze-date\").change(function () {\n    loadDateValues(\"freeze\");\n  });\n  var start = (0, _jquery.default)(\"#start\").val();\n  var end = (0, _jquery.default)(\"#end\").val();\n  var freeze = (0, _jquery.default)(\"#freeze\").val();\n\n  if (start) {\n    loadTimestamp(\"start\", start);\n  }\n\n  if (end) {\n    loadTimestamp(\"end\", end);\n  }\n\n  if (freeze) {\n    loadTimestamp(\"freeze\", freeze);\n  } // Toggle username and password based on stored value\n\n\n  (0, _jquery.default)(\"#mail_useauth\").change(function () {\n    (0, _jquery.default)(\"#mail_username_password\").toggle(this.checked);\n  }).change();\n});\n\n//# sourceURL=webpack:///./CTFd/themes/admin/assets/js/pages/configs.js?");

/***/ })

/******/ });