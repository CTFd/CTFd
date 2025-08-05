<template>
  <div>
    <form method="POST" @submit.prevent="submitSolution">
      <div class="form-group">
        <label>
          Content<br />
          <small>Markdown &amp; HTML are supported</small>
        </label>
        <textarea
          type="text"
          class="form-control"
          name="content"
          rows="10"
          :value="this.content"
          media-type="solution"
          media-id-title="solution_id"
          :media-id="this.solution_id"
          ref="content"
        ></textarea>
      </div>

      <div class="form-group">
        <label>
          State<br />
          <small>Controls who can view this solution</small>
        </label>
        <select class="form-control custom-select" name="state" v-model="state">
          <option value="hidden">Hidden</option>
          <option value="visible">Visible</option>
        </select>
      </div>
      <button class="btn btn-primary float-right" type="submit">
        {{ solution_id ? "Update" : "Create" }} Solution
      </button>
      <div
        v-if="loading"
        class="spinner-border spinner-border-sm ml-2"
        role="status"
      >
        <span class="sr-only">Loading...</span>
      </div>
    </form>
  </div>
</template>

<script>
import CTFd from "../../compat/CTFd";
import { bindMarkdownEditor } from "../../styles";

export default {
  name: "SolutionEditor",
  props: {
    challenge_id: Number,
  },
  data: function () {
    return {
      solution_id: null,
      content: "",
      state: "hidden",
      loading: false,
    };
  },
  watch: {
    solution_id: {
      handler(val, oldVal) {
        if (oldVal == null) {
          this.loadSolution();
        }
      },
    },
  },
  methods: {
    loadSolution: function () {
      CTFd.fetch(`/api/v1/solutions/${this.solution_id}`, {
        method: "GET",
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
          if (response.success) {
            let solution = response.data;
            this.content = solution.content || "";
            this.state = solution.state || "hidden";

            // Initialize markdown editor
            let editor = this.$refs.content;
            bindMarkdownEditor(editor);
            setTimeout(() => {
              if (editor.mde) {
                editor.mde.codemirror.getDoc().setValue(this.content);
                this._forceRefresh();
              }
            }, 200);
          }
        })
        .catch((error) => {
          console.error("Error loading solution:", error);
        });
    },
    resetForm: function () {
      this.content = "";
      this.state = "hidden";

      // Initialize markdown editor for new solution
      setTimeout(() => {
        let editor = this.$refs.content;
        if (editor) {
          bindMarkdownEditor(editor);
          setTimeout(() => {
            if (editor.mde) {
              editor.mde.codemirror.getDoc().setValue("");
              this._forceRefresh();
            }
          }, 200);
        }
      }, 100);
    },
    _forceRefresh: function () {
      // Temporary function while we are relying on CodeMirror + MDE
      let editor = this.$refs.content;
      if (editor && editor.mde) {
        editor.mde.codemirror.refresh();
      }
    },
    getContent: function () {
      this._forceRefresh();
      let editor = this.$refs.content;
      if (editor && editor.mde) {
        return editor.mde.codemirror.getDoc().getValue();
      }
      return editor.value;
    },
    submitSolution: function () {
      this.loading = true;

      let params = {
        content: this.getContent(),
        state: this.state,
      };

      let url, method;
      if (this.solution_id) {
        // Update existing solution
        url = `/api/v1/solutions/${this.solution_id}`;
        method = "PATCH";
      } else {
        // Create new solution with challenge_id
        params.challenge_id = this.challenge_id;
        url = "/api/v1/solutions";
        method = "POST";
      }

      CTFd.fetch(url, {
        method: method,
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(params),
      })
        .then((response) => {
          return response.json();
        })
        .then((response) => {
          if (response.success) {
            // If we created a new solution, update the solution_id
            if (!this.solution_id) {
              this.solution_id = response.data.id;
            }
            this.loading = false;
          } else {
            this.loading = false;
            console.error("Error submitting solution:", response.errors);
          }
        })
        .catch((error) => {
          this.loading = false;
          console.error("Network error:", error);
        });
    },
  },
  created() {
    this.solution_id = window.CHALLENGE_SOLUTION_ID;
    $("a[href='#solution']").on("shown.bs.tab", (_e) => {
      this._forceRefresh();
    });
    if (this.solution_id) {
      this.loadSolution();
    } else {
      this.resetForm();
    }
  },
};
</script>

<style scoped></style>
