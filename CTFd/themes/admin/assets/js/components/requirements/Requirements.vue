<template>
  <div>
    <table class="table table-striped text-center">
      <thead>
        <tr>
          <td><b>Requirement</b></td>
          <td><b>Settings</b></td>
        </tr>
      </thead>
      <tbody id="challenge-solves-body">
        <tr
          v-for="requirement in requirements.prerequisites"
          :key="requirement"
        >
          <td>{{ getChallengeById(requirement).name }}</td>
          <td>
            <i
              role="button"
              class="btn-fa fas fa-times delete-requirement"
              :challenge-id="requirement"
              @click="removeRequirement(requirement)"
            ></i>
          </td>
        </tr>
      </tbody>
    </table>

    <form @submit.prevent="addRequirement">
      <div class="form-group">
        <select
          class="form-control custom-select"
          name="prerequisite"
          v-model="selectedRequirement"
        >
          <option value=""> -- </option>
          <option
            :value="challenge.id"
            v-for="challenge in otherChallenges"
            :key="challenge.id"
          >
            {{ challenge.name }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <button class="btn btn-success float-right">Add Prerequisite</button>
      </div>
    </form>
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
      challenges: [],
      requirements: {},
      selectedRequirement: null
    };
  },
  computed: {
    // Get all challenges besides the current one and current prereqs
    otherChallenges: function() {
      const prerequisites = this.requirements.prerequisites || [];
      return this.challenges.filter(challenge => {
        return (
          challenge.id !== this.$props.challenge_id &&
          !prerequisites.includes(challenge.id)
        );
      });
    }
  },
  methods: {
    loadChallenges: function() {
      CTFd.fetch("/api/v1/challenges?view=admin", {
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
            this.challenges = response.data;
          }
        });
    },
    getChallengeById: function(challenge_id) {
      return this.challenges.find(challenge => challenge.id === challenge_id);
    },
    loadRequirements: function() {
      CTFd.fetch(
        `/api/v1/challenges/${this.$props.challenge_id}/requirements`,
        {
          method: "GET",
          credentials: "same-origin",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
          }
        }
      )
        .then(response => {
          return response.json();
        })
        .then(response => {
          if (response.success) {
            this.requirements = response.data || {};
          }
        });
    },
    addRequirement: function() {
      let newRequirements = this.requirements.prerequisites
        ? this.requirements.prerequisites
        : [];

      newRequirements.push(this.selectedRequirement);
      this.requirements["prerequisites"] = newRequirements;

      const params = {
        requirements: this.requirements
      };

      CTFd.fetch(`/api/v1/challenges/${this.$props.challenge_id}`, {
        method: "PATCH",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
      })
        .then(response => {
          return response.json();
        })
        .then(data => {
          if (data.success) {
            this.loadRequirements();
          }
        });
    },
    removeRequirement: function(challenge_id) {
      this.requirements.prerequisites = this.requirements.prerequisites.filter(
        val => val !== challenge_id
      );

      const params = {
        requirements: this.requirements
      };

      CTFd.fetch(`/api/v1/challenges/${this.$props.challenge_id}`, {
        method: "PATCH",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
      })
        .then(response => {
          return response.json();
        })
        .then(data => {
          if (data.success) {
            this.loadRequirements();
          }
        });
    }
  },
  created() {
    this.loadChallenges();
    this.loadRequirements();
  }
};
</script>

<style scoped></style>
