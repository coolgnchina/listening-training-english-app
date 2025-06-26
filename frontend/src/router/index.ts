import { createRouter, createWebHistory } from 'vue-router';
import WelcomeView from '../views/WelcomeView.vue';
import CourseList from '../components/CourseList.vue';
import Login from '../components/Login.vue';
import Register from '../components/Register.vue';
import CourseDetail from '../components/CourseDetail.vue';
import CourseForm from '../components/CourseForm.vue';
import UserManagement from '../components/UserManagement.vue';
import UserProfile from '../components/UserProfile.vue';
import EmailVerification from '../components/EmailVerification.vue';
import { useAuthStore } from '../stores/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: WelcomeView,
    },
    {
      path: '/courses',
      name: 'courses',
      component: CourseList,
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
    },
    {
      path: '/verify-email',
      name: 'verify-email',
      component: EmailVerification,
    },
    {
      path: '/courses/create',
      name: 'create-course',
      component: CourseForm,
    },
    {
      path: '/courses/:id',
      name: 'course-detail',
      component: CourseDetail,
    },
    {
      path: '/courses/edit/:id',
      name: 'edit-course',
      component: CourseForm,
      props: true, // Pass route params as props to the component
    },
    {
      path: '/admin/users',
      name: 'user-management',
      component: UserManagement,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/profile',
      name: 'user-profile',
      component: UserProfile,
      meta: { requiresAuth: true }
    },
  ],
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login');
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    alert('您没有权限访问此页面');
    next(from.path);
  } else {
    next();
  }
});

export default router;
