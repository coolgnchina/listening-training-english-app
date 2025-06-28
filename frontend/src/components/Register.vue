<template>
  <div class="auth-container">
    <div class="auth-form card">
      <h2 class="page-title">注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username" class="form-label">用户名</label>
          <input type="text" id="username" v-model="username" required placeholder="请输入您的用户名" class="form-input">
        </div>

        <div class="form-group">
          <label for="password" class="form-label">密码</label>
          <input type="password" id="password" v-model="password" required placeholder="请输入您的密码（至少6位）" class="form-input">
          <div v-if="password && password.length < 6" class="password-hint">密码长度至少为6位</div>
        </div>
        
        <div class="form-group">
          <label for="confirmPassword" class="form-label">确认密码</label>
          <input type="password" id="confirmPassword" v-model="confirmPassword" required placeholder="请再次输入密码" class="form-input">
          <div v-if="confirmPassword && password !== confirmPassword" class="password-hint">两次输入的密码不一致</div>
        </div>

        <button type="submit" class="btn btn-primary submit-btn">注册</button>
        <p v-if="message" :class="messageType" class="message">{{ message }}</p>
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
const confirmPassword = ref('');
const message = ref('');
const messageType = ref('');
const authStore = useAuthStore();
const router = useRouter();

const handleRegister = async () => {
  const auth = useAuthStore();
  const result = await auth.register(username.value, password.value);
  if (result.success) {
    alert('注册成功，请登录');
    router.push('/login');
  } else {
    alert(result.message);
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

.message {
  text-align: center;
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-md);
  border: 1px solid;
}

.message.success {
  color: var(--success-color);
  background: rgba(40, 167, 69, 0.1);
  border-color: rgba(40, 167, 69, 0.2);
}

.message.error {
  color: var(--danger-color);
  background: rgba(220, 53, 69, 0.1);
  border-color: rgba(220, 53, 69, 0.2);
}

/* 验证码样式 */
.captcha-container {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.captcha-input {
  flex: 1;
}

.captcha-image {
  width: 120px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: #f5f5f5;
  transition: all var(--transition-normal);
}

.captcha-image:hover {
  border-color: var(--primary-color);
  background: #f0f0f0;
}

.captcha-image img {
  max-width: 100%;
  max-height: 100%;
  border-radius: var(--border-radius-sm);
}

.captcha-loading {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.btn-refresh {
  background: none;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
  margin-top: var(--spacing-xs);
}

.btn-refresh:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.password-hint {
  color: #e74c3c;
  font-size: 12px;
  margin-top: 5px;
}

@media (max-width: 768px) {
  .auth-container {
    padding: var(--spacing-md);
  }
  
  .auth-form {
    padding: var(--spacing-xl);
  }
  
  .captcha-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .captcha-image {
    width: 100%;
    height: 50px;
  }
}
</style>