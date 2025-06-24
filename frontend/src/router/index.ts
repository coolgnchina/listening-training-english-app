import { createRouter, createWebHistory } from 'vue-router';
import CourseList from '../components/CourseList.vue';
import Login from '../components/Login.vue';
import Register from '../components/Register.vue';
import CourseDetail from '../components/CourseDetail.vue';
import CourseForm from '../components/CourseForm.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
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
  ],
});

export default router
