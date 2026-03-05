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
/******/ 		"pages/setup": 0
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
/******/ 	deferredModules.push(["./CTFd/themes/core/assets/js/pages/setup.js","helpers","vendor","default~pages/challenges~pages/main~pages/notifications~pages/scoreboard~pages/settings~pages/setup~~6822bf1f"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./CTFd/themes/core/assets/js/pages/setup.js":
/*!***************************************************!*\
  !*** ./CTFd/themes/core/assets/js/pages/setup.js ***!
  \***************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\n__webpack_require__(/*! ./main */ \"./CTFd/themes/core/assets/js/pages/main.js\");\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _dayjs = _interopRequireDefault(__webpack_require__(/*! dayjs */ \"./node_modules/dayjs/dayjs.min.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! ../CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { \"default\": obj }; }\n\nfunction switchTab(event) {\n  event.preventDefault(); // Handle tab validation\n\n  var valid_tab = true;\n  (0, _jquery[\"default\"])(event.target).closest(\"[role=tabpanel]\").find(\"input,textarea\").each(function (i, e) {\n    var $e = (0, _jquery[\"default\"])(e);\n    var status = e.checkValidity();\n\n    if (status === false) {\n      $e.removeClass(\"input-filled-valid\");\n      $e.addClass(\"input-filled-invalid\");\n      valid_tab = false;\n    }\n  });\n\n  if (valid_tab == false) {\n    return;\n  }\n\n  var href = (0, _jquery[\"default\"])(event.target).data(\"href\");\n  (0, _jquery[\"default\"])(\".nav a[href=\\\"\".concat(href, \"\\\"]\")).tab(\"show\");\n}\n\nfunction processDateTime(datetime) {\n  return function (_event) {\n    var date_picker = (0, _jquery[\"default\"])(\"#\".concat(datetime, \"-date\"));\n    var time_picker = (0, _jquery[\"default\"])(\"#\".concat(datetime, \"-time\"));\n    var unix_time = (0, _dayjs[\"default\"])(\"\".concat(date_picker.val(), \" \").concat(time_picker.val()), \"YYYY-MM-DD HH:mm\").unix();\n\n    if (isNaN(unix_time)) {\n      (0, _jquery[\"default\"])(\"#\".concat(datetime, \"-preview\")).val(\"\");\n    } else {\n      (0, _jquery[\"default\"])(\"#\".concat(datetime, \"-preview\")).val(unix_time);\n    }\n  };\n}\n\nfunction mlcSetup(_event) {\n  var params = {\n    name: (0, _jquery[\"default\"])(\"#ctf_name\").val(),\n    type: \"jeopardy\",\n    description: (0, _jquery[\"default\"])(\"#ctf_description\").val(),\n    user_mode: (0, _jquery[\"default\"])(\"#user_mode\").val(),\n    event_url: window.location.origin + _CTFd[\"default\"].config.urlRoot,\n    redirect_url: window.location.origin + _CTFd[\"default\"].config.urlRoot + \"/redirect\",\n    integration_setup_url: window.location.origin + _CTFd[\"default\"].config.urlRoot + \"/setup/integrations\",\n    start: (0, _jquery[\"default\"])(\"#start-preview\").val(),\n    end: (0, _jquery[\"default\"])(\"#end-preview\").val(),\n    platform: \"CTFd\",\n    state: window.STATE\n  };\n  var ret = [];\n\n  for (var p in params) {\n    ret.push(encodeURIComponent(p) + \"=\" + encodeURIComponent(params[p]));\n  }\n\n  window.open(\"https://www.majorleaguecyber.org/events/new?\" + ret.join(\"&\"), \"_blank\");\n}\n\n(0, _jquery[\"default\"])(function () {\n  (0, _jquery[\"default\"])(\".tab-next\").click(switchTab);\n  (0, _jquery[\"default\"])(\"input\").on(\"keypress\", function (e) {\n    // Hook Enter button\n    if (e.keyCode == 13) {\n      e.preventDefault();\n      (0, _jquery[\"default\"])(e.target).closest(\".tab-pane\").find(\"button[data-href]\").click();\n    }\n  });\n  (0, _jquery[\"default\"])(\"#integration-mlc\").click(mlcSetup);\n  (0, _jquery[\"default\"])(\"#start-date,#start-time\").change(processDateTime(\"start\"));\n  (0, _jquery[\"default\"])(\"#end-date,#end-time\").change(processDateTime(\"end\"));\n  (0, _jquery[\"default\"])(\"#config-color-picker\").on(\"input\", function (_e) {\n    (0, _jquery[\"default\"])(\"#config-color-input\").val((0, _jquery[\"default\"])(this).val());\n  });\n  (0, _jquery[\"default\"])(\"#config-color-reset\").click(function () {\n    (0, _jquery[\"default\"])(\"#config-color-input\").val(\"\");\n    (0, _jquery[\"default\"])(\"#config-color-picker\").val(\"\");\n  });\n  (0, _jquery[\"default\"])(\"#ctf_logo\").on(\"change\", function () {\n    if (this.files[0].size > 128000) {\n      if (!confirm(\"This image file is larger than 128KB which may result in increased load times. Are you sure you'd like to use this logo?\")) {\n        this.value = \"\";\n      }\n    }\n  });\n  (0, _jquery[\"default\"])(\"#ctf_banner\").on(\"change\", function () {\n    if (this.files[0].size > 512000) {\n      if (!confirm(\"This image file is larger than 512KB which may result in increased load times. Are you sure you'd like to use this icon?\")) {\n        this.value = \"\";\n      }\n    }\n  });\n  (0, _jquery[\"default\"])(\"#ctf_small_icon\").on(\"change\", function () {\n    if (this.files[0].size > 32000) {\n      if (!confirm(\"This image file is larger than 32KB which may result in increased load times. Are you sure you'd like to use this icon?\")) {\n        this.value = \"\";\n      }\n    }\n  });\n  window.addEventListener(\"storage\", function (event) {\n    if (event.key == \"integrations\" && event.newValue) {\n      var integration = JSON.parse(event.newValue);\n\n      if (integration[\"name\"] == \"mlc\") {\n        (0, _jquery[\"default\"])(\"#integration-mlc\").text(\"Already Configured\").attr(\"disabled\", true);\n        window.focus();\n        localStorage.removeItem(\"integrations\");\n      }\n    }\n  });\n  (0, _jquery[\"default\"])(\"#setup-form\").submit(function (e) {\n    if ((0, _jquery[\"default\"])(\"#newsletter-checkbox\").prop(\"checked\")) {\n      var email = (0, _jquery[\"default\"])(e.target).find(\"input[name=email]\").val();\n\n      _jquery[\"default\"].ajax({\n        url: \"https://newsletters.ctfd.io/lists/ot889gr1sa0e1/subscribe/post-json?c=?\",\n        data: {\n          email: email,\n          b_38e27f7d496889133d2214208_d7c3ed71f9: \"\"\n        },\n        dataType: \"jsonp\",\n        contentType: \"application/json; charset=utf-8\"\n      });\n    }\n  });\n});\n\n//# sourceURL=webpack:///./CTFd/themes/core/assets/js/pages/setup.js?");

/***/ })

/******/ });