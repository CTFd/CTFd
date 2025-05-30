<template>
  <div id="flag-create-modal" class="modal fade" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header text-center">
          <div class="container">
            <div class="row">
              <div class="col-md-12">
                <h3>Create Flag</h3>
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
          <label for="create-keys-select" class="control-label">
            Choose Flag Type
          </label>
          <select
            class="form-control custom-select"
            v-model="selectedType"
          >
            <option disabled value="">--</option>
            <option value="static">static</option>
            <option value="regex">regex</option>
            <!-- Add more as needed -->
          </select>

          <br />

          <component
            v-if="selectedTypeComponent"
            :is="selectedTypeComponent"
            :challenge_id="challenge_id"
            @submit="submitFlag"
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
  name: "FlagCreationForm",
  props: {
    challenge_id: Number,
  },
  components: {
    StaticFlagForm,
    RegexFlagForm,
  },
  data() {
    return {
      selectedType: "",
    };
  },
  computed: {
    selectedTypeComponent() {
      switch (this.selectedType) {
        case "static":
          return "StaticFlagForm";
        case "regex":
          return "RegexFlagForm";
        default:
          return null;
      }
    },
  },
  methods: {
    submitFlag(params) {
      CTFd.fetch("/api/v1/flags", {
        method: "POST",
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

