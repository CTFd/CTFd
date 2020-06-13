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
/******/ 		"pages/team": 0
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
/******/ 	deferredModules.push(["./CTFd/themes/admin/assets/js/pages/team.js","helpers","echarts","graphs","vendor","default~pages/challenge~pages/challenges~pages/configs~pages/editor~pages/main~pages/notifications~p~d5a3cc0a"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./CTFd/themes/admin/assets/js/pages/team.js":
/*!***************************************************!*\
  !*** ./CTFd/themes/admin/assets/js/pages/team.js ***!
  \***************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\n__webpack_require__(/*! ./main */ \"./CTFd/themes/admin/assets/js/pages/main.js\");\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! core/CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _utils = __webpack_require__(/*! core/utils */ \"./CTFd/themes/core/assets/js/utils.js\");\n\nvar _ezq = __webpack_require__(/*! core/ezq */ \"./CTFd/themes/core/assets/js/ezq.js\");\n\nvar _graphs = __webpack_require__(/*! core/graphs */ \"./CTFd/themes/core/assets/js/graphs.js\");\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nfunction _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }\n\nfunction _nonIterableRest() { throw new TypeError(\"Invalid attempt to destructure non-iterable instance\"); }\n\nfunction _iterableToArrayLimit(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i[\"return\"] != null) _i[\"return\"](); } finally { if (_d) throw _e; } } return _arr; }\n\nfunction _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }\n\nfunction createTeam(event) {\n  event.preventDefault();\n  var params = (0, _jquery.default)(\"#team-info-create-form\").serializeJSON(true);\n\n  _CTFd.default.fetch(\"/api/v1/teams\", {\n    method: \"POST\",\n    credentials: \"same-origin\",\n    headers: {\n      Accept: \"application/json\",\n      \"Content-Type\": \"application/json\"\n    },\n    body: JSON.stringify(params)\n  }).then(function (response) {\n    return response.json();\n  }).then(function (response) {\n    if (response.success) {\n      var team_id = response.data.id;\n      window.location = _CTFd.default.config.urlRoot + \"/admin/teams/\" + team_id;\n    } else {\n      (0, _jquery.default)(\"#team-info-form > #results\").empty();\n      Object.keys(response.errors).forEach(function (key, _index) {\n        (0, _jquery.default)(\"#team-info-form > #results\").append((0, _ezq.ezBadge)({\n          type: \"error\",\n          body: response.errors[key]\n        }));\n        var i = (0, _jquery.default)(\"#team-info-form\").find(\"input[name={0}]\".format(key));\n        var input = (0, _jquery.default)(i);\n        input.addClass(\"input-filled-invalid\");\n        input.removeClass(\"input-filled-valid\");\n      });\n    }\n  });\n}\n\nfunction updateTeam(event) {\n  event.preventDefault();\n  var params = (0, _jquery.default)(\"#team-info-edit-form\").serializeJSON(true);\n\n  _CTFd.default.fetch(\"/api/v1/teams/\" + window.TEAM_ID, {\n    method: \"PATCH\",\n    credentials: \"same-origin\",\n    headers: {\n      Accept: \"application/json\",\n      \"Content-Type\": \"application/json\"\n    },\n    body: JSON.stringify(params)\n  }).then(function (response) {\n    return response.json();\n  }).then(function (response) {\n    if (response.success) {\n      window.location.reload();\n    } else {\n      (0, _jquery.default)(\"#team-info-form > #results\").empty();\n      Object.keys(response.errors).forEach(function (key, _index) {\n        (0, _jquery.default)(\"#team-info-form > #results\").append((0, _ezq.ezBadge)({\n          type: \"error\",\n          body: response.errors[key]\n        }));\n        var i = (0, _jquery.default)(\"#team-info-form\").find(\"input[name={0}]\".format(key));\n        var input = (0, _jquery.default)(i);\n        input.addClass(\"input-filled-invalid\");\n        input.removeClass(\"input-filled-valid\");\n      });\n    }\n  });\n}\n\nfunction deleteSelectedSubmissions(event, target) {\n  var submissions;\n  var type;\n  var title;\n\n  switch (target) {\n    case \"solves\":\n      submissions = (0, _jquery.default)(\"input[data-submission-type=correct]:checked\");\n      type = \"solve\";\n      title = \"Solves\";\n      break;\n\n    case \"fails\":\n      submissions = (0, _jquery.default)(\"input[data-submission-type=incorrect]:checked\");\n      type = \"fail\";\n      title = \"Fails\";\n      break;\n\n    default:\n      break;\n  }\n\n  var submissionIDs = submissions.map(function () {\n    return (0, _jquery.default)(this).data(\"submission-id\");\n  });\n  var target_string = submissionIDs.length === 1 ? type : type + \"s\";\n  (0, _ezq.ezQuery)({\n    title: \"Delete \".concat(title),\n    body: \"Are you sure you want to delete \".concat(submissionIDs.length, \" \").concat(target_string, \"?\"),\n    success: function success() {\n      var reqs = [];\n      var _iteratorNormalCompletion = true;\n      var _didIteratorError = false;\n      var _iteratorError = undefined;\n\n      try {\n        for (var _iterator = submissionIDs[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {\n          var subId = _step.value;\n          reqs.push(_CTFd.default.api.delete_submission({\n            submissionId: subId\n          }));\n        }\n      } catch (err) {\n        _didIteratorError = true;\n        _iteratorError = err;\n      } finally {\n        try {\n          if (!_iteratorNormalCompletion && _iterator.return != null) {\n            _iterator.return();\n          }\n        } finally {\n          if (_didIteratorError) {\n            throw _iteratorError;\n          }\n        }\n      }\n\n      Promise.all(reqs).then(function (_responses) {\n        window.location.reload();\n      });\n    }\n  });\n}\n\nfunction deleteSelectedAwards(_event) {\n  var awardIDs = (0, _jquery.default)(\"input[data-award-id]:checked\").map(function () {\n    return (0, _jquery.default)(this).data(\"award-id\");\n  });\n  var target = awardIDs.length === 1 ? \"award\" : \"awards\";\n  (0, _ezq.ezQuery)({\n    title: \"Delete Awards\",\n    body: \"Are you sure you want to delete \".concat(awardIDs.length, \" \").concat(target, \"?\"),\n    success: function success() {\n      var reqs = [];\n      var _iteratorNormalCompletion2 = true;\n      var _didIteratorError2 = false;\n      var _iteratorError2 = undefined;\n\n      try {\n        for (var _iterator2 = awardIDs[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {\n          var awardID = _step2.value;\n\n          var req = _CTFd.default.fetch(\"/api/v1/awards/\" + awardID, {\n            method: \"DELETE\",\n            credentials: \"same-origin\",\n            headers: {\n              Accept: \"application/json\",\n              \"Content-Type\": \"application/json\"\n            }\n          });\n\n          reqs.push(req);\n        }\n      } catch (err) {\n        _didIteratorError2 = true;\n        _iteratorError2 = err;\n      } finally {\n        try {\n          if (!_iteratorNormalCompletion2 && _iterator2.return != null) {\n            _iterator2.return();\n          }\n        } finally {\n          if (_didIteratorError2) {\n            throw _iteratorError2;\n          }\n        }\n      }\n\n      Promise.all(reqs).then(function (_responses) {\n        window.location.reload();\n      });\n    }\n  });\n}\n\nfunction solveSelectedMissingChallenges(event) {\n  event.preventDefault();\n  var challengeIDs = (0, _jquery.default)(\"input[data-missing-challenge-id]:checked\").map(function () {\n    return (0, _jquery.default)(this).data(\"missing-challenge-id\");\n  });\n  var target = challengeIDs.length === 1 ? \"challenge\" : \"challenges\";\n  (0, _ezq.ezQuery)({\n    title: \"Mark Correct\",\n    body: \"Are you sure you want to mark \".concat(challengeIDs.length, \" \").concat(target, \" correct for \").concat((0, _utils.htmlEntities)(window.TEAM_NAME), \"?\"),\n    success: function success() {\n      (0, _ezq.ezAlert)({\n        title: \"User Attribution\",\n        body: \"\\n        Which user on \".concat((0, _utils.htmlEntities)(window.TEAM_NAME), \" solved these challenges?\\n        <div class=\\\"pb-3\\\" id=\\\"query-team-member-solve\\\">\\n        \").concat((0, _jquery.default)(\"#team-member-select\").html(), \"\\n        </div>\\n        \"),\n        button: \"Mark Correct\",\n        success: function success() {\n          var USER_ID = (0, _jquery.default)(\"#query-team-member-solve > select\").val();\n          var reqs = [];\n          var _iteratorNormalCompletion3 = true;\n          var _didIteratorError3 = false;\n          var _iteratorError3 = undefined;\n\n          try {\n            for (var _iterator3 = challengeIDs[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {\n              var challengeID = _step3.value;\n              var params = {\n                provided: \"MARKED AS SOLVED BY ADMIN\",\n                user_id: USER_ID,\n                team_id: window.TEAM_ID,\n                challenge_id: challengeID,\n                type: \"correct\"\n              };\n\n              var req = _CTFd.default.fetch(\"/api/v1/submissions\", {\n                method: \"POST\",\n                credentials: \"same-origin\",\n                headers: {\n                  Accept: \"application/json\",\n                  \"Content-Type\": \"application/json\"\n                },\n                body: JSON.stringify(params)\n              });\n\n              reqs.push(req);\n            }\n          } catch (err) {\n            _didIteratorError3 = true;\n            _iteratorError3 = err;\n          } finally {\n            try {\n              if (!_iteratorNormalCompletion3 && _iterator3.return != null) {\n                _iterator3.return();\n              }\n            } finally {\n              if (_didIteratorError3) {\n                throw _iteratorError3;\n              }\n            }\n          }\n\n          Promise.all(reqs).then(function (_responses) {\n            window.location.reload();\n          });\n        }\n      });\n    }\n  });\n}\n\nvar api_funcs = {\n  team: [function (x) {\n    return _CTFd.default.api.get_team_solves({\n      teamId: x\n    });\n  }, function (x) {\n    return _CTFd.default.api.get_team_fails({\n      teamId: x\n    });\n  }, function (x) {\n    return _CTFd.default.api.get_team_awards({\n      teamId: x\n    });\n  }],\n  user: [function (x) {\n    return _CTFd.default.api.get_user_solves({\n      userId: x\n    });\n  }, function (x) {\n    return _CTFd.default.api.get_user_fails({\n      userId: x\n    });\n  }, function (x) {\n    return _CTFd.default.api.get_user_awards({\n      userId: x\n    });\n  }]\n};\n\nvar createGraphs = function createGraphs(type, id, name, account_id) {\n  var _api_funcs$type = _slicedToArray(api_funcs[type], 3),\n      solves_func = _api_funcs$type[0],\n      fails_func = _api_funcs$type[1],\n      awards_func = _api_funcs$type[2];\n\n  Promise.all([solves_func(account_id), fails_func(account_id), awards_func(account_id)]).then(function (responses) {\n    (0, _graphs.createGraph)(\"score_graph\", \"#score-graph\", responses, type, id, name, account_id);\n    (0, _graphs.createGraph)(\"category_breakdown\", \"#categories-pie-graph\", responses, type, id, name, account_id);\n    (0, _graphs.createGraph)(\"solve_percentages\", \"#keys-pie-graph\", responses, type, id, name, account_id);\n  });\n};\n\nvar updateGraphs = function updateGraphs(type, id, name, account_id) {\n  var _api_funcs$type2 = _slicedToArray(api_funcs[type], 3),\n      solves_func = _api_funcs$type2[0],\n      fails_func = _api_funcs$type2[1],\n      awards_func = _api_funcs$type2[2];\n\n  Promise.all([solves_func(account_id), fails_func(account_id), awards_func(account_id)]).then(function (responses) {\n    (0, _graphs.updateGraph)(\"score_graph\", \"#score-graph\", responses, type, id, name, account_id);\n    (0, _graphs.updateGraph)(\"category_breakdown\", \"#categories-pie-graph\", responses, type, id, name, account_id);\n    (0, _graphs.updateGraph)(\"solve_percentages\", \"#keys-pie-graph\", responses, type, id, name, account_id);\n  });\n};\n\n(0, _jquery.default)(function () {\n  (0, _jquery.default)(\"#team-captain-form\").submit(function (e) {\n    e.preventDefault();\n    var params = (0, _jquery.default)(\"#team-captain-form\").serializeJSON(true);\n\n    _CTFd.default.fetch(\"/api/v1/teams/\" + window.TEAM_ID, {\n      method: \"PATCH\",\n      credentials: \"same-origin\",\n      headers: {\n        Accept: \"application/json\",\n        \"Content-Type\": \"application/json\"\n      },\n      body: JSON.stringify(params)\n    }).then(function (response) {\n      return response.json();\n    }).then(function (response) {\n      if (response.success) {\n        window.location.reload();\n      } else {\n        (0, _jquery.default)(\"#team-captain-form > #results\").empty();\n        Object.keys(response.errors).forEach(function (key, _index) {\n          (0, _jquery.default)(\"#team-captain-form > #results\").append((0, _ezq.ezBadge)({\n            type: \"error\",\n            body: response.errors[key]\n          }));\n          var i = (0, _jquery.default)(\"#team-captain-form\").find(\"select[name={0}]\".format(key));\n          var input = (0, _jquery.default)(i);\n          input.addClass(\"input-filled-invalid\");\n          input.removeClass(\"input-filled-valid\");\n        });\n      }\n    });\n  });\n  (0, _jquery.default)(\".edit-team\").click(function (_e) {\n    (0, _jquery.default)(\"#team-info-edit-modal\").modal(\"toggle\");\n  });\n  (0, _jquery.default)(\".edit-captain\").click(function (_e) {\n    (0, _jquery.default)(\"#team-captain-modal\").modal(\"toggle\");\n  });\n  (0, _jquery.default)(\".award-team\").click(function (_e) {\n    (0, _jquery.default)(\"#team-award-modal\").modal(\"toggle\");\n  });\n  (0, _jquery.default)(\".addresses-team\").click(function (_event) {\n    (0, _jquery.default)(\"#team-addresses-modal\").modal(\"toggle\");\n  });\n  (0, _jquery.default)(\"#user-award-form\").submit(function (e) {\n    e.preventDefault();\n    var params = (0, _jquery.default)(\"#user-award-form\").serializeJSON(true);\n    params[\"user_id\"] = (0, _jquery.default)(\"#award-member-input\").val();\n    params[\"team_id\"] = window.TEAM_ID;\n    (0, _jquery.default)(\"#user-award-form > #results\").empty();\n\n    if (!params[\"user_id\"]) {\n      (0, _jquery.default)(\"#user-award-form > #results\").append((0, _ezq.ezBadge)({\n        type: \"error\",\n        body: \"Please select a team member\"\n      }));\n      return;\n    }\n\n    params[\"user_id\"] = parseInt(params[\"user_id\"]);\n\n    _CTFd.default.fetch(\"/api/v1/awards\", {\n      method: \"POST\",\n      credentials: \"same-origin\",\n      headers: {\n        Accept: \"application/json\",\n        \"Content-Type\": \"application/json\"\n      },\n      body: JSON.stringify(params)\n    }).then(function (response) {\n      return response.json();\n    }).then(function (response) {\n      if (response.success) {\n        window.location.reload();\n      } else {\n        (0, _jquery.default)(\"#user-award-form > #results\").empty();\n        Object.keys(response.errors).forEach(function (key, _index) {\n          (0, _jquery.default)(\"#user-award-form > #results\").append((0, _ezq.ezBadge)({\n            type: \"error\",\n            body: response.errors[key]\n          }));\n          var i = (0, _jquery.default)(\"#user-award-form\").find(\"input[name={0}]\".format(key));\n          var input = (0, _jquery.default)(i);\n          input.addClass(\"input-filled-invalid\");\n          input.removeClass(\"input-filled-valid\");\n        });\n      }\n    });\n  });\n  (0, _jquery.default)(\".delete-member\").click(function (e) {\n    e.preventDefault();\n    var member_id = (0, _jquery.default)(this).attr(\"member-id\");\n    var member_name = (0, _jquery.default)(this).attr(\"member-name\");\n    var params = {\n      user_id: member_id\n    };\n    var row = (0, _jquery.default)(this).parent().parent();\n    (0, _ezq.ezQuery)({\n      title: \"Remove Member\",\n      body: \"Are you sure you want to remove {0} from {1}? <br><br><strong>All of their challenges solves, attempts, awards, and unlocked hints will also be deleted!</strong>\".format(\"<strong>\" + (0, _utils.htmlEntities)(member_name) + \"</strong>\", \"<strong>\" + (0, _utils.htmlEntities)(window.TEAM_NAME) + \"</strong>\"),\n      success: function success() {\n        _CTFd.default.fetch(\"/api/v1/teams/\" + window.TEAM_ID + \"/members\", {\n          method: \"DELETE\",\n          body: JSON.stringify(params)\n        }).then(function (response) {\n          return response.json();\n        }).then(function (response) {\n          if (response.success) {\n            row.remove();\n          }\n        });\n      }\n    });\n  });\n  (0, _jquery.default)(\".delete-team\").click(function (_e) {\n    (0, _ezq.ezQuery)({\n      title: \"Delete Team\",\n      body: \"Are you sure you want to delete {0}\".format(\"<strong>\" + (0, _utils.htmlEntities)(window.TEAM_NAME) + \"</strong>\"),\n      success: function success() {\n        _CTFd.default.fetch(\"/api/v1/teams/\" + window.TEAM_ID, {\n          method: \"DELETE\"\n        }).then(function (response) {\n          return response.json();\n        }).then(function (response) {\n          if (response.success) {\n            window.location = _CTFd.default.config.urlRoot + \"/admin/teams\";\n          }\n        });\n      }\n    });\n  });\n  (0, _jquery.default)(\"#solves-delete-button\").click(function (e) {\n    deleteSelectedSubmissions(e, \"solves\");\n  });\n  (0, _jquery.default)(\"#fails-delete-button\").click(function (e) {\n    deleteSelectedSubmissions(e, \"fails\");\n  });\n  (0, _jquery.default)(\"#awards-delete-button\").click(function (e) {\n    deleteSelectedAwards(e);\n  });\n  (0, _jquery.default)(\"#missing-solve-button\").click(function (e) {\n    solveSelectedMissingChallenges(e);\n  });\n  (0, _jquery.default)(\"#team-info-create-form\").submit(createTeam);\n  (0, _jquery.default)(\"#team-info-edit-form\").submit(updateTeam);\n  var type, id, name, account_id;\n  var _window$stats_data = window.stats_data;\n  type = _window$stats_data.type;\n  id = _window$stats_data.id;\n  name = _window$stats_data.name;\n  account_id = _window$stats_data.account_id;\n  createGraphs(type, id, name, account_id);\n  setInterval(function () {\n    updateGraphs(type, id, name, account_id);\n  }, 300000);\n});\n\n//# sourceURL=webpack:///./CTFd/themes/admin/assets/js/pages/team.js?");

/***/ })

/******/ });