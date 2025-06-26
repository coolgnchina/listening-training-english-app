<template>
  <div class="auth-container">
    <div class="auth-form card">
      <h2 class="page-title">登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username" class="form-label">用户名</label>
          <input type="text" id="username" v-model="username" required placeholder="请输入您的用户名" class="form-input">
        </div>
        <div class="form-group">
          <label for="password" class="form-label">密码</label>
          <input type="password" id="password" v-model="password" required placeholder="请输入您的密码" class="form-input">
        </div>
        <button type="submit" class="btn btn-primary submit-btn">登录</button>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  const success = await authStore.login(username.value, password.value);
  if (success) {
    router.push('/'); // Redirect to home page after successful login
  } else {
    errorMessage.value = '用户名或密码无效。';
  }
};
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: var(--spacing-lg);
  background: var(--gradient-primary);
}

.auth-form {
  width: 100%;
  max-width: 450px;
  padding: var(--spacing-2xl);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.submit-btn {
  width: 100%;
  padding: var(--spacing-md);
  font-size: var(--font-size-lg);
  margin-top: var(--spacing-md);
}

.error-message {
  color: var(--danger-color);
  text-align: center;
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm);
  background: rgba(220, 53, 69, 0.1);
  border-radius: var(--border-radius-md);
  border: 1px solid rgba(220, 53, 69, 0.2);
}

@media (max-width: 768px) {
  .auth-container {
    padding: var(--spacing-md);
  }
  
  .auth-form {
    padding: var(--spacing-xl);
  }
}
</style>