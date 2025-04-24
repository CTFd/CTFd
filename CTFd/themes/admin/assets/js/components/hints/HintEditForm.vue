<template>
  <div class="modal fade" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header text-center">
          <div class="container">
            <div class="row">
              <div class="col-md-12">
                <h3>Hint</h3>
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
        <form method="POST" @submit.prevent="updateHint">
          <div class="modal-body">
            <div class="container">
              <div class="row">
                <div class="col-md-12">
                  <div class="form-group">
                    <label>
                      Title<br />
                      <small>Content displayed before hint unlocking</small>
                    </label>
                    <input
                      type="text"
                      class="form-control"
                      name="title"
                      :value="this.title"
                      ref="title"
                    />
                  </div>

                  <div class="form-group">
                    <label>
                      Hint<br />
                      <small>Markdown &amp; HTML are supported</small>
                    </label>
                    <!-- Explicitly don't put the markdown class on this because we will add it later -->
                    <textarea
                      type="text"
                      class="form-control"
                      name="content"
                      rows="7"
                      :value="this.content"
                      ref="content"
                    ></textarea>
                  </div>

                  <div class="form-group">
                    <label>
                      Cost<br />
                      <small>How many points it costs to see your hint.</small>
                    </label>
                    <input
                      type="number"
                      class="form-control"
                      name="cost"
                      v-model.lazy="cost"
                    />
                  </div>

                  <div class="form-group">
                    <label>
                      Requirements<br />
                      <small
                        >Hints that must be unlocked before unlocking this
                        hint</small
                      >
                    </label>
                    <div
                      class="form-check"
                      v-for="hint in otherHints"
                      :key="hint.id"
                    >
                      <label class="form-check-label cursor-pointer">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          :value="hint.id"
                          v-model="selectedHints"
                        />
                        {{ hint.content }} - {{ hint.cost }}
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <div class="container">
              <div class="row">
                <div class="col-md-12">
                  <button class="btn btn-primary float-right">Submit</button>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import CTFd from "../../compat/CTFd";
import { bindMarkdownEditor } from "../../styles";

export default {
  name: "HintEditForm",
  props: {
    challenge_id: Number,
    hint_id: Number,
    hints: Array,
  },
  data: function () {
    return {
      cost: 0,
      title: null,
      content: null,
      selectedHints: [],
    };
  },
  computed: {
    // Get all hints besides the current one
    otherHints: function () {
      return this.hints.filter((hint) => {
        return hint.id !== this.$props.hint_id;
      });
    },
  },
  watch: {
    hint_id: {
      immediate: true,
      handler(val, oldVal) {
        if (val !== null) {
          this.loadHint();
        }
      },
    },
  },
  methods: {
    loadHint: function () {
      CTFd.fetch(`/api/v1/hints/${this.$props.hint_id}?preview=true`, {
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
            let hint = response.data;
            this.cost = hint.cost;
            this.title = hint.title;
            this.content = hint.content;
            this.selectedHints = hint.requirements?.prerequisites || [];
            // Wait a little longer because we need the modal to appear.
            // Kinda nasty but not really avoidable without polling the DOM via CodeMirror
            let editor = this.$refs.content;
            bindMarkdownEditor(editor);
            setTimeout(() => {
              editor.mde.codemirror.getDoc().setValue(editor.value);
              this._forceRefresh();
            }, 200);
          }
        });
    },
    _forceRefresh: function () {
      // Temporary function while we are relying on CodeMirror + MDE
      let editor = this.$refs.content;
      editor.mde.codemirror.refresh();
    },
    getCost: function () {
      return this.cost || 0;
    },
    getContent: function () {
      this._forceRefresh();
      let editor = this.$refs.content;
      return editor.mde.codemirror.getDoc().getValue();
    },
    getTitle: function () {
      return this.$refs.title.value;
    },
    updateHint: function () {
      let params = {
        challenge_id: this.$props.challenge_id,
        content: this.getContent(),
        cost: this.getCost(),
        title: this.getTitle(),
        requirements: { prerequisites: this.selectedHints },
      };

      CTFd.fetch(`/api/v1/hints/${this.$props.hint_id}`, {
        method: "PATCH",
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
            this.$emit("refreshHints", this.$options.name);
          }
        });
    },
  },
  mounted() {
    if (this.hint_id) {
      this.loadHint();
    }
  },
  created() {
    if (this.hint_id) {
      this.loadHint();
    }
  },
};
</script>

<style scoped></style>
