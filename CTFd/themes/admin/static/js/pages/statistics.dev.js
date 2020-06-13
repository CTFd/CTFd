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
/******/ 	deferredModules.push(["./CTFd/themes/admin/assets/js/pages/statistics.js","helpers","echarts","vendor","default~pages/challenge~pages/challenges~pages/configs~pages/editor~pages/main~pages/notifications~p~d5a3cc0a"]);
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
eval("\n\n__webpack_require__(/*! ./main */ \"./CTFd/themes/admin/assets/js/pages/main.js\");\n\nvar _utils = __webpack_require__(/*! core/utils */ \"./CTFd/themes/core/assets/js/utils.js\");\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! core/CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _echartsEn = _interopRequireDefault(__webpack_require__(/*! echarts/dist/echarts-en.common */ \"./node_modules/echarts/dist/echarts-en.common.js\"));\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nvar graph_configs = {\n  \"#solves-graph\": {\n    data: function data() {\n      return _CTFd.default.api.get_challenge_solve_statistics();\n    },\n    format: function format(response) {\n      var data = response.data;\n      var chals = [];\n      var counts = [];\n      var solves = {};\n\n      for (var c = 0; c < data.length; c++) {\n        solves[data[c][\"id\"]] = {\n          name: data[c][\"name\"],\n          solves: data[c][\"solves\"]\n        };\n      }\n\n      var solves_order = Object.keys(solves).sort(function (a, b) {\n        return solves[b].solves - solves[a].solves;\n      });\n\n      _jquery.default.each(solves_order, function (key, value) {\n        chals.push(solves[value].name);\n        counts.push(solves[value].solves);\n      });\n\n      var option = {\n        title: {\n          left: \"center\",\n          text: \"Solve Counts\"\n        },\n        tooltip: {\n          trigger: \"item\"\n        },\n        toolbox: {\n          show: true,\n          feature: {\n            mark: {\n              show: true\n            },\n            dataView: {\n              show: true,\n              readOnly: false\n            },\n            magicType: {\n              show: true,\n              type: [\"line\", \"bar\"]\n            },\n            restore: {\n              show: true\n            },\n            saveAsImage: {\n              show: true\n            }\n          }\n        },\n        xAxis: {\n          name: \"Solve Count\",\n          nameLocation: \"middle\",\n          type: \"value\"\n        },\n        yAxis: {\n          name: \"Challenge Name\",\n          nameLocation: \"middle\",\n          nameGap: 60,\n          type: \"category\",\n          data: chals,\n          axisLabel: {\n            interval: 0,\n            rotate: 0 //If the label names are too long you can manage this by rotating the label.\n\n          }\n        },\n        dataZoom: [{\n          id: \"dataZoomY\",\n          type: \"slider\",\n          yAxisIndex: [0],\n          filterMode: \"empty\"\n        }],\n        series: [{\n          itemStyle: {\n            normal: {\n              color: \"#1f76b4\"\n            }\n          },\n          data: counts,\n          type: \"bar\"\n        }]\n      };\n      return option;\n    }\n  },\n  \"#keys-pie-graph\": {\n    data: function data() {\n      return _CTFd.default.api.get_submission_property_counts({\n        column: \"type\"\n      });\n    },\n    format: function format(response) {\n      var data = response.data;\n      var solves = data[\"correct\"];\n      var fails = data[\"incorrect\"];\n      var option = {\n        title: {\n          left: \"center\",\n          text: \"Submission Percentages\"\n        },\n        tooltip: {\n          trigger: \"item\"\n        },\n        toolbox: {\n          show: true,\n          feature: {\n            dataView: {\n              show: true,\n              readOnly: false\n            },\n            saveAsImage: {}\n          }\n        },\n        legend: {\n          orient: \"horizontal\",\n          bottom: 0,\n          data: [\"Fails\", \"Solves\"]\n        },\n        series: [{\n          name: \"Submission Percentages\",\n          type: \"pie\",\n          radius: [\"30%\", \"50%\"],\n          avoidLabelOverlap: false,\n          label: {\n            show: false,\n            position: \"center\"\n          },\n          itemStyle: {\n            normal: {\n              label: {\n                show: true,\n                formatter: function formatter(data) {\n                  return \"\".concat(data.name, \" - \").concat(data.value, \" (\").concat(data.percent, \"%)\");\n                }\n              },\n              labelLine: {\n                show: true\n              }\n            },\n            emphasis: {\n              label: {\n                show: true,\n                position: \"center\",\n                textStyle: {\n                  fontSize: \"14\",\n                  fontWeight: \"normal\"\n                }\n              }\n            }\n          },\n          emphasis: {\n            label: {\n              show: true,\n              fontSize: \"30\",\n              fontWeight: \"bold\"\n            }\n          },\n          labelLine: {\n            show: false\n          },\n          data: [{\n            value: fails,\n            name: \"Fails\",\n            itemStyle: {\n              color: \"rgb(207, 38, 0)\"\n            }\n          }, {\n            value: solves,\n            name: \"Solves\",\n            itemStyle: {\n              color: \"rgb(0, 209, 64)\"\n            }\n          }]\n        }]\n      };\n      return option;\n    }\n  },\n  \"#categories-pie-graph\": {\n    data: function data() {\n      return _CTFd.default.api.get_challenge_property_counts({\n        column: \"category\"\n      });\n    },\n    format: function format(response) {\n      var data = response.data;\n      var categories = [];\n      var count = [];\n\n      for (var category in data) {\n        if (data.hasOwnProperty(category)) {\n          categories.push(category);\n          count.push(data[category]);\n        }\n      }\n\n      for (var i = 0; i < data.length; i++) {\n        categories.push(data[i].category);\n        count.push(data[i].count);\n      }\n\n      var option = {\n        title: {\n          left: \"center\",\n          text: \"Category Breakdown\"\n        },\n        tooltip: {\n          trigger: \"item\"\n        },\n        toolbox: {\n          show: true,\n          feature: {\n            dataView: {\n              show: true,\n              readOnly: false\n            },\n            saveAsImage: {}\n          }\n        },\n        legend: {\n          orient: \"horizontal\",\n          bottom: 0,\n          data: []\n        },\n        series: [{\n          name: \"Category Breakdown\",\n          type: \"pie\",\n          radius: [\"30%\", \"50%\"],\n          avoidLabelOverlap: false,\n          label: {\n            show: false,\n            position: \"center\"\n          },\n          itemStyle: {\n            normal: {\n              label: {\n                show: true,\n                formatter: function formatter(data) {\n                  return \"\".concat(data.name, \" - \").concat(data.value, \" (\").concat(data.percent, \"%)\");\n                }\n              },\n              labelLine: {\n                show: true\n              }\n            },\n            emphasis: {\n              label: {\n                show: true,\n                position: \"center\",\n                textStyle: {\n                  fontSize: \"14\",\n                  fontWeight: \"normal\"\n                }\n              }\n            }\n          },\n          emphasis: {\n            label: {\n              show: true,\n              fontSize: \"30\",\n              fontWeight: \"bold\"\n            }\n          },\n          labelLine: {\n            show: false\n          },\n          data: []\n        }]\n      };\n      categories.forEach(function (category, index) {\n        option.legend.data.push(category);\n        option.series[0].data.push({\n          value: count[index],\n          name: category,\n          itemStyle: {\n            color: (0, _utils.colorHash)(category)\n          }\n        });\n      });\n      return option;\n    }\n  },\n  \"#solve-percentages-graph\": {\n    layout: function layout(annotations) {\n      return {\n        title: \"Solve Percentages per Challenge\",\n        xaxis: {\n          title: \"Challenge Name\"\n        },\n        yaxis: {\n          title: \"Percentage of {0} (%)\".format(_CTFd.default.config.userMode.charAt(0).toUpperCase() + _CTFd.default.config.userMode.slice(1)),\n          range: [0, 100]\n        },\n        annotations: annotations\n      };\n    },\n    data: function data() {\n      return _CTFd.default.api.get_challenge_solve_percentages();\n    },\n    format: function format(response) {\n      var data = response.data;\n      var names = [];\n      var percents = [];\n      var annotations = [];\n\n      for (var key in data) {\n        names.push(data[key].name);\n        percents.push(data[key].percentage * 100);\n        var result = {\n          x: data[key].name,\n          y: data[key].percentage * 100,\n          text: Math.round(data[key].percentage * 100) + \"%\",\n          xanchor: \"center\",\n          yanchor: \"bottom\",\n          showarrow: false\n        };\n        annotations.push(result);\n      }\n\n      var option = {\n        title: {\n          left: \"center\",\n          text: \"Solve Percentages per Challenge\"\n        },\n        tooltip: {\n          trigger: \"item\",\n          formatter: function formatter(data) {\n            return \"\".concat(data.name, \" - \").concat((Math.round(data.value * 10) / 10).toFixed(1), \"%\");\n          }\n        },\n        toolbox: {\n          show: true,\n          feature: {\n            mark: {\n              show: true\n            },\n            dataView: {\n              show: true,\n              readOnly: false\n            },\n            magicType: {\n              show: true,\n              type: [\"line\", \"bar\"]\n            },\n            restore: {\n              show: true\n            },\n            saveAsImage: {\n              show: true\n            }\n          }\n        },\n        xAxis: {\n          name: \"Challenge Name\",\n          nameGap: 40,\n          nameLocation: \"middle\",\n          type: \"category\",\n          data: names,\n          axisLabel: {\n            interval: 0,\n            rotate: 50\n          }\n        },\n        yAxis: {\n          name: \"Percentage of {0} (%)\".format(_CTFd.default.config.userMode.charAt(0).toUpperCase() + _CTFd.default.config.userMode.slice(1)),\n          nameGap: 50,\n          nameLocation: \"middle\",\n          type: \"value\",\n          min: 0,\n          max: 100\n        },\n        series: [{\n          itemStyle: {\n            normal: {\n              color: \"#1f76b4\"\n            }\n          },\n          data: percents,\n          type: \"bar\"\n        }]\n      };\n      return option;\n    }\n  },\n  \"#score-distribution-graph\": {\n    layout: function layout(annotations) {\n      return {\n        title: \"Score Distribution\",\n        xaxis: {\n          title: \"Score Bracket\",\n          showticklabels: true,\n          type: \"category\"\n        },\n        yaxis: {\n          title: \"Number of {0}\".format(_CTFd.default.config.userMode.charAt(0).toUpperCase() + _CTFd.default.config.userMode.slice(1))\n        },\n        annotations: annotations\n      };\n    },\n    data: function data() {\n      return _CTFd.default.fetch(\"/api/v1/statistics/scores/distribution\").then(function (response) {\n        return response.json();\n      });\n    },\n    format: function format(response) {\n      var data = response.data.brackets;\n      var keys = [];\n      var brackets = [];\n      var sizes = [];\n\n      for (var key in data) {\n        keys.push(parseInt(key));\n      }\n\n      keys.sort(function (a, b) {\n        return a - b;\n      });\n      var start = \"<0\";\n      keys.map(function (key) {\n        brackets.push(\"{0} - {1}\".format(start, key));\n        sizes.push(data[key]);\n        start = key;\n      });\n      var option = {\n        title: {\n          left: \"center\",\n          text: \"Score Distribution\"\n        },\n        tooltip: {\n          trigger: \"item\"\n        },\n        toolbox: {\n          show: true,\n          feature: {\n            mark: {\n              show: true\n            },\n            dataView: {\n              show: true,\n              readOnly: false\n            },\n            magicType: {\n              show: true,\n              type: [\"line\", \"bar\"]\n            },\n            restore: {\n              show: true\n            },\n            saveAsImage: {\n              show: true\n            }\n          }\n        },\n        xAxis: {\n          name: \"Score Bracket\",\n          nameGap: 40,\n          nameLocation: \"middle\",\n          type: \"category\",\n          data: brackets\n        },\n        yAxis: {\n          name: \"Number of {0}\".format(_CTFd.default.config.userMode.charAt(0).toUpperCase() + _CTFd.default.config.userMode.slice(1)),\n          nameGap: 50,\n          nameLocation: \"middle\",\n          type: \"value\"\n        },\n        series: [{\n          itemStyle: {\n            normal: {\n              color: \"#1f76b4\"\n            }\n          },\n          data: sizes,\n          type: \"bar\"\n        }]\n      };\n      return option;\n    }\n  }\n};\n\nvar createGraphs = function createGraphs() {\n  var _loop = function _loop(key) {\n    var cfg = graph_configs[key];\n    var $elem = (0, _jquery.default)(key);\n    $elem.empty();\n\n    var chart = _echartsEn.default.init(document.querySelector(key));\n\n    cfg.data().then(cfg.format).then(function (option) {\n      chart.setOption(option);\n      (0, _jquery.default)(window).on(\"resize\", function () {\n        if (chart != null && chart != undefined) {\n          chart.resize();\n        }\n      });\n    });\n  };\n\n  for (var key in graph_configs) {\n    _loop(key);\n  }\n};\n\nfunction updateGraphs() {\n  var _loop2 = function _loop2(key) {\n    var cfg = graph_configs[key];\n\n    var chart = _echartsEn.default.init(document.querySelector(key));\n\n    cfg.data().then(cfg.format).then(function (option) {\n      chart.setOption(option);\n    });\n  };\n\n  for (var key in graph_configs) {\n    _loop2(key);\n  }\n}\n\n(0, _jquery.default)(function () {\n  createGraphs();\n  setInterval(updateGraphs, 300000);\n});\n\n//# sourceURL=webpack:///./CTFd/themes/admin/assets/js/pages/statistics.js?");

/***/ })

/******/ });