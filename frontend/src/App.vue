<script setup>
import { RouterLink, RouterView } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

const handleLogout = () => {
  authStore.logout();
  // Optionally redirect to the login page
  // router.push('/login'); 
};
</script>

<template>
  <div id="app-container">
    <header class="app-header">
      <div class="logo">
        <RouterLink to="/">听力训练</RouterLink>
      </div>
      <nav class="main-nav">
        <RouterLink to="/">首页</RouterLink>
        <template v-if="!authStore.isAuthenticated">
          <RouterLink to="/login">登录</RouterLink>
          <RouterLink to="/register">注册</RouterLink>
        </template>
        <template v-else>
          <RouterLink to="/courses/create">创建课程</RouterLink>
          <a @click.prevent="handleLogout" href="#">退出登录</a>
        </template>
      </nav>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
#app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f0f2f5;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.logo a {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  text-decoration: none;
}

.main-nav a {
  margin: 0 1rem;
  color: #555;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.main-nav a:hover,
.main-nav a.router-link-exact-active {
  color: #007bff;
}

.app-main {
  flex: 1;
  padding: 2rem;
}
</style>
