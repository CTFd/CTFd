<template>
  <div>
    <div>
      <FlagCreationForm
        ref="FlagCreationForm"
        :challenge_id="challenge_id"
        @refreshFlags="refreshFlags"
      />
    </div>

    <div>
      <FlagEditForm
        ref="FlagEditForm"
        :flag_id="editing_flag_id"
        @refreshFlags="refreshFlags"
      />
    </div>

    <table id="flagsboard" class="table table-striped">
      <thead>
        <tr>
          <td class="text-center"><b>Type</b></td>
          <td class="text-center"><b>Flag</b></td>
          <td class="text-center"><b>Settings</b></td>
        </tr>
      </thead>
      <tbody>
        <tr :name="flag.id" v-for="flag in flags" :key="flag.id">
          <td class="text-center">{{ flag.type }}</td>
          <td class="text-break">
            <pre class="flag-content">{{ flag.content }}</pre>
          </td>
          <td class="text-center">
            <i
              role="button"
              class="btn-fa fas fa-edit edit-flag"
              :flag-id="flag.id"
              :flag-type="flag.type"
              @click="editFlag(flag.id)"
            ></i>
            <i
              role="button"
              class="btn-fa fas fa-times delete-flag"
              :flag-id="flag.id"
              @click="deleteFlag(flag.id)"
            ></i>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="col-md-12">
      <button
        id="flag-add-button"
        class="btn btn-success d-inline-block float-right"
        @click="addFlag()"
      >
        Create Flag
      </button>
    </div>
  </div>
</template>

<script>
import $ from "jquery";
import CTFd from "core/CTFd";
import FlagCreationForm from "./FlagCreationForm.vue";
import FlagEditForm from "./FlagEditForm.vue";

export default {
  components: {
    FlagCreationForm,
    FlagEditForm
  },
  props: {
    challenge_id: Number
  },
  data: function() {
    return {
      flags: [],
      editing_flag_id: null
    };
  },
  methods: {
    loadFlags: function() {
      CTFd.fetch(`/api/v1/challenges/${this.$props.challenge_id}/flags`, {
        method: "GET",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        }
      })
        .then(response => {
          return response.json();
        })
        .then(response => {
          if (response.success) {
            this.flags = response.data;
          }
        });
    },
    refreshFlags(caller) {
      this.loadFlags();
      let modal;
      switch (caller) {
        case "FlagEditForm":
          modal = this.$refs.FlagEditForm.$el;
          $(modal).modal("hide");
          break;
        case "FlagCreationForm":
          modal = this.$refs.FlagCreationForm.$el;
          $(modal).modal("hide");
          break;
        default:
          break;
      }
    },
    addFlag: function() {
      let modal = this.$refs.FlagCreationForm.$el;
      $(modal).modal();
    },
    editFlag: function(flag_id) {
      this.editing_flag_id = flag_id;
      let modal = this.$refs.FlagEditForm.$el;
      $(modal).modal();
    },
    deleteFlag: function(flag_id) {
      if (confirm("Are you sure you'd like to delete this flag?")) {
        CTFd.fetch(`/api/v1/flags/${flag_id}`, {
          method: "DELETE"
        })
          .then(response => {
            return response.json();
          })
          .then(response => {
            if (response.success) {
              this.loadFlags();
            }
          });
      }
    }
  },
  created() {
    this.loadFlags();
  }
};
</script>

<style scoped></style>
