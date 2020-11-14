<template>
    <div id="flag-edit-modal" class="modal fade" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header text-center">
                    <div class="container">
                        <div class="row">
                            <div class="col-md-12">
                                <h3 class="text-center">Edit Flag</h3>
                            </div>
                        </div>
                    </div>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <form method="POST" v-html="editForm" @submit.prevent="updateFlag">
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import $ from "jquery";
import CTFd from "core/CTFd";
import nunjucks from "nunjucks";

export default {
  props: {
    flag_id: Number
  },
  data: function() {
    return {
      flag: {},
      editForm: "",
    };
  },
  methods: {
    loadFlag: function() {
      CTFd.fetch(`/api/v1/flags/${this.$props.flag_id}`, {
        method: "GET"
      })
        .then(response => {
          return response.json();
        })
        .then(response => {
          this.flag = response.data;
          let editFormURL = this.flag["templates"]["update"];

          $.get(CTFd.config.urlRoot + editFormURL, template_data => {
            const template = nunjucks.compile(template_data);
            this.editForm = template.render(this.flag);
          });
        });
    },
    updateFlag: function(event) {
      let form = $(event.target);
      let params = form.serializeJSON(true);

      CTFd.fetch(`/api/v1/flags/${this.$props.flag_id}`, {
        method: "PATCH",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
      })
        .then(function(response) {
          return response.json();
        })
        .then(function(response) {
          // TODO: Refresh the list of flags
          window.location.reload();
          // if (response.success) {
          //   $(row)
          //     .find(".flag-content")
          //     .text(response.data.content);
          //   $("#edit-flags").modal("toggle");
          // }
        });
    },
  },
  created() {
    this.loadFlag();
  }
};
</script>

<style scoped></style>
