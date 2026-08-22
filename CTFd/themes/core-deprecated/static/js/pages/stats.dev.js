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
/******/ 		"pages/stats": 0
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
/******/ 	deferredModules.push(["./CTFd/themes/core/assets/js/pages/stats.js","helpers","echarts","vendor","default~pages/challenges~pages/main~pages/notifications~pages/scoreboard~pages/settings~pages/setup~~6822bf1f"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./CTFd/themes/core/assets/js/graphs.js":
/*!**********************************************!*\
  !*** ./CTFd/themes/core/assets/js/graphs.js ***!
  \**********************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\nObject.defineProperty(exports, \"__esModule\", {\n  value: true\n});\nexports.createGraph = createGraph;\nexports.updateGraph = updateGraph;\nexports.disposeGraph = disposeGraph;\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _echartsEn = _interopRequireDefault(__webpack_require__(/*! echarts/dist/echarts-en.common */ \"./node_modules/echarts/dist/echarts-en.common.js\"));\n\nvar _dayjs = _interopRequireDefault(__webpack_require__(/*! dayjs */ \"./node_modules/dayjs/dayjs.min.js\"));\n\nvar _utils = __webpack_require__(/*! ./utils */ \"./CTFd/themes/core/assets/js/utils.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { \"default\": obj }; }\n\nvar graph_configs = {\n  score_graph: {\n    format: function format(type, id, name, _account_id, responses) {\n      var option = {\n        title: {\n          left: \"center\",\n          text: \"Score over Time\"\n        },\n        tooltip: {\n          trigger: \"axis\",\n          axisPointer: {\n            type: \"cross\"\n          }\n        },\n        legend: {\n          type: \"scroll\",\n          orient: \"horizontal\",\n          align: \"left\",\n          bottom: 0,\n          data: [name]\n        },\n        toolbox: {\n          feature: {\n            saveAsImage: {}\n          }\n        },\n        grid: {\n          containLabel: true\n        },\n        xAxis: [{\n          type: \"category\",\n          boundaryGap: false,\n          data: []\n        }],\n        yAxis: [{\n          type: \"value\"\n        }],\n        dataZoom: [{\n          id: \"dataZoomX\",\n          type: \"slider\",\n          xAxisIndex: [0],\n          filterMode: \"filter\",\n          height: 20,\n          top: 35,\n          fillerColor: \"rgba(233, 236, 241, 0.4)\"\n        }],\n        series: []\n      };\n      var times = [];\n      var scores = [];\n      var solves = responses[0].data;\n      var awards = responses[2].data;\n      var total = solves.concat(awards);\n      total.sort(function (a, b) {\n        return new Date(a.date) - new Date(b.date);\n      });\n\n      for (var i = 0; i < total.length; i++) {\n        var date = (0, _dayjs[\"default\"])(total[i].date);\n        times.push(date.toDate());\n\n        try {\n          scores.push(total[i].challenge.value);\n        } catch (e) {\n          scores.push(total[i].value);\n        }\n      }\n\n      times.forEach(function (time) {\n        option.xAxis[0].data.push(time);\n      });\n      option.series.push({\n        name: window.stats_data.name,\n        type: \"line\",\n        label: {\n          normal: {\n            show: true,\n            position: \"top\"\n          }\n        },\n        areaStyle: {\n          normal: {\n            color: (0, _utils.colorHash)(name + id)\n          }\n        },\n        itemStyle: {\n          normal: {\n            color: (0, _utils.colorHash)(name + id)\n          }\n        },\n        data: (0, _utils.cumulativeSum)(scores)\n      });\n      return option;\n    }\n  },\n  category_breakdown: {\n    format: function format(type, id, name, account_id, responses) {\n      var option = {\n        title: {\n          left: \"center\",\n          text: \"Category Breakdown\"\n        },\n        tooltip: {\n          trigger: \"item\"\n        },\n        toolbox: {\n          show: true,\n          feature: {\n            saveAsImage: {}\n          }\n        },\n        legend: {\n          type: \"scroll\",\n          orient: \"vertical\",\n          top: \"middle\",\n          right: 0,\n          data: []\n        },\n        series: [{\n          name: \"Category Breakdown\",\n          type: \"pie\",\n          radius: [\"30%\", \"50%\"],\n          avoidLabelOverlap: false,\n          label: {\n            show: false,\n            position: \"center\"\n          },\n          itemStyle: {\n            normal: {\n              label: {\n                show: true,\n                formatter: function formatter(data) {\n                  return \"\".concat(data.percent, \"% (\").concat(data.value, \")\");\n                }\n              },\n              labelLine: {\n                show: true\n              }\n            },\n            emphasis: {\n              label: {\n                show: true,\n                position: \"center\",\n                textStyle: {\n                  fontSize: \"14\",\n                  fontWeight: \"normal\"\n                }\n              }\n            }\n          },\n          emphasis: {\n            label: {\n              show: true,\n              fontSize: \"30\",\n              fontWeight: \"bold\"\n            }\n          },\n          labelLine: {\n            show: false\n          },\n          data: []\n        }]\n      };\n      var solves = responses[0].data;\n      var categories = [];\n\n      for (var i = 0; i < solves.length; i++) {\n        categories.push(solves[i].challenge.category);\n      }\n\n      var keys = categories.filter(function (elem, pos) {\n        return categories.indexOf(elem) == pos;\n      });\n      var counts = [];\n\n      for (var _i = 0; _i < keys.length; _i++) {\n        var count = 0;\n\n        for (var x = 0; x < categories.length; x++) {\n          if (categories[x] == keys[_i]) {\n            count++;\n          }\n        }\n\n        counts.push(count);\n      }\n\n      keys.forEach(function (category, index) {\n        option.legend.data.push(category);\n        option.series[0].data.push({\n          value: counts[index],\n          name: category,\n          itemStyle: {\n            color: (0, _utils.colorHash)(category)\n          }\n        });\n      });\n      return option;\n    }\n  },\n  solve_percentages: {\n    format: function format(type, id, name, account_id, responses) {\n      var solves_count = responses[0].data.length;\n      var fails_count = responses[1].meta.count;\n      var option = {\n        title: {\n          left: \"center\",\n          text: \"Solve Percentages\"\n        },\n        tooltip: {\n          trigger: \"item\"\n        },\n        toolbox: {\n          show: true,\n          feature: {\n            saveAsImage: {}\n          }\n        },\n        legend: {\n          orient: \"vertical\",\n          top: \"middle\",\n          right: 0,\n          data: [\"Fails\", \"Solves\"]\n        },\n        series: [{\n          name: \"Solve Percentages\",\n          type: \"pie\",\n          radius: [\"30%\", \"50%\"],\n          avoidLabelOverlap: false,\n          label: {\n            show: false,\n            position: \"center\"\n          },\n          itemStyle: {\n            normal: {\n              label: {\n                show: true,\n                formatter: function formatter(data) {\n                  return \"\".concat(data.name, \" - \").concat(data.value, \" (\").concat(data.percent, \"%)\");\n                }\n              },\n              labelLine: {\n                show: true\n              }\n            },\n            emphasis: {\n              label: {\n                show: true,\n                position: \"center\",\n                textStyle: {\n                  fontSize: \"14\",\n                  fontWeight: \"normal\"\n                }\n              }\n            }\n          },\n          emphasis: {\n            label: {\n              show: true,\n              fontSize: \"30\",\n              fontWeight: \"bold\"\n            }\n          },\n          labelLine: {\n            show: false\n          },\n          data: [{\n            value: fails_count,\n            name: \"Fails\",\n            itemStyle: {\n              color: \"rgb(207, 38, 0)\"\n            }\n          }, {\n            value: solves_count,\n            name: \"Solves\",\n            itemStyle: {\n              color: \"rgb(0, 209, 64)\"\n            }\n          }]\n        }]\n      };\n      return option;\n    }\n  }\n};\n\nfunction createGraph(graph_type, target, data, type, id, name, account_id) {\n  var cfg = graph_configs[graph_type];\n\n  var chart = _echartsEn[\"default\"].init(document.querySelector(target));\n\n  chart.setOption(cfg.format(type, id, name, account_id, data));\n  (0, _jquery[\"default\"])(window).on(\"resize\", function () {\n    if (chart != null && chart != undefined) {\n      chart.resize();\n    }\n  });\n}\n\nfunction updateGraph(graph_type, target, data, type, id, name, account_id) {\n  var cfg = graph_configs[graph_type];\n\n  var chart = _echartsEn[\"default\"].init(document.querySelector(target));\n\n  chart.setOption(cfg.format(type, id, name, account_id, data));\n}\n\nfunction disposeGraph(target) {\n  _echartsEn[\"default\"].dispose(document.querySelector(target));\n}\n\n//# sourceURL=webpack:///./CTFd/themes/core/assets/js/graphs.js?");

/***/ }),

