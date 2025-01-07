import CTFd from "@ctfdio/ctfd-js";
import { buildIcon } from 'iconify-icon';

import dayjs from "dayjs";
import advancedFormat from "dayjs/plugin/advancedFormat";

import MainMenuInit from "./mainMenu";
import BackButtonInit from "./backButton";
import IconWallCanvasInit from "./backgroundCanvas";
import TabPageInit from "./tabs";
import CountdownInit from "./countdown";
import events from "./events";

import times from "./theme/times";
import 'large-small-dynamic-viewport-units-polyfill';
// import highlight from "./theme/highlight";

dayjs.extend(advancedFormat);
CTFd.init(window.init);

(() => {
    MainMenuInit();
    BackButtonInit();
    IconWallCanvasInit();
    TabPageInit();
    CountdownInit();
    times();
    //   highlight();
    
    events(window.init.urlRoot);

})();

export default CTFd;
