(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["helpers"],{

/***/ "./CTFd/themes/core/assets/js/helpers.js":
/*!***********************************************!*\
  !*** ./CTFd/themes/core/assets/js/helpers.js ***!
  \***********************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\nObject.defineProperty(exports, \"__esModule\", {\n  value: true\n});\nexports.default = void 0;\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _ezq = _interopRequireDefault(__webpack_require__(/*! ./ezq */ \"./CTFd/themes/core/assets/js/ezq.js\"));\n\nvar _utils = __webpack_require__(/*! ./utils */ \"./CTFd/themes/core/assets/js/utils.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nfunction _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }\n\nfunction _nonIterableRest() { throw new TypeError(\"Invalid attempt to destructure non-iterable instance\"); }\n\nfunction _iterableToArrayLimit(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i[\"return\"] != null) _i[\"return\"](); } finally { if (_d) throw _e; } } return _arr; }\n\nfunction _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }\n\nvar utils = {\n  htmlEntities: _utils.htmlEntities,\n  colorHash: _utils.colorHash,\n  copyToClipboard: _utils.copyToClipboard\n};\nvar files = {\n  upload: function upload(form, extra_data, cb) {\n    var CTFd = window.CTFd;\n\n    if (form instanceof _jquery.default) {\n      form = form[0];\n    }\n\n    var formData = new FormData(form);\n    formData.append(\"nonce\", CTFd.config.csrfNonce);\n\n    for (var _i = 0, _Object$entries = Object.entries(extra_data); _i < _Object$entries.length; _i++) {\n      var _Object$entries$_i = _slicedToArray(_Object$entries[_i], 2),\n          key = _Object$entries$_i[0],\n          value = _Object$entries$_i[1];\n\n      formData.append(key, value);\n    }\n\n    var pg = _ezq.default.ezProgressBar({\n      width: 0,\n      title: \"Upload Progress\"\n    });\n\n    _jquery.default.ajax({\n      url: CTFd.config.urlRoot + \"/api/v1/files\",\n      data: formData,\n      type: \"POST\",\n      cache: false,\n      contentType: false,\n      processData: false,\n      xhr: function xhr() {\n        var xhr = _jquery.default.ajaxSettings.xhr();\n\n        xhr.upload.onprogress = function (e) {\n          if (e.lengthComputable) {\n            var width = e.loaded / e.total * 100;\n            pg = _ezq.default.ezProgressBar({\n              target: pg,\n              width: width\n            });\n          }\n        };\n\n        return xhr;\n      },\n      success: function success(data) {\n        form.reset();\n        pg = _ezq.default.ezProgressBar({\n          target: pg,\n          width: 100\n        });\n        setTimeout(function () {\n          pg.modal(\"hide\");\n        }, 500);\n\n        if (cb) {\n          cb(data);\n        }\n      }\n    });\n  }\n};\nvar helpers = {\n  files: files,\n  utils: utils,\n  ezq: _ezq.default\n};\nvar _default = helpers;\nexports.default = _default;\n\n//# sourceURL=webpack:///./CTFd/themes/core/assets/js/helpers.js?");

/***/ }),

/***/ "./node_modules/markdown-it/lib/helpers/index.js":
/*!*******************************************************!*\
  !*** ./node_modules/markdown-it/lib/helpers/index.js ***!
  \*******************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("// Just a shortcut for bulk export\n\n\nexports.parseLinkLabel = __webpack_require__(/*! ./parse_link_label */ \"./node_modules/markdown-it/lib/helpers/parse_link_label.js\");\nexports.parseLinkDestination = __webpack_require__(/*! ./parse_link_destination */ \"./node_modules/markdown-it/lib/helpers/parse_link_destination.js\");\nexports.parseLinkTitle = __webpack_require__(/*! ./parse_link_title */ \"./node_modules/markdown-it/lib/helpers/parse_link_title.js\");\n\n//# sourceURL=webpack:///./node_modules/markdown-it/lib/helpers/index.js?");

/***/ }),

