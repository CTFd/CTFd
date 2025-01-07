import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import advancedFormat from 'dayjs/plugin/advancedFormat';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import getLyricsContent from './splashData.js';
import { _ } from './utils/i18n.js';

dayjs.extend(duration);
dayjs.extend(advancedFormat);
dayjs.extend(utc);
dayjs.extend(timezone);

import tdcip from '2d-canvas-image-particles/';
import tippy from 'tippy.js';

const canvas = document.getElementById('particlesCanvas');
const titleScreen = document.getElementById('titleScreen');

function initHomeCountdown() {
    const countdown = document.getElementById('homeCountdown');
    const localDate = document.getElementById('homeLocalDate');
    const isoDate = document.getElementById('homeISODate');

    var now = dayjs();
    const timezoneFormat = now.format("z").includes("GMT") ? "[(UTC]Z[)]" : "[(]z[, UTC]Z[)]";
    var start = window.init.start && dayjs.unix(window.init.start);
    var end = window.init.end && dayjs.unix(window.init.end);
    var archived = window.init.archived;
    const dateFormat = _("D MMM YYYY, H:mm");
    if (archived) {
        countdown.innerText = _("The CTF is archived.");
        localDate.innerText = `${start.format(dateFormat)} – ${end.format(`${dateFormat} ${timezoneFormat}`)}`;
        isoDate.innerText = `${start.toISOString()} + ${dayjs.duration(end.diff(start)).toISOString()}`;
        localDate.dateTime = isoDate.innerText;
        isoDate.dateTime = isoDate.innerText;
        return;
    }
    var target = null;
    var prompt = "";
    if (start && now.isBefore(start)) {
        target = start;
        prompt = _("%(time)s until start.");
    }
    else if (end && now.isBefore(end)) {
        target = end;
        prompt = _("%(time)s until end.");
    }
    var display = target || end || start;
    if (display) {
        localDate.innerText = display.format(`${dateFormat} ${timezoneFormat}`);
        isoDate.innerText = display.toISOString();
        localDate.dateTime = isoDate.innerText;
        isoDate.dateTime = isoDate.innerText;
    } else {
        localDate.styles.display = "none";
        isoDate.styles.display = "none";
    }
    // console.log(now, start, end, now.isBefore(start), now.isBefore(end));

    if (target === null) {
        if (start === null) countdown.style.display = "none";
        else if (end === null) countdown.innerText = _("The CTF has started.");
        else countdown.innerText = _("The CTF has ended.");
    } else {
        var countdownInterval = null;
        var countdownIntervalFn = () => {
            var diffVal = target.diff(dayjs());
            if (diffVal > 0) {
                var diff = dayjs.duration(diffVal);
                var diffDay = Math.floor(diff.asDays());
                var diffHours = Math.floor(diff.asHours());
                var diffStr = 
                    diffDay >= 3 ?
                    _("%(days)sd %(rest)s").replace("%(days)s", diffDay).replace("%(rest)s", diff.format(_("HH[h] mm[m] ss[s]"))) :
                    diff.asHours() >= 1 ?
                    _("%(hours)sh %(rest)s").replace("%(hours)s", diffHours).replace("%(rest)s", diff.format(_("mm[m] ss[s]"))) :
                    diff.format(`mm[m] ss[s]`);
                countdown.innerText = prompt.replace("%(time)s", diffStr);
                countdown.dateTime = diff.toISOString();
            } else {
                clearInterval(countdownInterval);
                initHomeCountdown();
            }
        };
        countdownIntervalFn();
        countdownInterval = setInterval(countdownIntervalFn, 1000);
    }
}

function showTitleScreen() {
    document.body.classList.add("titleScreenVisible");
    titleScreen.classList.remove("hidden");
    window.localStorage.setItem("luna_showTitleScreen", "true");

    const options = {
        width: [40, 100],
        height: [20, 50],
        density: 0.1,
        speed: [60, 80],
        cursorMode: null,
        rotationMode: RotationMode.Random,
        velocityAngle: [180 + 40, 180 + 50],
        rotationSpeed: [30, 100],
        tints: [
            new Tint('#F5C0F3', 1),
            new Tint('#C3F5FD', 1),
            new Tint('#FEF79F', 1),
        ],
        addOnClickNb: 0,
    };

    const ps = [
        new ParticleSystem(canvas, PartileAssets.pattern1, options),
        new ParticleSystem(canvas, PartileAssets.pattern2, options),
        new ParticleSystem(canvas, PartileAssets.pattern3, {...options, 
            width: [150, 200],
            height: [75, 100],
            tints: [
                new Tint('#F5C0F3', 0.5),
                new Tint('#C3F5FD', 0.5),
                new Tint('#FEF79F', 0.5),
                new Tint('#F5C0F3', 0.25),
                new Tint('#C3F5FD', 0.25),
                new Tint('#FEF79F', 0.25),
            ],}),
    ];
}

function hideTitleScreen(withAnimation = false) {
    window.localStorage.setItem("luna_showTitleScreen", "false");
    if (withAnimation) {
        if (titleScreen.classList.contains("splash-exit")) return;
        titleScreen.classList.add("splash-exit");
        setTimeout(() => {
            document.body.classList.remove("titleScreenVisible");
            titleScreen.classList.add("hidden");
            titleScreen.classList.remove("splash-exit");
            ParticleSystem.destroyAll();
        }, 2000);
    } else {
        document.body.classList.remove("titleScreenVisible");
        titleScreen.classList.add("hidden");
        ParticleSystem.destroyAll();
    }
}

function initTitleScreen() {
    var shouldShowTitleScreen = window.localStorage.getItem("luna_showTitleScreen");
    if (shouldShowTitleScreen === null) {
        shouldShowTitleScreen = "true";
        window.localStorage.setItem("luna_showTitleScreen", "true");
    }
    if (shouldShowTitleScreen === "true") {
        showTitleScreen();
    } else {
        hideTitleScreen(false);
    }

    titleScreen.addEventListener("click", () => hideTitleScreen(true));
}

(() => {
    initTitleScreen();
    initHomeCountdown();

    const lyricsContent = getLyricsContent();
    tippy(document.querySelectorAll("[data-tippy-lyrics]"), {
        content: lyricsContent,
        theme: "lunaDefault",
        allowHTML: true,
        placement: "bottom-start",
        arrow: false,
    })
})();