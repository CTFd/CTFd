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
/******/ 		"pages/editor": 0
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
/******/ 	deferredModules.push(["./CTFd/themes/admin/assets/js/pages/editor.js","helpers","vendor","default~pages/challenge~pages/configs~pages/editor~pages/main~pages/notifications~pages/pages~pages/~0fc9fcae"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./CTFd/themes/admin/assets/js/pages/editor.js":
/*!*****************************************************!*\
  !*** ./CTFd/themes/admin/assets/js/pages/editor.js ***!
  \*****************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\n__webpack_require__(/*! ./main */ \"./CTFd/themes/admin/assets/js/pages/main.js\");\n\n__webpack_require__(/*! core/utils */ \"./CTFd/themes/core/assets/js/utils.js\");\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! core/CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _helpers = _interopRequireDefault(__webpack_require__(/*! core/helpers */ \"./CTFd/themes/core/assets/js/helpers.js\"));\n\nvar _codemirror = _interopRequireDefault(__webpack_require__(/*! codemirror */ \"./node_modules/codemirror/lib/codemirror.js\"));\n\nvar _ezq = __webpack_require__(/*! core/ezq */ \"./CTFd/themes/core/assets/js/ezq.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nfunction get_filetype_icon_class(filename) {\n  var mapping = {\n    // Image Files\n    png: \"fa-file-image\",\n    jpg: \"fa-file-image\",\n    jpeg: \"fa-file-image\",\n    gif: \"fa-file-image\",\n    bmp: \"fa-file-image\",\n    svg: \"fa-file-image\",\n    // Text Files\n    txt: \"fa-file-alt\",\n    // Video Files\n    mov: \"fa-file-video\",\n    mp4: \"fa-file-video\",\n    wmv: \"fa-file-video\",\n    flv: \"fa-file-video\",\n    mkv: \"fa-file-video\",\n    avi: \"fa-file-video\",\n    // PDF Files\n    pdf: \"fa-file-pdf\",\n    // Audio Files\n    mp3: \"fa-file-sound\",\n    wav: \"fa-file-sound\",\n    aac: \"fa-file-sound\",\n    // Archive Files\n    zip: \"fa-file-archive\",\n    gz: \"fa-file-archive\",\n    tar: \"fa-file-archive\",\n    \"7z\": \"fa-file-archive\",\n    rar: \"fa-file-archive\",\n    // Code Files\n    py: \"fa-file-code\",\n    c: \"fa-file-code\",\n    cpp: \"fa-file-code\",\n    html: \"fa-file-code\",\n    js: \"fa-file-code\",\n    rb: \"fa-file-code\",\n    go: \"fa-file-code\"\n  };\n  var ext = filename.split(\".\").pop();\n  return mapping[ext];\n}\n\nfunction get_page_files() {\n  return _CTFd.default.fetch(\"/api/v1/files?type=page\", {\n    credentials: \"same-origin\"\n  }).then(function (response) {\n    return response.json();\n  });\n}\n\nfunction show_files(data) {\n  var list = (0, _jquery.default)(\"#media-library-list\");\n  list.empty();\n\n  for (var i = 0; i < data.length; i++) {\n    var f = data[i];\n    var fname = f.location.split(\"/\").pop();\n    var ext = get_filetype_icon_class(f.location);\n    var wrapper = (0, _jquery.default)(\"<div>\").attr(\"class\", \"media-item-wrapper\");\n    var link = (0, _jquery.default)(\"<a>\");\n    link.attr(\"href\", \"##\");\n\n    if (ext === undefined) {\n      link.append('<i class=\"far fa-file\" aria-hidden=\"true\"></i> '.format(ext));\n    } else {\n      link.append('<i class=\"far {0}\" aria-hidden=\"true\"></i> '.format(ext));\n    }\n\n    link.append((0, _jquery.default)(\"<small>\").attr(\"class\", \"media-item-title\").text(fname));\n    link.click(function (e) {\n      var media_div = (0, _jquery.default)(this).parent();\n      var icon = (0, _jquery.default)(this).find(\"i\")[0];\n      var f_loc = media_div.attr(\"data-location\");\n      var fname = media_div.attr(\"data-filename\");\n      var f_id = media_div.attr(\"data-id\");\n      (0, _jquery.default)(\"#media-delete\").attr(\"data-id\", f_id);\n      (0, _jquery.default)(\"#media-link\").val(f_loc);\n      (0, _jquery.default)(\"#media-filename\").html((0, _jquery.default)(\"<a>\").attr(\"href\", f_loc).attr(\"target\", \"_blank\").text(fname));\n      (0, _jquery.default)(\"#media-icon\").empty();\n\n      if ((0, _jquery.default)(icon).hasClass(\"fa-file-image\")) {\n        (0, _jquery.default)(\"#media-icon\").append((0, _jquery.default)(\"<img>\").attr(\"src\", f_loc).css({\n          \"max-width\": \"100%\",\n          \"max-height\": \"100%\",\n          \"object-fit\": \"contain\"\n        }));\n      } else {\n        // icon is empty so we need to pull outerHTML\n        var copy_icon = (0, _jquery.default)(icon).clone();\n        (0, _jquery.default)(copy_icon).addClass(\"fa-4x\");\n        (0, _jquery.default)(\"#media-icon\").append(copy_icon);\n      }\n\n      (0, _jquery.default)(\"#media-item\").show();\n    });\n    wrapper.append(link);\n    wrapper.attr(\"data-location\", _CTFd.default.config.urlRoot + \"/files/\" + f.location);\n    wrapper.attr(\"data-id\", f.id);\n    wrapper.attr(\"data-filename\", fname);\n    list.append(wrapper);\n  }\n}\n\nfunction refresh_files(cb) {\n  get_page_files().then(function (response) {\n    var data = response.data;\n    show_files(data);\n\n    if (cb) {\n      cb();\n    }\n  });\n}\n\nfunction insert_at_cursor(editor, text) {\n  var doc = editor.getDoc();\n  var cursor = doc.getCursor();\n  doc.replaceRange(text, cursor);\n}\n\nfunction submit_form() {\n  // Save the CodeMirror data to the Textarea\n  window.editor.save();\n  var params = (0, _jquery.default)(\"#page-edit\").serializeJSON();\n  var target = \"/api/v1/pages\";\n  var method = \"POST\";\n\n  if (params.id) {\n    target += \"/\" + params.id;\n    method = \"PATCH\";\n  }\n\n  _CTFd.default.fetch(target, {\n    method: method,\n    credentials: \"same-origin\",\n    headers: {\n      Accept: \"application/json\",\n      \"Content-Type\": \"application/json\"\n    },\n    body: JSON.stringify(params)\n  }).then(function (response) {\n    return response.json();\n  }).then(function (response) {\n    if (method === \"PATCH\" && response.success) {\n      (0, _ezq.ezToast)({\n        title: \"Saved\",\n        body: \"Your changes have been saved\"\n      });\n    } else {\n      window.location = _CTFd.default.config.urlRoot + \"/admin/pages/\" + response.data.id;\n    }\n  });\n}\n\nfunction preview_page() {\n  editor.save(); // Save the CodeMirror data to the Textarea\n\n  (0, _jquery.default)(\"#page-edit\").attr(\"action\", _CTFd.default.config.urlRoot + \"/admin/pages/preview\");\n  (0, _jquery.default)(\"#page-edit\").attr(\"target\", \"_blank\");\n  (0, _jquery.default)(\"#page-edit\").submit();\n}\n\nfunction upload_media() {\n  _helpers.default.files.upload((0, _jquery.default)(\"#media-library-upload\"), function (data) {\n    refresh_files();\n  });\n}\n\n(0, _jquery.default)(function () {\n  window.editor = _codemirror.default.fromTextArea(document.getElementById(\"admin-pages-editor\"), {\n    lineNumbers: true,\n    lineWrapping: true,\n    mode: \"xml\",\n    htmlMode: true\n  });\n  (0, _jquery.default)(\"#media-insert\").click(function (e) {\n    var tag = \"\";\n\n    try {\n      tag = (0, _jquery.default)(\"#media-icon\").children()[0].nodeName.toLowerCase();\n    } catch (err) {\n      tag = \"\";\n    }\n\n    var link = (0, _jquery.default)(\"#media-link\").val();\n    var fname = (0, _jquery.default)(\"#media-filename\").text();\n    var entry = null;\n\n    if (tag === \"img\") {\n      entry = \"![{0}]({1})\".format(fname, link);\n    } else {\n      entry = \"[{0}]({1})\".format(fname, link);\n    }\n\n    insert_at_cursor(editor, entry);\n  });\n  (0, _jquery.default)(\"#media-download\").click(function (e) {\n    var link = (0, _jquery.default)(\"#media-link\").val();\n    window.open(link, \"_blank\");\n  });\n  (0, _jquery.default)(\"#media-delete\").click(function (e) {\n    var file_id = (0, _jquery.default)(this).attr(\"data-id\");\n    (0, _ezq.ezQuery)({\n      title: \"Delete File?\",\n      body: \"Are you sure you want to delete this file?\",\n      success: function success() {\n        _CTFd.default.fetch(\"/api/v1/files/\" + file_id, {\n          method: \"DELETE\",\n          credentials: \"same-origin\",\n          headers: {\n            Accept: \"application/json\",\n            \"Content-Type\": \"application/json\"\n          }\n        }).then(function (response) {\n          if (response.status === 200) {\n            response.json().then(function (object) {\n              if (object.success) {\n                refresh_files();\n              }\n            });\n          }\n        });\n      }\n    });\n  });\n  (0, _jquery.default)(\"#save-page\").click(function (e) {\n    e.preventDefault();\n    submit_form();\n  });\n  (0, _jquery.default)(\"#media-button\").click(function () {\n    (0, _jquery.default)(\"#media-library-list\").empty();\n    refresh_files(function () {\n      (0, _jquery.default)(\"#media-modal\").modal();\n    });\n  });\n  (0, _jquery.default)(\".media-upload-button\").click(function () {\n    upload_media();\n  });\n  (0, _jquery.default)(\".preview-page\").click(function () {\n    preview_page();\n  });\n});\n\n//# sourceURL=webpack:///./CTFd/themes/admin/assets/js/pages/editor.js?");

/***/ })

/******/ });