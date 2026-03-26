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
      component: () => import("@/views/admin/Login.vue"),
      meta: { public: true },
    },
    {
      path: "/register",
      component: () => import("@/views/admin/Register.vue"),
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
      redirect: "/admin/dashboard",
      meta: { roles: ["ADMIN", "MANAGER", "STAFF"] },
      children: [
        {
          path: "dashboard",
          component: () => import("@/views/admin/Dashboard.vue"),
          meta: { roles: ["ADMIN", "MANAGER", "STAFF"] },
        },
        {
          path: "hotels",
          component: () => import("@/views/admin/Hotels.vue"),
          meta: { roles: ["ADMIN", "MANAGER"] },
        },
        {
          path: "rooms",
          component: () => import("@/views/admin/Rooms.vue"),
          meta: { roles: ["ADMIN", "MANAGER", "STAFF"] },
        },
        {
          path: "bookings",
          component: () => import("@/views/admin/Bookings.vue"),
          meta: { roles: ["ADMIN", "MANAGER", "STAFF"] },
        },
        {
          path: "guests",
          component: () => import("@/views/admin/Guests.vue"),
          meta: { roles: ["ADMIN", "MANAGER", "STAFF"] },
        },
        {
          path: "users",
          component: () => import("@/views/admin/Users.vue"),
          meta: { roles: ["ADMIN"] },
        },
        {
          path: "reports",
          component: () => import("@/views/admin/Reports.vue"),
          meta: { roles: ["ADMIN", "MANAGER"] },
        },
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
    return next("/admin/dashboard");
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

  // Check role-based access
  if (to.meta.roles) {
    if (!to.meta.roles.includes(authStore.user.role)) {
      return next("/forbidden");
    }
  }

  // Check parent route roles for nested routes
  const matchedRoute = to.matched.find((record) => record.meta.roles);
  if (matchedRoute && matchedRoute.meta.roles) {
    if (!matchedRoute.meta.roles.includes(authStore.user.role)) {
      return next("/forbidden");
    }
  }

  next();
});

export default router;
