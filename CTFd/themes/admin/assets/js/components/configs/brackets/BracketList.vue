<template>
  <div>
    <div class="mb-5" v-for="(bracket, index) in brackets" :key="bracket.id">
      <Bracket
        :index="index"
        :initialBracket.sync="brackets[index]"
        @remove-bracket="removeBracket"
      />
    </div>

    <div class="row">
      <div class="col text-center">
        <button
          class="btn btn-sm btn-success btn-outlined m-auto"
          type="button"
          @click="addBracket()"
        >
          Add New Bracket
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import CTFd from "../../../compat/CTFd";
import Bracket from "./Bracket.vue";

export default {
  name: "BracketList",
  components: {
    Bracket,
  },
  data: function () {
    return {
      brackets: [],
    };
  },
  methods: {
    loadBrackets: function () {
      CTFd.fetch(`/api/v1/brackets`, {
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
          this.brackets = response.data;
        });
    },
    addBracket: function () {
      this.brackets.push({
        id: Math.random(),
        name: "",
        description: "",
        type: null,
      });
    },
    removeBracket: function (index) {
      this.brackets.splice(index, 1);
    },
  },
  created() {
    this.loadBrackets();
  },
};
</script>
