<template>
  <div>
    <div>
      <input type="text">
    </div>
    <div>
      <input type="text">
    </div>
  </div>
</template>

<script>
import $ from "jquery";
import CTFd from "core/CTFd";

export default {
  name: "UserAddForm",
  props: {
    team_id: Number
  },
  data: function() {
    return {
      users: [],
    };
  },
  methods: {
    searchUsers: function() {

    },
    addUsertoTeam: function() {

    }
  }
};
</script>

<style scoped></style>
