<script setup>
import { RouterLink, RouterView } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useHeartsStore } from '@/stores/hearts';
import { useErrorHandler } from '@/composables/useErrorHandler';
import ErrorToast from '@/components/ErrorToast.vue';
import { watch, onMounted } from 'vue';

const authStore = useAuthStore();
const heartsStore = useHeartsStore();
const { errorMessage, showError, clearError } = useErrorHandler();

// 监听登录状态变化，自动初始化生命值
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated) {
    heartsStore.fetchHearts();
  } else {
    heartsStore.reset();
  }
}, { immediate: true });

// 组件挂载时初始化
onMounted(() => {
  if (authStore.isAuthenticated) {
    heartsStore.fetchHearts();
  }
});

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
        <RouterLink to="/courses">课程列表</RouterLink>
        <RouterLink v-if="authStore.isAuthenticated && authStore.isVip" to="/courses/create">创建课程</RouterLink>
        <RouterLink v-if="authStore.isAuthenticated && authStore.userId === 1" to="/admin/users">用户管理</RouterLink>
        <template v-if="!authStore.isAuthenticated">
          <RouterLink to="/login">登录</RouterLink>
          <RouterLink to="/register">注册</RouterLink>
        </template>
        <template v-else>
          <RouterLink to="/profile">个人资料</RouterLink>
          <button @click="handleLogout" class="logout-btn">退出登录</button>
        </template>
      </nav>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
    <ErrorToast 
      v-if="showError" 
      :message="errorMessage" 
      @hide="clearError" 
    />
  </div>
</template>

<style scoped>
#app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-lg) var(--spacing-xl);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.logo {
  font-size: var(--font-size-xl);
  font-weight: 800;
}

.logo a {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-decoration: none;
}

.main-nav {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}

.main-nav a,
.logout-btn {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 600;
  transition: all var(--transition-normal);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-md);
  border: none;
  background: none;
  cursor: pointer;
  font-size: var(--font-size-base);
}

.main-nav a:hover,
.main-nav a.router-link-exact-active,
.logout-btn:hover {
  color: var(--primary-color);
  background: rgba(107, 78, 230, 0.1);
  transform: translateY(-2px);
}

.main-content {
  flex: 1;
}

@media (max-width: 768px) {
  .app-header {
    padding: var(--spacing-md);
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .main-nav {
    gap: var(--spacing-md);
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
