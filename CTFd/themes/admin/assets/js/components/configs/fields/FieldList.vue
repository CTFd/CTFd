<template>
  <div>
    <!-- You can't use index as :key here b/c Vue is crazy -->
    <!-- https://rimdev.io/the-v-for-key/ -->
    <div class="mb-5" v-for="(field, index) in fields" :key="field.id">
      <Field
        :index="index"
        :initialField.sync="fields[index]"
        @delete-field="deleteField"
      />
    </div>

    <button
      class="btn btn-sm btn-success btn-outlined float-right"
      type="button"
      @click="addField()"
    >
      Add New Field
    </button>
  </div>
</template>

<script>
import Field from "./Field.vue";

export default {
  name: "FieldList",
  components: {
    Field
  },
  props: {},
  data: function() {
    return {
      fields: []
    };
  },
  methods: {
    addField: function() {
      this.fields.push({
        id: `#${Math.random().toString(16).slice(2)}`,
        name: "",
        description: "",
        editable: false,
        required: false,
        public: false
      })
      console.log(this.$data.fields)
    },
    deleteField: function(index) {
      // if (fieldId) {
        // Wait for API implementation
      // }
      // Remove field at index
      this.fields.splice(index, 1);
      console.log(this.fields)
    }
  },
  created() {
    this.fields.push({
      id: 1,
      name: "Name",
      description: "Desc",
      editable: true,
      required: false,
      public: true
    });
  }
};
</script>
