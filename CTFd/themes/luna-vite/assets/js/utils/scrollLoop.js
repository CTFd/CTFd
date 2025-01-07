import { debounce } from "lodash";

export const itemHeight = 100;

function setScrollOffset(node, val) {
    node.scrollTop += val;
}

const isOverlap = (startA, endA, startB, endB) => (startA <= endB) && (endA >= startB);

export function scrollUpdate() {
    if (performance.now() - window.lastClick < 500) return;

    const listNode = document.getElementById("challengesList");
    const centerNodes = [...document.querySelectorAll("[data-is-center]")];
    var centerProbe = centerNodes;
    var probe = false;
    if (document.querySelectorAll(".challengeItem.selected").length) {
        probe = true;
        centerProbe = [...document.querySelectorAll(".challengeItem.selected")];
    }
    const centerTop = Math.min(...centerNodes.map((v) => v.offsetTop));
    const centerBottom = Math.max(
      ...centerNodes.map((v) => v.offsetTop + v.offsetHeight)
    );
    const probeTop = Math.min(...centerProbe.map((v) => v.offsetTop));
    const probeBottom = Math.max(
      ...centerProbe.map((v) => v.offsetTop + v.offsetHeight)
    );
    const viewTop = listNode.scrollTop;
    const viewBottom = listNode.scrollTop + listNode.clientHeight;
    const viewHeight = listNode.clientHeight;
    const centerHeight = centerBottom - centerTop;
    const viewCenter = (viewTop + viewBottom) / 2;
    
    if (!probe) {
        if (centerBottom < viewCenter) {
            setScrollOffset(listNode, -centerHeight);
        } else if (centerTop > viewCenter) {
            setScrollOffset(listNode, centerHeight);
        }
    } else {
        // screen between two probes
        if (
            (probeBottom < viewTop && probeTop + centerHeight > viewBottom) ||
            (probeTop > viewBottom && probeBottom - centerHeight < viewTop)
        ) {
            if (centerBottom < viewCenter) {
                setScrollOffset(listNode, -centerHeight);
            } else if (centerTop > viewCenter) {
                setScrollOffset(listNode, centerHeight);
            }
        } else if (probeBottom < viewTop && probeTop + centerHeight <= viewBottom) {
            // center out above, next is visible
            var offset = Math.max(Math.floor(viewHeight / centerHeight), 1) * centerHeight;
            setScrollOffset(listNode, -offset);
        } else if (probeTop > viewBottom && probeBottom - centerHeight >= viewTop) {
            // center out below, next is visible
            var offset = Math.max(Math.floor(viewHeight / centerHeight), 1) * centerHeight;
            setScrollOffset(listNode, offset);
        }
    }
}

const isWinGecko = !!/Windows NT .* rv:([^\)]+)\) Gecko\/\d{8}/.test(navigator.userAgent);

if (isWinGecko) {
    scrollUpdate = debounce(scrollUpdate, 150);
}
