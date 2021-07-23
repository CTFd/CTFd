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
/******/ 		"pages/scoreboard": 0
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
/******/ 	deferredModules.push(["./CTFd/themes/core/assets/js/pages/scoreboard.js","helpers","echarts","vendor","default~pages/challenges~pages/main~pages/notifications~pages/scoreboard~pages/settings~pages/setup~~6822bf1f"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./CTFd/themes/core/assets/js/pages/scoreboard.js":
/*!********************************************************!*\
  !*** ./CTFd/themes/core/assets/js/pages/scoreboard.js ***!
  \********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\n__webpack_require__(/*! ./main */ \"./CTFd/themes/core/assets/js/pages/main.js\");\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! ../CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _echartsEn = _interopRequireDefault(__webpack_require__(/*! echarts/dist/echarts-en.common */ \"./node_modules/echarts/dist/echarts-en.common.js\"));\n\nvar _dayjs = _interopRequireDefault(__webpack_require__(/*! dayjs */ \"./node_modules/dayjs/dayjs.min.js\"));\n\nvar _utils = __webpack_require__(/*! ../utils */ \"./CTFd/themes/core/assets/js/utils.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { \"default\": obj }; }\n\nvar graph = (0, _jquery[\"default\"])(\"#score-graph\");\nvar table = (0, _jquery[\"default\"])(\"#scoreboard tbody\");\n\nvar updateScores = function updateScores() {\n  _CTFd[\"default\"].api.get_scoreboard_list().then(function (response) {\n    var teams = response.data;\n    table.empty();\n\n    for (var i = 0; i < teams.length; i++) {\n      var row = [\"<tr>\", '<th scope=\"row\" class=\"text-center\">', i + 1, \"</th>\", '<td><a href=\"{0}/teams/{1}\">'.format(_CTFd[\"default\"].config.urlRoot, teams[i].account_id), (0, _utils.htmlEntities)(teams[i].name), \"</a></td>\", \"<td>\", teams[i].score, \"</td>\", \"</tr>\"].join(\"\");\n      table.append(row);\n    }\n  });\n};\n\nvar buildGraphData = function buildGraphData() {\n  return _CTFd[\"default\"].api.get_scoreboard_detail({\n    count: 10\n  }).then(function (response) {\n    var places = response.data;\n    var teams = Object.keys(places);\n\n    if (teams.length === 0) {\n      return false;\n    }\n\n    var option = {\n      title: {\n        left: \"center\",\n        text: \"Top 10 \" + (_CTFd[\"default\"].config.userMode === \"teams\" ? \"Teams\" : \"Users\")\n      },\n      tooltip: {\n        trigger: \"axis\",\n        axisPointer: {\n          type: \"cross\"\n        }\n      },\n      legend: {\n        type: \"scroll\",\n        orient: \"horizontal\",\n        align: \"left\",\n        bottom: 35,\n        data: []\n      },\n      toolbox: {\n        feature: {\n          dataZoom: {\n            yAxisIndex: \"none\"\n          },\n          saveAsImage: {}\n        }\n      },\n      grid: {\n        containLabel: true\n      },\n      xAxis: [{\n        type: \"time\",\n        boundaryGap: false,\n        data: []\n      }],\n      yAxis: [{\n        type: \"value\"\n      }],\n      dataZoom: [{\n        id: \"dataZoomX\",\n        type: \"slider\",\n        xAxisIndex: [0],\n        filterMode: \"filter\",\n        height: 20,\n        top: 35,\n        fillerColor: \"rgba(233, 236, 241, 0.4)\"\n      }],\n      series: []\n    };\n\n    var _loop = function _loop(i) {\n      var team_score = [];\n      var times = [];\n\n      for (var j = 0; j < places[teams[i]][\"solves\"].length; j++) {\n        team_score.push(places[teams[i]][\"solves\"][j].value);\n        var date = (0, _dayjs[\"default\"])(places[teams[i]][\"solves\"][j].date);\n        times.push(date.toDate());\n      }\n\n      var total_scores = (0, _utils.cumulativeSum)(team_score);\n      scores = times.map(function (e, i) {\n        return [e, total_scores[i]];\n      });\n      option.legend.data.push(places[teams[i]][\"name\"]);\n      var data = {\n        name: places[teams[i]][\"name\"],\n        type: \"line\",\n        label: {\n          normal: {\n            position: \"top\"\n          }\n        },\n        itemStyle: {\n          normal: {\n            color: (0, _utils.colorHash)(places[teams[i]][\"name\"] + places[teams[i]][\"id\"])\n          }\n        },\n        data: scores\n      };\n      option.series.push(data);\n    };\n\n    for (var i = 0; i < teams.length; i++) {\n      var scores;\n\n      _loop(i);\n    }\n\n    return option;\n  });\n};\n\nvar createGraph = function createGraph() {\n  buildGraphData().then(function (option) {\n    if (option === false) {\n      // Replace spinner\n      graph.html('<h3 class=\"opacity-50 text-center w-100 justify-content-center align-self-center\">No solves yet</h3>');\n      return;\n    }\n\n    graph.empty(); // Remove spinners\n\n    var chart = _echartsEn[\"default\"].init(document.querySelector(\"#score-graph\"));\n\n    chart.setOption(option);\n    (0, _jquery[\"default\"])(window).on(\"resize\", function () {\n      if (chart != null && chart != undefined) {\n        chart.resize();\n      }\n    });\n  });\n};\n\nvar updateGraph = function updateGraph() {\n  buildGraphData().then(function (option) {\n    var chart = _echartsEn[\"default\"].init(document.querySelector(\"#score-graph\"));\n\n    chart.setOption(option);\n  });\n};\n\nfunction update() {\n  updateScores();\n  updateGraph();\n}\n\n(0, _jquery[\"default\"])(function () {\n  setInterval(update, 300000); // Update scores every 5 minutes\n\n  createGraph();\n});\nwindow.updateScoreboard = update;\n\n//# sourceURL=webpack:///./CTFd/themes/core/assets/js/pages/scoreboard.js?");

/***/ })

/******/ });