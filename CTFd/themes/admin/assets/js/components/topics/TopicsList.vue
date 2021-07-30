<template>
  <div class="col-md-12">
    <div id="challenge-topics" class="my-3">
      <h5 class="challenge-tag" v-for="topic in topics" :key="topic.id">
        <span class="mr-1">{{ topic.value }}</span>
        <a class="btn-fa delete-tag" @click="deleteTopic(topic.id)"> &#215;</a>
      </h5>
    </div>

    <div class="form-group">
      <label>
        Topic
        <br />
        <small class="text-muted">Type topic and press Enter</small>
      </label>
      <input
        id="tags-add-input"
        maxlength="255"
        type="text"
        class="form-control"
        v-model="topicValue"
        @keyup.down="moveCursor('down')"
        @keyup.up="moveCursor('up')"
        @keyup.enter="addTopic()"
      />
    </div>

    <div class="form-group">
      <ul class="list-group">
        <li
          :class="{
            'list-group-item': true,
            active: idx + 1 === selectedResultIdx
          }"
          v-for="(topic, idx) in topicResults"
          :key="topic.id"
          @click="selectTopic(idx)"
        >
          {{ topic.value }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import CTFd from "core/CTFd";

export default {
  props: {
    challenge_id: Number
  },
  data: function() {
    return {
      topics: [],
      topicValue: "",
      searchedTopic: "",
      topicResults: [],
      selectedResultIdx: 0,
      awaitingSearch: false
    };
  },
  methods: {
    loadTopics: function() {
      CTFd.fetch(`/api/v1/challenges/${this.$props.challenge_id}/topics`, {
        method: "GET",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        }
      })
        .then(response => {
          return response.json();
        })
        .then(response => {
          if (response.success) {
            this.topics = response.data;
          }
        });
    },
    searchTopics: function() {
      this.selectedResultIdx = 0;
      if (this.topicValue == "") {
        this.topicResults = [];
        return;
      }

      CTFd.fetch(`/api/v1/topics?field=value&q=${this.topicValue}`, {
        method: "GET",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        }
      })
        .then(response => {
          return response.json();
        })
        .then(response => {
          if (response.success) {
            this.topicResults = response.data.slice(0, 10);
          }
        });
    },
    addTopic: function() {
      let value;
      if (this.selectedResultIdx === 0) {
        value = this.topicValue;
      } else {
        let idx = this.selectedResultIdx - 1;
        let topic = this.topicResults[idx];
        value = topic.value;
      }
      const params = {
        value: value,
        challenge: this.$props.challenge_id,
        type: "challenge"
      };

      CTFd.fetch("/api/v1/topics", {
        method: "POST",
        body: JSON.stringify(params)
      })
        .then(response => {
          return response.json();
        })
        .then(response => {
          if (response.success) {
            this.topicValue = "";
            this.loadTopics();
          }
        });
    },
    deleteTopic: function(topic_id) {
      CTFd.fetch(`/api/v1/topics?type=challenge&target_id=${topic_id}`, {
        method: "DELETE"
      })
        .then(response => {
          return response.json();
        })
        .then(response => {
          if (response.success) {
            this.loadTopics();
          }
        });
    },
    moveCursor: function(dir) {
      switch (dir) {
        case "up":
          if (this.selectedResultIdx) {
            this.selectedResultIdx -= 1;
          }
          break;
        case "down":
          if (this.selectedResultIdx < this.topicResults.length) {
            this.selectedResultIdx += 1;
          }
          break;
      }
    },
    selectTopic: function(idx) {
      if (idx === undefined) {
        idx = this.selectedResultIdx;
      }
      let topic = this.topicResults[idx];
      this.topicValue = topic.value;
    }
  },
  watch: {
    topicValue: function(val) {
      if (this.awaitingSearch === false) {
        // 1 second delay after typing
        setTimeout(() => {
          this.searchTopics();
          this.awaitingSearch = false;
        }, 500);
      }
      this.awaitingSearch = true;
    }
  },
  created() {
    this.loadTopics();
  }
};
</script>

<style scoped></style>
