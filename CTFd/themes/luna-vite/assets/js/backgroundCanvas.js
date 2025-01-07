const BackgroundCanvasResources = {
    canvas: null,
    iconWallCanvas: null
};

const rad50 = 0.872665;
const rad40 = Math.PI / 2 - rad50;
const scale = 0.5;

function buildIconWallData(w, h, iconWall) {
    const offscreenCanvas = document.createElement("canvas");
    const offscreenCtx = offscreenCanvas.getContext("2d");

    const a1 = w * Math.cos(rad40),
        a2 = h * Math.cos(rad50),
        b1 = h * Math.cos(rad40),
        b2 = w * Math.cos(rad50);

    const width = (b1 + b2) / scale;
    const height = (a1 + a2 + 580) / scale;

    offscreenCanvas.width = width;
    offscreenCanvas.height = height;

    const pattern = offscreenCtx.createPattern(iconWall, "repeat");
    offscreenCtx.fillStyle = pattern;
    offscreenCtx.fillRect(0, 0, width, height);
    BackgroundCanvasResources.offscreenCanvas = offscreenCanvas;
}

function drawPatternScale(ctx, offscreenCanvas, startx, starty, width, height) {
    ctx.scale(scale, scale);
    ctx.drawImage(offscreenCanvas, startx / scale, starty / scale, width / scale, height / scale);
    ctx.restore();
}

function render(timer) {
    timer = (timer / 30) % 580;
    const { canvas, offscreenCanvas } = BackgroundCanvasResources;
    if (canvas && offscreenCanvas) {
        const ctx = canvas.getContext("2d");
        ctx.save();
        const w = canvas.width,
            h = canvas.height;
        ctx.clearRect(0, 0, w, h);
        ctx.save();
        ctx.rotate(rad50);
        const a1 = w * Math.cos(rad40),
            a2 = h * Math.cos(rad50),
            b1 = h * Math.cos(rad40),
            b2 = w * Math.cos(rad50);
        ctx.translate(0, -timer);
        drawPatternScale(ctx, offscreenCanvas, 0, -a1, b1 + b2, a1 + a2 + 580);
    }
}

function frame(timer) {
    render(timer);
    return window.requestAnimationFrame(frame);
}

export default function IconWallCanvasInit() {
    const container = document.querySelector(".triangleContainer");
    if (!container || container.classList.contains("page-challenges-listing")) {
        return;
    }
    var canvas = document.getElementById("iconWallCanvas");
    if (!canvas) {
        canvas = document.createElement("canvas");
        canvas.id = "iconWallCanvas";
        canvas.classList.add("iconWallCanvas");
        container.insertBefore(canvas, container.firstChild);
    }
    const iconWall = new Image();
    iconWall.crossOrigin = "anonymous";
    iconWall.onload = () => {
        buildIconWallData(canvas.width, canvas.height, iconWall);
    };
    iconWall.src = /(?:")(.+)(?=")/g.exec(getComputedStyle(document.documentElement).getPropertyValue("--icon-wall"))[1];

    BackgroundCanvasResources.canvas = canvas;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    window.addEventListener("resize", () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        buildIconWallData(canvas.width, canvas.height, iconWall);
    });

    window.requestAnimationFrame(frame);
}