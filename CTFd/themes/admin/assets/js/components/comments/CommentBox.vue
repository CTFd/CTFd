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
    <div class="comments">
      <div
        class="card mb-2"
        v-for="comment in comments.slice().reverse()"
        :key="comment.id"
      >
        <div class="card-body">
          <div class="card-text" v-html="comment.html"></div>
          <small class="text-muted float-left">
            <span>{{ comment.author.name }}</span>
          </small>
          <small class="text-muted float-right">
            <span class="float-right">{{ toLocalTime(comment.date) }}</span>
          </small>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CTFd from "core/CTFd";
import { default as helpers } from "core/helpers";
import Moment from "moment";
export default {
  props: {
    // These props are passed to the api via query string.
    // See this.getArgs()
    type: String,
    id: Number
  },
  data: function() {
    return {
      comment: "",
      comments: []
    };
  },
  methods: {
    toLocalTime(date) {
      return Moment(date)
        .local()
        .format("MMMM Do, h:mm:ss A");
    },
    getArgs: function() {
      let args = {};
      args[`${this.$props.type}_id`] = this.$props.id;
      return args;
    },
    loadComments: function() {
      let apiArgs = this.getArgs();
      helpers.comments.get_comments(apiArgs).then(response => {
        this.comments = response.data;
        return this.comments;
      });
    },
    submitComment: function() {
      let comment = this.comment.trim();
      if (comment.length > 0) {
        helpers.comments.add_comment(
          comment,
          "challenge",
          this.getArgs(),
          () => {
            this.loadComments();
          }
        );
      }
    }
  },
  created() {
    this.loadComments();
  }
};
</script>