/***/ "./node_modules/markdown-it/lib/helpers/parse_link_destination.js":
/*!************************************************************************!*\
  !*** ./node_modules/markdown-it/lib/helpers/parse_link_destination.js ***!
  \************************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("// Parse link destination\n//\n\n\nvar unescapeAll = __webpack_require__(/*! ../common/utils */ \"./node_modules/markdown-it/lib/common/utils.js\").unescapeAll;\n\nmodule.exports = function parseLinkDestination(str, pos, max) {\n  var code,\n      level,\n      lines = 0,\n      start = pos,\n      result = {\n    ok: false,\n    pos: 0,\n    lines: 0,\n    str: ''\n  };\n\n  if (str.charCodeAt(pos) === 0x3C\n  /* < */\n  ) {\n      pos++;\n\n      while (pos < max) {\n        code = str.charCodeAt(pos);\n\n        if (code === 0x0A\n        /* \\n */\n        ) {\n            return result;\n          }\n\n        if (code === 0x3E\n        /* > */\n        ) {\n            result.pos = pos + 1;\n            result.str = unescapeAll(str.slice(start + 1, pos));\n            result.ok = true;\n            return result;\n          }\n\n        if (code === 0x5C\n        /* \\ */\n        && pos + 1 < max) {\n          pos += 2;\n          continue;\n        }\n\n        pos++;\n      } // no closing '>'\n\n\n      return result;\n    } // this should be ... } else { ... branch\n\n\n  level = 0;\n\n  while (pos < max) {\n    code = str.charCodeAt(pos);\n\n    if (code === 0x20) {\n      break;\n    } // ascii control characters\n\n\n    if (code < 0x20 || code === 0x7F) {\n      break;\n    }\n\n    if (code === 0x5C\n    /* \\ */\n    && pos + 1 < max) {\n      pos += 2;\n      continue;\n    }\n\n    if (code === 0x28\n    /* ( */\n    ) {\n        level++;\n      }\n\n    if (code === 0x29\n    /* ) */\n    ) {\n        if (level === 0) {\n          break;\n        }\n\n        level--;\n      }\n\n    pos++;\n  }\n\n  if (start === pos) {\n    return result;\n  }\n\n  if (level !== 0) {\n    return result;\n  }\n\n  result.str = unescapeAll(str.slice(start, pos));\n  result.lines = lines;\n  result.pos = pos;\n  result.ok = true;\n  return result;\n};\n\n//# sourceURL=webpack:///./node_modules/markdown-it/lib/helpers/parse_link_destination.js?");

/***/ }),

/***/ "./node_modules/markdown-it/lib/helpers/parse_link_label.js":
/*!******************************************************************!*\
  !*** ./node_modules/markdown-it/lib/helpers/parse_link_label.js ***!
  \******************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("// Parse link label\n//\n// this function assumes that first character (\"[\") already matches;\n// returns the end of the label\n//\n\n\nmodule.exports = function parseLinkLabel(state, start, disableNested) {\n  var level,\n      found,\n      marker,\n      prevPos,\n      labelEnd = -1,\n      max = state.posMax,\n      oldPos = state.pos;\n  state.pos = start + 1;\n  level = 1;\n\n  while (state.pos < max) {\n    marker = state.src.charCodeAt(state.pos);\n\n    if (marker === 0x5D\n    /* ] */\n    ) {\n        level--;\n\n        if (level === 0) {\n          found = true;\n          break;\n        }\n      }\n\n    prevPos = state.pos;\n    state.md.inline.skipToken(state);\n\n    if (marker === 0x5B\n    /* [ */\n    ) {\n        if (prevPos === state.pos - 1) {\n          // increase level if we find text `[`, which is not a part of any token\n          level++;\n        } else if (disableNested) {\n          state.pos = oldPos;\n          return -1;\n        }\n      }\n  }\n\n  if (found) {\n    labelEnd = state.pos;\n  } // restore old state\n\n\n  state.pos = oldPos;\n  return labelEnd;\n};\n\n//# sourceURL=webpack:///./node_modules/markdown-it/lib/helpers/parse_link_label.js?");

/***/ }),

/***/ "./node_modules/markdown-it/lib/helpers/parse_link_title.js":
/*!******************************************************************!*\
  !*** ./node_modules/markdown-it/lib/helpers/parse_link_title.js ***!
  \******************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("// Parse link title\n//\n\n\nvar unescapeAll = __webpack_require__(/*! ../common/utils */ \"./node_modules/markdown-it/lib/common/utils.js\").unescapeAll;\n\nmodule.exports = function parseLinkTitle(str, pos, max) {\n  var code,\n      marker,\n      lines = 0,\n      start = pos,\n      result = {\n    ok: false,\n    pos: 0,\n    lines: 0,\n    str: ''\n  };\n\n  if (pos >= max) {\n    return result;\n  }\n\n  marker = str.charCodeAt(pos);\n\n  if (marker !== 0x22\n  /* \" */\n  && marker !== 0x27\n  /* ' */\n  && marker !== 0x28\n  /* ( */\n  ) {\n      return result;\n    }\n\n  pos++; // if opening marker is \"(\", switch it to closing marker \")\"\n\n  if (marker === 0x28) {\n    marker = 0x29;\n  }\n\n  while (pos < max) {\n    code = str.charCodeAt(pos);\n\n    if (code === marker) {\n      result.pos = pos + 1;\n      result.lines = lines;\n      result.str = unescapeAll(str.slice(start + 1, pos));\n      result.ok = true;\n      return result;\n    } else if (code === 0x0A) {\n      lines++;\n    } else if (code === 0x5C\n    /* \\ */\n    && pos + 1 < max) {\n      pos++;\n\n      if (str.charCodeAt(pos) === 0x0A) {\n        lines++;\n      }\n    }\n\n    pos++;\n  }\n\n  return result;\n};\n\n//# sourceURL=webpack:///./node_modules/markdown-it/lib/helpers/parse_link_title.js?");

/***/ })

}]);