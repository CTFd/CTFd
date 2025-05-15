<!-- components/flags/RegexFlagForm.vue -->
<template>
  <div>
    <div class="form-group">
      <label for="regex-flag">Regular Expression</label>
      <input
        v-model="flag"
        type="text"
        class="form-control"
        id="regex-flag"
        name="flag"
        placeholder="e.g. ^CTF\{[a-zA-Z0-9]+\}$"
        required
      />
    </div>
    <div class="form-group">
      <label for="regex-data">Case Sensitive</label>
      <select
        v-model="data"
        class="form-control custom-select"
        id="regex-data"
        name="data"
      >
        <option value="true">Yes</option>
        <option value="false">No</option>
      </select>
    </div>
    <button class="btn btn-success float-right" @click="submit">
      Create Flag
    </button>
  </div>
</template>

<script>
export default {
  name: "RegexFlagForm",
  props: {
    challenge_id: {
      type: Number,
      default: null,
    },
    mode: {
      type: String,
      default: "create", // or "edit"
    },
    initialData: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      flag: this.initialData.content || "",
      data: this.initialData.data || "true", // case sensitivity flag
    };
  },
  methods: {
    submit() {
      const params = {
        type: "regex",
        content: this.flag,
        data: this.data,
      };

      if (this.challenge_id) {
        params.challenge = this.challenge_id;
      }

      if (this.mode === "edit" && this.initialData.id) {
        params.id = this.initialData.id;
      }

      this.$emit("submit", params);
    },
  },
};
</script>

