function get_filetype_icon_class(filename) {
  var mapping = {
    // Image Files
    png: "fa-file-image",
    jpg: "fa-file-image",
    jpeg: "fa-file-image",
    gif: "fa-file-image",
    bmp: "fa-file-image",
    svg: "fa-file-image",

    // Text Files
    txt: "fa-file-alt",

    // Video Files
    mov: "fa-file-video",
    mp4: "fa-file-video",
    wmv: "fa-file-video",
    flv: "fa-file-video",
    mkv: "fa-file-video",
    avi: "fa-file-video",

    // PDF Files
    pdf: "fa-file-pdf",

    // Audio Files
    mp3: "fa-file-sound",
    wav: "fa-file-sound",
    aac: "fa-file-sound",

    // Archive Files
    zip: "fa-file-archive",
    gz: "fa-file-archive",
    tar: "fa-file-archive",
    "7z": "fa-file-archive",
    rar: "fa-file-archive",

    // Code Files
    py: "fa-file-code",
    c: "fa-file-code",
    cpp: "fa-file-code",
    html: "fa-file-code",
    js: "fa-file-code",
    rb: "fa-file-code",
    go: "fa-file-code"
  };

  var ext = filename.split(".").pop();
  return mapping[ext];
}

function get_page_files() {
  return CTFd.fetch("/api/v1/files?type=page", {
    credentials: "same-origin"
  }).then(function(response) {
    return response.json();
  });
}

// .
// then(function (data) {
//     data.map(function (f) {
//         console.log(f);
//     });
// });
