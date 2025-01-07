import $ from "jquery";
import events from "../events";
import config from "../config";

$(() => {
  events(config.urlRoot);
});
