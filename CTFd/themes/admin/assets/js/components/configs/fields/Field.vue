<template>
  <div class="border-bottom">

    <div>
      <button
        type="button"
        class="close float-right"
        aria-label="Close"
        @click="deleteField()"
      >
        <span aria-hidden="true">&times;</span>
      </button>
    </div>

    <div class="row">
      <div class="col-md-3">
        <div class="form-group">
          <label>Field Type</label>
          <select class="form-control custom-select">
            <option>Text Field</option>
            <option>Checkbox</option>
          </select>
          <small class="form-text text-muted">Type of field shown to the user</small>
        </div>
      </div>
      <div class="col-md-9">
        <div class="form-group">
          <label>Field Name</label>
          <input type="text" class="form-control" v-model.lazy="field.name">
          <small class="form-text text-muted">Field name</small>
        </div>
      </div>

      <div class="col-md-12">
        <div class="form-group">
          <label>Field Description</label>
          <input type="text" class="form-control" v-model.lazy="field.description">
          <small id="emailHelp" class="form-text text-muted">Field Description</small>
        </div>
      </div>

      <div class="col-md-12">
        <div class="form-check">
          <label class="form-check-label">
              <input class="form-check-input" type="checkbox" v-model.lazy="field.editable"> Editable by user in profile
          </label>
        </div>
        <div class="form-check">
          <label class="form-check-label">
            <input class="form-check-input" type="checkbox" v-model.lazy="field.required"> Required on registration
          </label>
        </div>
        <div class="form-check">
          <label class="form-check-label">
            <input class="form-check-input" type="checkbox" v-model.lazy="field.public"> Shown on public profile
          </label>
        </div>
      </div>
    </div>

    <div class="row pb-3">
      <div class="col-md-12">
        <div class="d-block">
          <button
            class="btn btn-sm btn-success btn-outlined float-right"
            type="button"
            @click="saveField()"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    index: Number,
    initialField: Object
  },
  data: function() {
    return {
      field: this.initialField
    }
  },
  methods: {
    saveField: function(){
      console.log(this.field)
      // Update field in API
    },
    deleteField: function() {
      // Delete field in API
      this.$emit('delete-field', this.index);
    },
  }
}
</script>

<style scoped>
</style>