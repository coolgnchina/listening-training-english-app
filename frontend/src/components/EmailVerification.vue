<template>
  <div class="auth-container">
    <div class="auth-form card">
      <h2 class="page-title">邮箱验证</h2>
      
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在验证您的邮箱...</p>
      </div>
      
      <div v-else-if="verified" class="success-container">
        <div class="success-icon">✓</div>
        <h3>验证成功！</h3>
        <p>您的邮箱已成功验证，现在可以登录了。</p>
        <button @click="goToLogin" class="btn btn-primary">前往登录</button>
      </div>
      
      <div v-else class="error-container">
        <div class="error-icon">✗</div>
        <h3>验证失败</h3>
        <p>{{ errorMessage }}</p>
        <div class="action-buttons">
          <button @click="resendEmail" class="btn btn-secondary" :disabled="resending">{{ resending ? '发送中...' : '重新发送验证邮件' }}</button>
          <button @click="goToLogin" class="btn btn-primary">返回登录</button>
        </div>
      </div>
      
      <div v-if="resendMessage" :class="resendMessageType" class="message">
        {{ resendMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { buildApiUrl } from '@/config/api';

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const verified = ref(false);
const errorMessage = ref('');
const resending = ref(false);
const resendMessage = ref('');
const resendMessageType = ref('');

const verifyEmail = async (token) => {
  try {
        const response = await fetch(buildApiUrl('/verify-email'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    });
    
    const data = await response.json();
    
    if (response.ok) {
      verified.value = true;
    } else {
      errorMessage.value = data.message || '验证失败，请重试。';
    }
  } catch (error) {
    console.error('Email verification error:', error);
    errorMessage.value = '网络错误，请稍后重试。';
  } finally {
    loading.value = false;
  }
};

const resendEmail = async () => {
  const email = prompt('请输入您的邮箱地址：');
  if (!email) return;
  
  resending.value = true;
  resendMessage.value = '';
  
  try {
        const response = await fetch(buildApiUrl('/resend-verification'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });
    
    const data = await response.json();
    
    if (response.ok) {
      resendMessage.value = '验证邮件已重新发送，请检查您的邮箱。';
      resendMessageType.value = 'success';
    } else {
      resendMessage.value = data.message || '发送失败，请重试。';
      resendMessageType.value = 'error';
    }
  } catch (error) {
    console.error('Resend email error:', error);
    resendMessage.value = '网络错误，请稍后重试。';
    resendMessageType.value = 'error';
  } finally {
    resending.value = false;
  }
};

const goToLogin = () => {
  router.push('/login');
};

onMounted(() => {
  const token = route.query.token;
  if (token) {
    verifyEmail(token);
  } else {
    errorMessage.value = '无效的验证链接。';
    loading.value = false;
  }
});
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
  text-align: center;
}

.loading-container {
  padding: var(--spacing-xl) 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto var(--spacing-md);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.success-container, .error-container {
  padding: var(--spacing-xl) 0;
}

.success-icon {
  width: 60px;
  height: 60px;
  background: #27ae60;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  font-weight: bold;
  margin: 0 auto var(--spacing-md);
}

.error-icon {
  width: 60px;
  height: 60px;
  background: #e74c3c;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  font-weight: bold;
  margin: 0 auto var(--spacing-md);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  margin-top: var(--spacing-lg);
}

.action-buttons .btn {
  flex: 1;
  max-width: 150px;
}

.message {
  text-align: center;
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-md);
  border: 1px solid;
}

.message.success {
  background-color: #d4edda;
  border-color: #c3e6cb;
  color: #155724;
}

.message.error {
  background-color: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}

@media (max-width: 768px) {
  .auth-container {
    padding: var(--spacing-md);
  }
  
  .auth-form {
    padding: var(--spacing-xl);
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .btn {
    max-width: none;
  }
}
</style>