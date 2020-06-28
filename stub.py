import glob
import os

static_js_dirs = [
    "CTFd/themes/core/static/js/**/*.dev.js",
    "CTFd/themes/admin/static/js/**/*.dev.js",
]

for js_dir in static_js_dirs:
    for path in glob.glob(js_dir, recursive=True):
        if path.endswith(".dev.js"):
            path = path.replace(".dev.js", ".min.js")
            if os.path.isfile(path) is False:
                open(path, "a").close()
