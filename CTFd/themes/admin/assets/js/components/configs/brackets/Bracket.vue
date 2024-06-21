<template>
  <div class="border-bottom">
    <div>
      <button
        type="button"
        class="close float-right"
        aria-label="Close"
        @click="deleteBracket()"
      >
        <span aria-hidden="true">&times;</span>
      </button>
    </div>

    <div class="row">
      <div class="col-md-9">
        <div class="form-group">
          <label>Bracket Name</label>
          <input type="text" class="form-control" v-model.lazy="bracket.name" />
          <small class="form-text text-muted">
            Bracket name (e.g. "Students", "Interns", "Engineers")
          </small>
        </div>
      </div>

      <div class="col-md-12">
        <div class="form-group">
          <label>Bracket Description</label>
          <input
            type="text"
            class="form-control"
            v-model.lazy="bracket.description"
          />
          <small class="form-text text-muted">Bracket Description</small>
        </div>
      </div>

      <div class="col-md-12">
        <label>Bracket Type</label>
        <select class="custom-select" v-model.lazy="bracket.type">
          <option></option>
          <option value="users">Users</option>
          <option value="teams">Teams</option>
        </select>
        <small class="form-text text-muted">
          If you are using Team Mode and would like the bracket to apply to
          entire teams instead of individuals, select Teams.
        </small>
      </div>
    </div>

    <div class="row pb-3">
      <div class="col-md-12">
        <div class="d-block">
          <button
            class="btn btn-sm btn-success btn-outlined float-right"
            type="button"
            @click="saveBracket()"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CTFd from "../../../compat/CTFd";
import { ezToast } from "../../../compat/ezq";

export default {
  props: {
    index: Number,
    initialBracket: Object,
  },
  data: function () {
    return {
      bracket: this.initialBracket,
    };
  },
  methods: {
    persisted: function () {
      // We're using Math.random() for unique IDs so new items have IDs < 1
      // Real items will have an ID > 1
      return this.bracket.id >= 1;
    },
    saveBracket: function () {
      let body = this.bracket;
      let url = "";
      let method = "";
      let message = "";
      if (this.persisted()) {
        url = `/api/v1/brackets/${this.bracket.id}`;
        method = "PATCH";
        message = "Bracket has been updated!";
      } else {
        url = `/api/v1/brackets`;
        method = "POST";
        message = "Bracket has been created!";
      }
      CTFd.fetch(url, {
        method: method,
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      })
        .then((response) => {
          return response.json();
        })
        .then((response) => {
          if (response.success === true) {
            this.field = response.data;
            ezToast({
              title: "Success",
              body: message,
              delay: 1000,
            });
          }
        });
    },
    deleteBracket: function () {
      if (confirm("Are you sure you'd like to delete this bracket?")) {
        if (this.persisted()) {
          CTFd.fetch(`/api/v1/brackets/${this.bracket.id}`, {
            method: "DELETE",
            credentials: "same-origin",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
          })
            .then((response) => {
              return response.json();
            })
            .then((response) => {
              if (response.success === true) {
                this.$emit("remove-bracket", this.index);
              }
            });
        } else {
          this.$emit("remove-bracket", this.index);
        }
      }
    },
  },
};
</script>
