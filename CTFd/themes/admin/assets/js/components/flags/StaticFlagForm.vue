<!-- components/flags/StaticFlagForm.vue -->
<template>
  <div>
    <div class="form-group">
      <label for="static-flag">Flag</label>
      <input
        v-model="flag"
        type="text"
        class="form-control"
        id="static-flag"
        name="flag"
        required
      />
    </div>
    <div class="form-group">
      <label for="static-data">Data (optional)</label>
      <input
        v-model="data"
        type="text"
        class="form-control"
        id="static-data"
        name="data"
      />
    </div>
    <button class="btn btn-success float-right" @click="submit">
      Create Flag
    </button>
  </div>
</template>

<script>
export default {
  name: "StaticFlagForm",
  props: {
    challenge_id: Number,
    mode: {
      type: String,
      default: "create",
    },
    initialData: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      flag: this.initialData.content || "",
      data: this.initialData.data || "",
    };
  },
  methods: {
    submit() {
      const params = {
        type: "static",
        content: this.flag,
        data: this.data,
      };

      if (this.challenge_id) {
        params.challenge = this.challenge_id;
      }

      if (this.mode === "edit") {
        params.id = this.initialData.id;
      }

      this.$emit("submit", params);
    },
  },
};
</script>

