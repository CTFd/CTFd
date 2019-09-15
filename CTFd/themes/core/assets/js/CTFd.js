import fetch from "./fetch";
import config from "./config";
import { API } from "./api";
import "./patch";
import MarkdownIt from "markdown-it";
import $ from "jquery";

const api = new API("/");
const user = {};
const _internal = {};
const lib = {
  $,
  MarkdownIt
};

let initialized = false;
const init = data => {
  if (initialized) {
    return;
  }
  initialized = true;

  config.urlRoot = data.urlRoot || config.urlRoot;
  config.csrfNonce = data.csrfNonce || config.csrfNonce;
  config.userMode = data.userMode || config.userMode;
  api.domain = config.urlRoot + "/api/v1";
  user.id = data.userId;
};
const plugin = {
  run: f => {
    f(CTFd);
  }
};

const CTFd = {
  init,
  config,
  fetch,
  user,
  api,
  lib,
  _internal,
  plugin
};

export default CTFd;
