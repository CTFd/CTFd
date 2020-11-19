<template>
  <div>
    <div class="row mb-3">
      <div class="col-md-12">
        <div class="comment">
          <textarea
            class="form-control mb-2"
            rows="2"
            id="comment-input"
            placeholder="Add comment"
            v-model.lazy="comment"
          ></textarea>
          <button
            class="btn btn-sm btn-success btn-outlined float-right"
            type="submit"
            @click="submitComment()"
          >
            Comment
          </button>
        </div>
      </div>
    </div>

    <div class="row" v-if="pages > 1">
      <div class="col-md-12">
        <div class="text-center">
          <!-- Inversed ternary b/c disabled will turn the button off -->
          <button
            type="button"
            class="btn btn-link p-0"
            @click="prevPage()"
            :disabled="prev ? false : true"
          >
            &lt;&lt;&lt;
          </button>
          <button
            type="button"
            class="btn btn-link p-0"
            @click="nextPage()"
            :disabled="next ? false : true"
          >
            &gt;&gt;&gt;
          </button>
        </div>
      </div>
      <div class="col-md-12">
        <div class="text-center">
          <small class="text-muted"
            >Page {{ page }} of {{ total }} comments</small
          >
        </div>
      </div>
    </div>
    <div class="comments">
      <transition-group name="comment-card">
        <div
          class="comment-card card mb-2"
          v-for="comment in comments"
          :key="comment.id"
        >
          <div class="card-body pl-0 pb-0 pt-2 pr-2">
            <button
              type="button"
              class="close float-right"
              aria-label="Close"
              @click="deleteComment(comment.id)"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="card-body">
            <div class="card-text" v-html="comment.html"></div>
            <small class="text-muted float-left">
              <span>
                <a :href="`${urlRoot}/admin/users/${comment.author_id}`">{{
                  comment.author.name
                }}</a>
              </span>
            </small>
            <small class="text-muted float-right">
              <span class="float-right">{{ toLocalTime(comment.date) }}</span>
            </small>
          </div>
        </div>
      </transition-group>
    </div>
    <div class="row" v-if="pages > 1">
      <div class="col-md-12">
        <div class="text-center">
          <!-- Inversed ternary b/c disabled will turn the button off -->
          <button
            type="button"
            class="btn btn-link p-0"
            @click="prevPage()"
            :disabled="prev ? false : true"
          >
            &lt;&lt;&lt;
          </button>
          <button
            type="button"
            class="btn btn-link p-0"
            @click="nextPage()"
            :disabled="next ? false : true"
          >
            &gt;&gt;&gt;
          </button>
        </div>
      </div>
      <div class="col-md-12">
        <div class="text-center">
          <small class="text-muted"
            >Page {{ page }} of {{ total }} comments</small
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CTFd from "core/CTFd";
import { default as helpers } from "core/helpers";
import dayjs from "dayjs";
import hljs from "highlight.js";
export default {
  props: {
    // These props are passed to the api via query string.
    // See this.getArgs()
    type: String,
    id: Number
  },
  data: function() {
    return {
      page: 1,
      pages: null,
      next: null,
      prev: null,
      total: null,
      comment: "",
      comments: [],
      urlRoot: CTFd.config.urlRoot
    };
  },
  methods: {
    toLocalTime(date) {
      return dayjs(date).format("MMMM Do, h:mm:ss A");
    },
    nextPage: function() {
      this.page++;
      this.loadComments();
    },
    prevPage: function() {
      this.page--;
      this.loadComments();
    },
    getArgs: function() {
      let args = {};
      args[`${this.$props.type}_id`] = this.$props.id;
      return args;
    },
    loadComments: function() {
      let apiArgs = this.getArgs();
      apiArgs[`page`] = this.page;
      apiArgs[`per_page`] = 10;

      helpers.comments.get_comments(apiArgs).then(response => {
        this.page = response.meta.pagination.page;
        this.pages = response.meta.pagination.pages;
        this.next = response.meta.pagination.next;
        this.prev = response.meta.pagination.prev;
        this.total = response.meta.pagination.total;
        this.comments = response.data;
        return this.comments;
      });
    },
    submitComment: function() {
      let comment = this.comment.trim();
      if (comment.length > 0) {
        helpers.comments.add_comment(
          comment,
          this.$props.type,
          this.getArgs(),
          () => {
            this.loadComments();
          }
        );
      }
      this.comment = "";
    },
    deleteComment: function(commentId) {
      if (confirm("Are you sure you'd like to delete this comment?")) {
        helpers.comments.delete_comment(commentId).then(response => {
          if (response.success === true) {
            for (let i = this.comments.length - 1; i >= 0; --i) {
              if (this.comments[i].id == commentId) {
                this.comments.splice(i, 1);
              }
            }
          }
        });
      }
    }
  },
  created() {
    this.loadComments();
  },
  updated() {
    this.$el.querySelectorAll("pre code").forEach(block => {
      hljs.highlightBlock(block);
    });
  }
};
</script>

<style scoped>
.card .close {
  opacity: 0;
  transition: 0.2s;
}
.card:hover .close {
  opacity: 0.5;
}
.close:hover {
  opacity: 0.75 !important;
}

.comment-card-leave {
  max-height: 200px;
}
.comment-card-leave-to {
  max-height: 0;
}
.comment-card-active {
  position: absolute;
}
.comment-card-enter-active,
.comment-card-move,
.comment-card-leave-active {
  transition: all 0.3s;
}
</style>
