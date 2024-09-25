import { createRouter, createWebHistory } from "vue-router";
import AppMain from "@/components/AppMain.vue";
import AppLogin from "@/components/AppLogin.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/main",
      name: "main",
      component: AppMain,
    },
    {
      path: "/login",
      name: "login",
      component: AppLogin,
    },
  ],
});

export default router;
