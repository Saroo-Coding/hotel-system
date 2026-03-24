import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: () => import("@/views/Dashboard.vue"),
      meta: { public: true },
    },
    {
      path: "/rooms/:id",
      component: () => import("@/views/RoomDetail.vue"),
      meta: { public: true },
    },
    {
      path: "/my-room",
      name: "my-room",
      component: () => import("@/views/BookingPending.vue"),
      meta: { public: true },
    },
    {
      path: "/my-room/:bookingCode",
      name: "my-room-code",
      component: () => import("@/views/BookingPending.vue"),
      meta: { public: true },
    },
    {
      path: "/login",
      component: () => import("@/views/Login.vue"),
      meta: { public: true },
    },
    {
      path: "/register",
      component: () => import("@/views/Register.vue"),
      meta: { public: true },
    },
    {
      path: "/404",
      name: "not-found",
      component: () => import("@/views/NotFound.vue"),
      meta: { public: true },
    },
    {
      path: "/admin",
      meta: { roles: ["ADMIN"] },
      children: [
        // { path: "dashboard", component: () => import("@/pages/admin/Dashboard.vue") },
        // { path: "users", component: () => import("@/pages/admin/Users.vue") },
        // { path: "hotels", component: () => import("@/pages/admin/Hotels.vue") },
        // { path: "hotels/:id", component: () => import("@/pages/admin/HotelDetail.vue") },
        // { path: "rooms", component: () => import("@/pages/admin/Rooms.vue") },
        // { path: "guests", component: () => import("@/pages/admin/Guests.vue") }
      ],
    },
    {
      path: "/staff",
      meta: { roles: ["STAFF"] },
      children: [
        // { path: "dashboard", component: () => import("@/pages/staff/Dashboard.vue") },
        // { path: "check-in", component: () => import("@/pages/staff/CheckIn.vue") },
        // { path: "check-out", component: () => import("@/pages/staff/CheckOut.vue") },
        // { path: "guests", component: () => import("@/pages/staff/Guests.vue") },
        // { path: "rooms", component: () => import("@/pages/staff/Rooms.vue") }
      ],
    },
    {
      path: "/forbidden",
      // component: () => import("@/pages/Forbidden.vue")
    },
    {
      path: "/:pathMatch(.*)*",
      redirect: "/404",
      meta: { public: true },
    },
  ],
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  if (to.path === "/login" && authStore.token) {
    return next("/");
  }

  if (to.meta.public) {
    return next();
  }

  if (!authStore.token) {
    return next("/login");
  }

  if (!authStore.initialized) {
    try {
      await authStore.fetchMe();
    } catch (err) {
      await authStore.logout();
      return next("/login");
    }
  }

  if (to.meta.roles) {
    if (!to.meta.roles.includes(authStore.user.role)) {
      return next("/forbidden");
    }
  }

  next();
});

export default router;
