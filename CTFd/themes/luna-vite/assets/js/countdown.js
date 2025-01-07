import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import relativeTime from 'dayjs/plugin/relativeTime';
dayjs.extend(duration);
dayjs.extend(relativeTime);

export default function CountdownInit() {
    const countdown = document.getElementById('statusCountdown');
    if (countdown) {
        var now = dayjs();
        var start = window.init.start && dayjs.unix(window.init.start);
        var end = window.init.end && dayjs.unix(window.init.end);
        var target = null;
        if (start && now.isBefore(start)) target = start;
        else if (end && now.isBefore(end)) target = end;
        // console.log(now, start, end, now.isBefore(start), now.isBefore(end));

        if (target === null) {
            countdown.style.display = "none";
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
                        `${diffDay}d ${diff.format('HH:mm:ss')}` : 
                        diff.asHours() >= 1 ?
                        `${diffHours}:${diff.format('mm:ss')}` :
                        diff.format('mm:ss');
                    countdown.innerText = diffStr;
                    countdown.dateTime = diff.toISOString();
                } else {
                    clearInterval(countdownInterval);
                    CountdownInit();
                }
            };
            countdownIntervalFn();
            setInterval(countdownIntervalFn, 1000);
        }
    }
}