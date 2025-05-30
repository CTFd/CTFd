<template>
  <div id="flag-edit-modal" class="modal fade" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header text-center">
          <div class="container">
            <div class="row">
              <div class="col-md-12">
                <h3>Edit Flag</h3>
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
          <component
            v-if="flag && selectedTypeComponent"
            :is="selectedTypeComponent"
            :mode="'edit'"
            :initialData="flag"
            @submit="updateFlag"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StaticFlagForm from "./StaticFlagForm.vue";
import RegexFlagForm from "./RegexFlagForm.vue";
import CTFd from "../../compat/CTFd";

export default {
  name: "FlagEditForm",
  props: {
    flag_id: Number,
  },
  components: {
    StaticFlagForm,
    RegexFlagForm,
  },
  data() {
    return {
      flag: null,
    };
  },
  computed: {
    selectedTypeComponent() {
      if (!this.flag) return null;
      switch (this.flag.type) {
        case "static":
          return "StaticFlagForm";
        case "regex":
          return "RegexFlagForm";
        default:
          return null;
      }
    },
  },
  watch: {
    flag_id: {
      immediate: true,
      handler(val) {
        if (val !== null) {
          this.loadFlag();
        }
      },
    },
  },
  methods: {
    loadFlag() {
      CTFd.fetch(`/api/v1/flags/${this.flag_id}`, {
        method: "GET",
      })
        .then((res) => res.json())
        .then((res) => {
          this.flag = res.data;
        });
    },
    updateFlag(params) {
      CTFd.fetch(`/api/v1/flags/${this.flag_id}`, {
        method: "PATCH",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(params),
      })
        .then((response) => response.json())
        .then((_response) => {
          this.$emit("refreshFlags", this.$options.name);
        });
    },
  },
};
</script>

<style scoped></style>
