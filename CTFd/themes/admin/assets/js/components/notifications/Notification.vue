<template>
  <div class="card bg-light mb-4">
    <button
      type="button"
      :data-notif-id="this.id"
      class="delete-notification close position-absolute p-3"
      style="right:0;"
      data-dismiss="alert"
      aria-label="Close"
      @click="deleteNotification()"
    >
      <span aria-hidden="true">&times;</span>
    </button>
    <div class="card-body">
      <h3 class="card-title">{{ title }}</h3>
      <blockquote class="blockquote mb-0">
        <p v-html="this.content"></p>
        <small class="text-muted">
          <span :data-time="this.date">{{ this.localDate() }}</span>
        </small>
      </blockquote>
    </div>
  </div>
</template>

<script>
import CTFd from "core/CTFd";
import Moment from "moment";
export default {
  props: {
    id: Number,
    title: String,
    content: String,
    date: String
  },
  methods: {
    localDate: function() {
      return Moment(this.date)
        .local()
        .format("MMMM Do, h:mm:ss A");
    },
    deleteNotification: function() {
      if (confirm("Are you sure you want to delete this notification?")) {
        CTFd.api
          .delete_notification({ notificationId: this.id })
          .then(response => {
            if (response.success) {
              // Delete the current component
              // https://stackoverflow.com/a/55384005
              this.$destroy();
              this.$el.parentNode.removeChild(this.$el);
            }
          });
      }
    }
  }
};
</script>
