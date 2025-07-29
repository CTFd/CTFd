import "./main";
import Vue from "vue";
import EmailAll from "../components/emails/EmailAll.vue";

const selector = document.querySelector("#email-all-view");

// Mount the vue component inside div with id email-all-view
if (selector) {
  const EmailAllComponent = Vue.extend(EmailAll);
  const vueContainer = document.createElement("div");
  selector.appendChild(vueContainer);
  new EmailAllComponent().$mount(vueContainer);
}
