import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'

const routes = [
  { path: '/login', component: Login },
  { path: '/', component: Dashboard }
]

export default createRouter({
  history: createWebHistory(),
  routes
})

// import { createRouter, createWebHistory } from 'vue-router'
// import { useAuthStore } from '@/stores/auth.store'

// const router = createRouter({
//   history: createWebHistory(),
//   routes: [
//     {
//       path: '/login',
//       component: () => import('@/pages/Login.vue'),
//       meta: { public: true }
//     },

//     {
//       path: '/admin',
//       meta: { requiresAuth: true, roles: ['ADMIN'] },
//       children: [
//         { path: 'dashboard', component: () => import('@/pages/admin/Dashboard.vue') },
//         { path: 'users', component: () => import('@/pages/admin/Users.vue') },
//         { path: 'hotels', component: () => import('@/pages/admin/Hotels.vue') },
//         { path: 'hotels/:id', component: () => import('@/pages/admin/HotelDetail.vue') },
//         { path: 'rooms', component: () => import('@/pages/admin/Rooms.vue') },
//         { path: 'guests', component: () => import('@/pages/admin/Guests.vue') }
//       ]
//     },

//     {
//       path: '/staff',
//       meta: { requiresAuth: true, roles: ['STAFF'] },
//       children: [
//         { path: 'dashboard', component: () => import('@/pages/staff/Dashboard.vue') },
//         { path: 'check-in', component: () => import('@/pages/staff/CheckIn.vue') },
//         { path: 'check-out', component: () => import('@/pages/staff/CheckOut.vue') },
//         { path: 'guests', component: () => import('@/pages/staff/Guests.vue') },
//         { path: 'rooms', component: () => import('@/pages/staff/Rooms.vue') }
//       ]
//     },

//     {
//       path: '/forbidden',
//       component: () => import('@/pages/Forbidden.vue')
//     }
//   ]
// })