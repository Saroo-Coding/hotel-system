import { defineStore } from "pinia";
import { loginApi, logoutApi } from "@/api/auth.api";
import { userApi } from "@/api/user.api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    token: localStorage.getItem("token"),
    initialized: false,
    loading: false,
  }),

  actions: {
    async login(data) {
      try {
        const res = await loginApi(data);

        this.token = res.access_token;
        localStorage.setItem("token", res.access_token);

        await this.fetchMe();
      } catch (err) {
        throw err;
      }
    },

    async fetchMe() {
      if (this.initialized) return;

      this.loading = true;
      try {
        const res = await userApi();
        this.user = res.data;
      } catch (err) {
        this.user = null;
        this.token = null;
        localStorage.removeItem("token");
      } finally {
        this.loading = false;
        this.initialized = true;
      }
    },

    async logout() {
      try {
        await logoutApi();
      } catch (_) {}

      this.user = null;
      this.token = null;
      this.initialized = true;
      localStorage.removeItem("token");
    },
  },
});
