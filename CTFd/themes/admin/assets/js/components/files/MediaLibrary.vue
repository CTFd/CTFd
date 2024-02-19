<template>
  <div id="media-modal" class="modal fade" tabindex="-1">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <div class="container">
            <div class="row">
              <div class="col-md-12">
                <h3 class="text-center">Media Library</h3>
              </div>
            </div>
          </div>
          <button
            type="button"
            class="close"
            data-dismiss="modal"
            aria-label="Close"
          >
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="modal-header">
            <div class="container">
              <div class="row mh-100">
                <div class="col-md-6" id="media-library-list">
                  <div
                    class="media-item-wrapper"
                    v-for="file in files"
                    :key="file.id"
                  >
                    <a
                      href="javascript:void(0)"
                      @click="
                        selectFile(file)
                        // return false;
                      "
                    >
                      <i
                        v-bind:class="getIconClass(file.location)"
                        aria-hidden="true"
                      ></i>
                      <small class="media-item-title pl-1">{{
                        file.location.split("/").pop()
                      }}</small>
                    </a>
                  </div>
                </div>
                <div class="col-md-6" id="media-library-details">
                  <h4 class="text-center">Media Details</h4>
                  <div id="media-item">
                    <div class="text-center" id="media-icon">
                      <div v-if="this.selectedFile">
                        <div
                          v-if="
                            getIconClass(this.selectedFile.location) ===
                            'far fa-file-image'
                          "
                        >
                          <img
                            v-bind:src="buildSelectedFileUrl()"
                            style="
                              max-width: 100%;
                              max-height: 100%;
                              object-fit: contain;
                            "
                          />
                        </div>
                        <div v-else>
                          <i
                            v-bind:class="`${getIconClass(
                              this.selectedFile.location,
                            )} fa-4x`"
                            aria-hidden="true"
                          ></i>
                        </div>
                      </div>
                    </div>
                    <br />
                    <div
                      class="text-center"
                      id="media-filename"
                      v-if="this.selectedFile"
                    >
                      <a v-bind:href="buildSelectedFileUrl()" target="_blank">
                        {{ this.selectedFile.location.split("/").pop() }}
                      </a>
                    </div>
                    <br />

                    <div class="form-group">
                      <div v-if="this.selectedFile">
                        Link:
                        <input
                          class="form-control"
                          type="text"
                          id="media-link"
                          v-bind:value="buildSelectedFileUrl()"
                          readonly
                        />
                      </div>
                      <div v-else>
                        Link:
                        <input
                          class="form-control"
                          type="text"
                          id="media-link"
                          readonly
                        />
                      </div>
                    </div>

                    <div class="form-group text-center">
                      <div class="row">
                        <div class="col-md-6">
                          <button
                            @click="insertSelectedFile"
                            class="btn btn-success w-100"
                            id="media-insert"
                            data-toggle="tooltip"
                            data-placement="top"
                            title="Insert link into editor"
                          >
                            Insert
                          </button>
                        </div>
                        <div class="col-md-3">
                          <button
                            @click="downloadSelectedFile"
                            class="btn btn-primary w-100"
                            id="media-download"
                            data-toggle="tooltip"
                            data-placement="top"
                            title="Download file"
                          >
                            <i class="fas fa-download"></i>
                          </button>
                        </div>
                        <div class="col-md-3">
                          <button
                            @click="deleteSelectedFile"
                            class="btn btn-danger w-100"
                            id="media-delete"
                            data-toggle="tooltip"
                            data-placement="top"
                            title="Delete file"
                          >
                            <i class="far fa-trash-alt"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <form id="media-library-upload" enctype="multipart/form-data">
            <div class="form-row pt-3">
              <div class="col">
                <div class="form-group">
                  <label for="media-files">Upload Files</label>
                  <input
                    type="file"
                    name="file"
                    id="media-files"
                    class="form-control-file"
                    multiple
                  />
                  <sub class="help-block">
                    Attach multiple files using Control+Click or Cmd+Click.
                  </sub>
                </div>
              </div>
              <div class="col">
                <div class="form-group">
                  <label>Upload File Location</label>
                  <input
                    class="form-control"
                    type="text"
                    name="location"
                    placeholder="Location"
                  />
                  <sub class="help-block">
                    Route where file will be accessible (if not provided a
                    random folder will be used). <br />
                    Provide as <code>directory/filename.ext</code>
                  </sub>
                </div>
              </div>
            </div>
            <input type="hidden" value="page" name="type" />
          </form>
        </div>
        <div class="modal-footer">
          <div class="float-right">
            <button
              @click="uploadChosenFiles"
              type="submit"
              class="btn btn-primary media-upload-button"
            >
              Upload
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CTFd from "../../compat/CTFd";
import { default as helpers } from "../../compat/helpers";

function get_page_files() {
  return CTFd.fetch("/api/v1/files?type=page", {
    credentials: "same-origin",
  }).then(function (response) {
    return response.json();
  });
}

export default {
  props: {
    editor: Object,
  },
  data: function () {
    return {
      files: [],
      selectedFile: null,
    };
  },
  methods: {
    getPageFiles: function () {
      get_page_files().then((response) => {
        this.files = response.data;
        return this.files;
      });
    },
    uploadChosenFiles: function () {
      // TODO: We should reduce the need to interact with the DOM directly.
      // This looks jank and we should be able to remove it.
      let form = document.querySelector("#media-library-upload");
      helpers.files.upload(form, {}, (_data) => {
        this.getPageFiles();
      });
    },
    selectFile: function (file) {
      this.selectedFile = file;
      return this.selectedFile;
    },
    buildSelectedFileUrl: function () {
      return CTFd.config.urlRoot + "/files/" + this.selectedFile.location;
    },
    deleteSelectedFile: function () {
      var file_id = this.selectedFile.id;

      if (confirm("Are you sure you want to delete this file?")) {
        CTFd.fetch("/api/v1/files/" + file_id, {
          method: "DELETE",
        }).then((response) => {
          if (response.status === 200) {
            response.json().then((object) => {
              if (object.success) {
                this.getPageFiles();
                this.selectedFile = null;
              }
            });
          }
        });
      }
    },
    insertSelectedFile: function () {
      let editor = this.$props.editor;
      if (editor.hasOwnProperty("codemirror")) {
        editor = editor.codemirror;
      }
      let doc = editor.getDoc();
      let cursor = doc.getCursor();

      let url = this.buildSelectedFileUrl();
      let img =
        this.getIconClass(this.selectedFile.location) === "far fa-file-image";
      let filename = url.split("/").pop();
      link = "[{0}]({1})".format(filename, url);
      if (img) {
        link = "!" + link;
      }

      doc.replaceRange(link, cursor);
    },
    downloadSelectedFile: function () {
      var link = this.buildSelectedFileUrl();
      window.open(link, "_blank");
    },
    getIconClass: function (filename) {
      var mapping = {
        // Image Files
        png: "far fa-file-image",
        jpg: "far fa-file-image",
        jpeg: "far fa-file-image",
        gif: "far fa-file-image",
        bmp: "far fa-file-image",
        svg: "far fa-file-image",

        // Text Files
        txt: "far fa-file-alt",

        // Video Files
        mov: "far fa-file-video",
        mp4: "far fa-file-video",
        wmv: "far fa-file-video",
        flv: "far fa-file-video",
        mkv: "far fa-file-video",
        avi: "far fa-file-video",

        // PDF Files
        pdf: "far fa-file-pdf",

        // Audio Files
        mp3: "far fa-file-sound",
        wav: "far fa-file-sound",
        aac: "far fa-file-sound",

        // Archive Files
        zip: "far fa-file-archive",
        gz: "far fa-file-archive",
        tar: "far fa-file-archive",
        "7z": "far fa-file-archive",
        rar: "far fa-file-archive",

        // Code Files
        py: "far fa-file-code",
        c: "far fa-file-code",
        cpp: "far fa-file-code",
        html: "far fa-file-code",
        js: "far fa-file-code",
        rb: "far fa-file-code",
        go: "far fa-file-code",
      };

      var ext = filename.split(".").pop();
      return mapping[ext] || "far fa-file";
    },
  },
  created() {
    return this.getPageFiles();
  },
};
</script>
