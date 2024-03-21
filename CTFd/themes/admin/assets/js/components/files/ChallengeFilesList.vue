<template>
  <div>
    <table id="filesboard" class="table table-striped">
      <thead>
        <tr>
          <td class="text-center"><b>File</b></td>
          <td class="text-center"><b>Settings</b></td>
        </tr>
      </thead>
      <tbody>
        <tr v-for="file in files" :key="file.id">
          <td class="text-center">
            <a :href="`${urlRoot}/files/${file.location}`">{{
              file.location.split("/").pop()
            }}</a>
          </td>

          <td class="text-center">
            <i
              role="button"
              class="btn-fa fas fa-times delete-file"
              @click="deleteFile(file.id)"
            ></i>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="col-md-12 mt-3">
      <form method="POST" ref="FileUploadForm" @submit.prevent="addFiles">
        <div class="form-group">
          <input
            class="form-control-file"
            id="file"
            multiple=""
            name="file"
            required=""
            type="file"
          />
          <sub class="text-muted">
            Attach multiple files using Control+Click or Cmd+Click.
          </sub>
        </div>
        <div class="form-group">
          <input
            class="btn btn-success float-right"
            id="_submit"
            name="_submit"
            type="submit"
            value="Upload"
          />
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ezQuery } from "../../compat/ezq";
import { default as helpers } from "../../compat/helpers";
import CTFd from "../../compat/CTFd";

export default {
  props: {
    challenge_id: Number,
  },
  data: function () {
    return {
      files: [],
      urlRoot: CTFd.config.urlRoot,
    };
  },
  methods: {
    loadFiles: function () {
      CTFd.fetch(`/api/v1/challenges/${this.$props.challenge_id}/files`, {
        method: "GET",
      })
        .then((response) => {
          return response.json();
        })
        .then((response) => {
          if (response.success) {
            this.files = response.data;
          }
        });
    },
    addFiles: function () {
      let data = {
        challenge: this.$props.challenge_id,
        type: "challenge",
      };
      let form = this.$refs.FileUploadForm;
      helpers.files.upload(form, data, (_response) => {
        setTimeout(() => {
          this.loadFiles();
        }, 700);
      });
    },
    deleteFile: function (fileId) {
      ezQuery({
        title: "Delete Files",
        body: "Are you sure you want to delete this file?",
        success: () => {
          CTFd.fetch(`/api/v1/files/${fileId}`, {
            method: "DELETE",
          })
            .then((response) => {
              return response.json();
            })
            .then((response) => {
              if (response.success) {
                this.loadFiles();
              }
            });
        },
      });
    },
  },
  created() {
    this.loadFiles();
  },
};
</script>

<style scoped></style>