/***/ "./CTFd/themes/core/assets/js/pages/stats.js":
/*!***************************************************!*\
  !*** ./CTFd/themes/core/assets/js/pages/stats.js ***!
  \***************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\n__webpack_require__(/*! ./main */ \"./CTFd/themes/core/assets/js/pages/main.js\");\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! ../CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _graphs = __webpack_require__(/*! ../graphs */ \"./CTFd/themes/core/assets/js/graphs.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { \"default\": obj }; }\n\nfunction _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest(); }\n\nfunction _nonIterableRest() { throw new TypeError(\"Invalid attempt to destructure non-iterable instance.\\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.\"); }\n\nfunction _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === \"string\") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === \"Object\" && o.constructor) n = o.constructor.name; if (n === \"Map\" || n === \"Set\") return Array.from(o); if (n === \"Arguments\" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }\n\nfunction _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }\n\nfunction _iterableToArrayLimit(arr, i) { if (typeof Symbol === \"undefined\" || !(Symbol.iterator in Object(arr))) return; var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i[\"return\"] != null) _i[\"return\"](); } finally { if (_d) throw _e; } } return _arr; }\n\nfunction _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }\n\nvar api_funcs = {\n  team: [function (x) {\n    return _CTFd[\"default\"].api.get_team_solves({\n      teamId: x\n    });\n  }, function (x) {\n    return _CTFd[\"default\"].api.get_team_fails({\n      teamId: x\n    });\n  }, function (x) {\n    return _CTFd[\"default\"].api.get_team_awards({\n      teamId: x\n    });\n  }],\n  user: [function (x) {\n    return _CTFd[\"default\"].api.get_user_solves({\n      userId: x\n    });\n  }, function (x) {\n    return _CTFd[\"default\"].api.get_user_fails({\n      userId: x\n    });\n  }, function (x) {\n    return _CTFd[\"default\"].api.get_user_awards({\n      userId: x\n    });\n  }]\n};\n\nvar createGraphs = function createGraphs(type, id, name, account_id) {\n  var _api_funcs$type = _slicedToArray(api_funcs[type], 3),\n      solves_func = _api_funcs$type[0],\n      fails_func = _api_funcs$type[1],\n      awards_func = _api_funcs$type[2];\n\n  Promise.all([solves_func(account_id), fails_func(account_id), awards_func(account_id)]).then(function (responses) {\n    (0, _graphs.createGraph)(\"score_graph\", \"#score-graph\", responses, type, id, name, account_id);\n    (0, _graphs.createGraph)(\"category_breakdown\", \"#categories-pie-graph\", responses, type, id, name, account_id);\n    (0, _graphs.createGraph)(\"solve_percentages\", \"#keys-pie-graph\", responses, type, id, name, account_id);\n  });\n};\n\nvar updateGraphs = function updateGraphs(type, id, name, account_id) {\n  var _api_funcs$type2 = _slicedToArray(api_funcs[type], 3),\n      solves_func = _api_funcs$type2[0],\n      fails_func = _api_funcs$type2[1],\n      awards_func = _api_funcs$type2[2];\n\n  Promise.all([solves_func(account_id), fails_func(account_id), awards_func(account_id)]).then(function (responses) {\n    (0, _graphs.updateGraph)(\"score_graph\", \"#score-graph\", responses, type, id, name, account_id);\n    (0, _graphs.updateGraph)(\"category_breakdown\", \"#categories-pie-graph\", responses, type, id, name, account_id);\n    (0, _graphs.updateGraph)(\"solve_percentages\", \"#keys-pie-graph\", responses, type, id, name, account_id);\n  });\n};\n\n(0, _jquery[\"default\"])(function () {\n  var type, id, name, account_id;\n  var _window$stats_data = window.stats_data;\n  type = _window$stats_data.type;\n  id = _window$stats_data.id;\n  name = _window$stats_data.name;\n  account_id = _window$stats_data.account_id;\n  createGraphs(type, id, name, account_id);\n  setInterval(function () {\n    updateGraphs(type, id, name, account_id);\n  }, 300000);\n});\n\n//# sourceURL=webpack:///./CTFd/themes/core/assets/js/pages/stats.js?");

/***/ })

/******/ });