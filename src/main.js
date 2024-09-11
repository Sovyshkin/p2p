import { createApp } from "vue";
import App from "./App.vue";
import axios from "axios";

axios.defaults.baseURL = "http://45.147.178.123:3000";

createApp(App).mount("#app");
