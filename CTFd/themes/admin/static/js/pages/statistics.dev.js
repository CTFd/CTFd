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
/******/ 		"pages/statistics": 0
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
/******/ 	deferredModules.push(["./CTFd/themes/admin/assets/js/pages/statistics.js","helpers","graphs","plotly","vendor","default~pages/challenge~pages/configs~pages/editor~pages/main~pages/notifications~pages/pages~pages/~0fc9fcae"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./CTFd/themes/admin/assets/js/pages/statistics.js":
/*!*********************************************************!*\
  !*** ./CTFd/themes/admin/assets/js/pages/statistics.js ***!
  \*********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\n__webpack_require__(/*! ./main */ \"./CTFd/themes/admin/assets/js/pages/main.js\");\n\n__webpack_require__(/*! core/utils */ \"./CTFd/themes/core/assets/js/utils.js\");\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! core/CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _plotly = _interopRequireDefault(__webpack_require__(/*! plotly.js-basic-dist */ \"./node_modules/plotly.js-basic-dist/plotly-basic.js\"));\n\nvar _graphs = __webpack_require__(/*! core/graphs */ \"./CTFd/themes/core/assets/js/graphs.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nfunction _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }\n\nfunction _nonIterableRest() { throw new TypeError(\"Invalid attempt to destructure non-iterable instance\"); }\n\nfunction _iterableToArrayLimit(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i[\"return\"] != null) _i[\"return\"](); } finally { if (_d) throw _e; } } return _arr; }\n\nfunction _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }\n\nvar graph_configs = {\n  \"#solves-graph\": {\n    layout: function layout(annotations) {\n      return {\n        title: \"Solve Counts\",\n        annotations: annotations,\n        xaxis: {\n          title: \"Challenge Name\"\n        },\n        yaxis: {\n          title: \"Amount of Solves\"\n        }\n      };\n    },\n    fn: function fn() {\n      return \"CTFd_solves_\" + new Date().toISOString().slice(0, 19);\n    },\n    data: function data() {\n      return _CTFd.default.api.get_challenge_solve_statistics();\n    },\n    format: function format(response) {\n      var data = response.data;\n      var chals = [];\n      var counts = [];\n      var annotations = [];\n      var solves = {};\n\n      for (var c = 0; c < data.length; c++) {\n        solves[data[c][\"id\"]] = {\n          name: data[c][\"name\"],\n          solves: data[c][\"solves\"]\n        };\n      }\n\n      var solves_order = Object.keys(solves).sort(function (a, b) {\n        return solves[b].solves - solves[a].solves;\n      });\n\n      _jquery.default.each(solves_order, function (key, value) {\n        chals.push(solves[value].name);\n        counts.push(solves[value].solves);\n        var result = {\n          x: solves[value].name,\n          y: solves[value].solves,\n          text: solves[value].solves,\n          xanchor: \"center\",\n          yanchor: \"bottom\",\n          showarrow: false\n        };\n        annotations.push(result);\n      });\n\n      return [{\n        type: \"bar\",\n        x: chals,\n        y: counts,\n        text: counts,\n        orientation: \"v\"\n      }, annotations];\n    }\n  },\n  \"#keys-pie-graph\": {\n    layout: function layout() {\n      return {\n        title: \"Submission Percentages\"\n      };\n    },\n    fn: function fn() {\n      return \"CTFd_submissions_\" + new Date().toISOString().slice(0, 19);\n    },\n    data: function data() {\n      return _CTFd.default.api.get_submission_property_counts({\n        column: \"type\"\n      });\n    },\n    format: function format(response) {\n      var data = response.data;\n      var solves = data[\"correct\"];\n      var fails = data[\"incorrect\"];\n      return [{\n        values: [solves, fails],\n        labels: [\"Correct\", \"Incorrect\"],\n        marker: {\n          colors: [\"rgb(0, 209, 64)\", \"rgb(207, 38, 0)\"]\n        },\n        text: [\"Solves\", \"Fails\"],\n        hole: 0.4,\n        type: \"pie\"\n      }, null];\n    }\n  },\n  \"#categories-pie-graph\": {\n    layout: function layout() {\n      return {\n        title: \"Category Breakdown\"\n      };\n    },\n    data: function data() {\n      return _CTFd.default.api.get_challenge_property_counts({\n        column: \"category\"\n      });\n    },\n    fn: function fn() {\n      return \"CTFd_categories_\" + new Date().toISOString().slice(0, 19);\n    },\n    format: function format(response) {\n      var data = response.data;\n      var categories = [];\n      var count = [];\n\n      for (var category in data) {\n        if (data.hasOwnProperty(category)) {\n          categories.push(category);\n          count.push(data[category]);\n        }\n      }\n\n      for (var i = 0; i < data.length; i++) {\n        categories.push(data[i].category);\n        count.push(data[i].count);\n      }\n\n      return [{\n        values: count,\n        labels: categories,\n        hole: 0.4,\n        type: \"pie\"\n      }, null];\n    }\n  },\n  \"#solve-percentages-graph\": {\n    layout: function layout(annotations) {\n      return {\n        title: \"Solve Percentages per Challenge\",\n        xaxis: {\n          title: \"Challenge Name\"\n        },\n        yaxis: {\n          title: \"Percentage of {0} (%)\".format(_CTFd.default.config.userMode.charAt(0).toUpperCase() + _CTFd.default.config.userMode.slice(1)),\n          range: [0, 100]\n        },\n        annotations: annotations\n      };\n    },\n    data: function data() {\n      return _CTFd.default.api.get_challenge_solve_percentages();\n    },\n    fn: function fn() {\n      return \"CTFd_challenge_percentages_\" + new Date().toISOString().slice(0, 19);\n    },\n    format: function format(response) {\n      var data = response.data;\n      var names = [];\n      var percents = [];\n      var annotations = [];\n\n      for (var key in data) {\n        names.push(data[key].name);\n        percents.push(data[key].percentage * 100);\n        var result = {\n          x: data[key].name,\n          y: data[key].percentage * 100,\n          text: Math.round(data[key].percentage * 100) + \"%\",\n          xanchor: \"center\",\n          yanchor: \"bottom\",\n          showarrow: false\n        };\n        annotations.push(result);\n      }\n\n      return [{\n        type: \"bar\",\n        x: names,\n        y: percents,\n        orientation: \"v\"\n      }, annotations];\n    }\n  }\n};\nvar config = {\n  displaylogo: false,\n  responsive: true\n};\n\nvar createGraphs = function createGraphs() {\n  var _loop = function _loop(key) {\n    var cfg = graph_configs[key];\n    var $elem = (0, _jquery.default)(key);\n    $elem.empty();\n    $elem[0].fn = cfg.fn();\n    cfg.data().then(cfg.format).then(function (_ref) {\n      var _ref2 = _slicedToArray(_ref, 2),\n          data = _ref2[0],\n          annotations = _ref2[1];\n\n      _plotly.default.newPlot($elem[0], [data], cfg.layout(annotations), config);\n    });\n  };\n\n  for (var key in graph_configs) {\n    _loop(key);\n  }\n};\n\nfunction updateGraphs() {\n  var _loop2 = function _loop2(key) {\n    var cfg = graph_configs[key];\n    var $elem = (0, _jquery.default)(key);\n    cfg.data().then(cfg.format).then(function (_ref3) {\n      var _ref4 = _slicedToArray(_ref3, 2),\n          data = _ref4[0],\n          annotations = _ref4[1];\n\n      // FIXME: Pass annotations\n      _plotly.default.react($elem[0], [data], cfg.layout(annotations), config);\n    });\n  };\n\n  for (var key in graph_configs) {\n    _loop2(key);\n  }\n}\n\n(0, _jquery.default)(function () {\n  createGraphs();\n  setInterval(updateGraphs, 300000);\n});\n\n//# sourceURL=webpack:///./CTFd/themes/admin/assets/js/pages/statistics.js?");

/***/ })

/******/ });