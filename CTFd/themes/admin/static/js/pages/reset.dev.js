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
/******/ 		"pages/reset": 0
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
/******/ 	deferredModules.push(["./CTFd/themes/admin/assets/js/pages/reset.js","vendor"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./CTFd/themes/admin/assets/js/pages/reset.js":
/*!****************************************************!*\
  !*** ./CTFd/themes/admin/assets/js/pages/reset.js ***!
  \****************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _ezq = __webpack_require__(/*! core/ezq */ \"./CTFd/themes/core/assets/js/ezq.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nfunction reset(event) {\n  event.preventDefault();\n  (0, _ezq.ezQuery)({\n    title: \"Reset CTF?\",\n    body: \"Are you sure you want to reset your CTFd instance?\",\n    success: function success() {\n      (0, _jquery.default)(\"#reset-ctf-form\").off(\"submit\").submit();\n    }\n  });\n}\n\n(0, _jquery.default)(function () {\n  (0, _jquery.default)(\"#reset-ctf-form\").submit(reset);\n});\n\n//# sourceURL=webpack:///./CTFd/themes/admin/assets/js/pages/reset.js?");

/***/ }),

/***/ "./CTFd/themes/core/assets/js/ezq.js":
/*!*******************************************!*\
  !*** ./CTFd/themes/core/assets/js/ezq.js ***!
  \*******************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\nObject.defineProperty(exports, \"__esModule\", {\n  value: true\n});\nexports.ezAlert = ezAlert;\nexports.ezToast = ezToast;\nexports.ezQuery = ezQuery;\nexports.ezProgressBar = ezProgressBar;\nexports.ezBadge = ezBadge;\n\n__webpack_require__(/*! bootstrap/js/dist/modal */ \"./node_modules/bootstrap/js/dist/modal.js\");\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nvar modalTpl = '<div class=\"modal fade\" tabindex=\"-1\" role=\"dialog\">' + '  <div class=\"modal-dialog\" role=\"document\">' + '    <div class=\"modal-content\">' + '      <div class=\"modal-header\">' + '        <h5 class=\"modal-title\">{0}</h5>' + '        <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\">' + '          <span aria-hidden=\"true\">&times;</span>' + \"        </button>\" + \"      </div>\" + '      <div class=\"modal-body\">' + \"      </div>\" + '      <div class=\"modal-footer\">' + \"      </div>\" + \"    </div>\" + \"  </div>\" + \"</div>\";\nvar toastTpl = '<div class=\"toast m-3\" role=\"alert\">' + '  <div class=\"toast-header\">' + '    <strong class=\"mr-auto\">{0}</strong>' + '    <button type=\"button\" class=\"ml-2 mb-1 close\" data-dismiss=\"toast\" aria-label=\"Close\">' + '      <span aria-hidden=\"true\">&times;</span>' + \"    </button>\" + \"  </div>\" + '  <div class=\"toast-body\">{1}</div>' + \"</div>\";\nvar progressTpl = '<div class=\"progress\">' + '  <div class=\"progress-bar progress-bar-success progress-bar-striped progress-bar-animated\" role=\"progressbar\" style=\"width: {0}%\">' + \"  </div>\" + \"</div>\";\nvar errorTpl = '<div class=\"alert alert-danger alert-dismissable\" role=\"alert\">\\n' + '  <span class=\"sr-only\">Error:</span>\\n' + \"  {0}\\n\" + '  <button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-label=\"Close\"><span aria-hidden=\"true\">×</span></button>\\n' + \"</div>\";\nvar successTpl = '<div class=\"alert alert-success alert-dismissable submit-row\" role=\"alert\">\\n' + \"  <strong>Success!</strong>\\n\" + \"  {0}\\n\" + '  <button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-label=\"Close\"><span aria-hidden=\"true\">×</span></button>\\n' + \"</div>\";\nvar buttonTpl = '<button type=\"button\" class=\"btn btn-primary\" data-dismiss=\"modal\">{0}</button>';\nvar noTpl = '<button type=\"button\" class=\"btn btn-danger\" data-dismiss=\"modal\">No</button>';\nvar yesTpl = '<button type=\"button\" class=\"btn btn-primary\" data-dismiss=\"modal\">Yes</button>';\n\nfunction ezAlert(args) {\n  var modal = modalTpl.format(args.title, args.body);\n  var obj = (0, _jquery.default)(modal);\n\n  if (typeof args.body === \"string\") {\n    obj.find(\".modal-body\").append(\"<p>\".concat(args.body, \"</p>\"));\n  } else {\n    obj.find(\".modal-body\").append((0, _jquery.default)(args.body));\n  }\n\n  var button = (0, _jquery.default)(buttonTpl.format(args.button));\n\n  if (args.success) {\n    (0, _jquery.default)(button).click(function () {\n      args.success();\n    });\n  }\n\n  if (args.large) {\n    obj.find(\".modal-dialog\").addClass(\"modal-lg\");\n  }\n\n  obj.find(\".modal-footer\").append(button);\n  (0, _jquery.default)(\"main\").append(obj);\n  obj.modal(\"show\");\n  (0, _jquery.default)(obj).on(\"hidden.bs.modal\", function () {\n    (0, _jquery.default)(this).modal(\"dispose\");\n  });\n  return obj;\n}\n\nfunction ezToast(args) {\n  var container_available = (0, _jquery.default)(\"#ezq--notifications-toast-container\").length;\n\n  if (!container_available) {\n    (0, _jquery.default)(\"body\").append((0, _jquery.default)(\"<div/>\").attr({\n      id: \"ezq--notifications-toast-container\"\n    }).css({\n      position: \"fixed\",\n      bottom: \"0\",\n      right: \"0\",\n      \"min-width\": \"20%\"\n    }));\n  }\n\n  var res = toastTpl.format(args.title, args.body);\n  var obj = (0, _jquery.default)(res);\n\n  if (args.onclose) {\n    (0, _jquery.default)(obj).find(\"button[data-dismiss=toast]\").click(function () {\n      args.onclose();\n    });\n  }\n\n  if (args.onclick) {\n    var body = (0, _jquery.default)(obj).find(\".toast-body\");\n    body.addClass(\"cursor-pointer\");\n    body.click(function () {\n      args.onclick();\n    });\n  }\n\n  var autohide = args.autohide || false;\n  var delay = args.delay || 10000; // 10 seconds\n\n  (0, _jquery.default)(\"#ezq--notifications-toast-container\").prepend(obj);\n  obj.toast({\n    autohide: autohide,\n    delay: delay\n  });\n  obj.toast(\"show\");\n  return obj;\n}\n\nfunction ezQuery(args) {\n  var modal = modalTpl.format(args.title, args.body);\n  var obj = (0, _jquery.default)(modal);\n\n  if (typeof args.body === \"string\") {\n    obj.find(\".modal-body\").append(\"<p>\".concat(args.body, \"</p>\"));\n  } else {\n    obj.find(\".modal-body\").append((0, _jquery.default)(args.body));\n  }\n\n  var yes = (0, _jquery.default)(yesTpl);\n  var no = (0, _jquery.default)(noTpl);\n  obj.find(\".modal-footer\").append(no);\n  obj.find(\".modal-footer\").append(yes);\n  (0, _jquery.default)(\"main\").append(obj);\n  (0, _jquery.default)(obj).on(\"hidden.bs.modal\", function () {\n    (0, _jquery.default)(this).modal(\"dispose\");\n  });\n  (0, _jquery.default)(yes).click(function () {\n    args.success();\n  });\n  obj.modal(\"show\");\n  return obj;\n}\n\nfunction ezProgressBar(args) {\n  if (args.target) {\n    var _obj = (0, _jquery.default)(args.target);\n\n    var pbar = _obj.find(\".progress-bar\");\n\n    pbar.css(\"width\", args.width + \"%\");\n    return _obj;\n  }\n\n  var progress = progressTpl.format(args.width);\n  var modal = modalTpl.format(args.title, progress);\n  var obj = (0, _jquery.default)(modal);\n  (0, _jquery.default)(\"main\").append(obj);\n  return obj.modal(\"show\");\n}\n\nfunction ezBadge(args) {\n  var mapping = {\n    success: successTpl,\n    error: errorTpl\n  };\n  var tpl = mapping[args.type].format(args.body);\n  return (0, _jquery.default)(tpl);\n}\n\n//# sourceURL=webpack:///./CTFd/themes/core/assets/js/ezq.js?");

/***/ })

/******/ });