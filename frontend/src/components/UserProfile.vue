<template>
  <div class="user-profile-container">
    <div class="profile-header">
      <h1 class="page-title">个人资料</h1>
      <div class="user-info-card">
        <div class="user-avatar">
          {{ authStore.username?.charAt(0).toUpperCase() }}
        </div>
        <div class="user-details">
          <h2>{{ authStore.username }}</h2>
          <p class="user-role">{{ authStore.userId === 1 ? '管理员' : '普通用户' }}</p>
          <div class="hearts-display">
            <span v-for="n in heartsStore.maxHearts" :key="n" class="heart">
              {{ n <= heartsStore.currentHearts ? '❤️' : '🤍' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="profile-content">
      <div class="profile-section">
        <h3>修改密码</h3>
        <form @submit.prevent="changePassword" class="password-form">
          <div class="form-group">
            <label for="current-password">当前密码:</label>
            <input 
              type="password" 
              id="current-password" 
              v-model="passwordForm.currentPassword" 
              required 
              class="form-input"
              placeholder="请输入当前密码"
            >
          </div>
          <div class="form-group">
            <label for="new-password">新密码:</label>
            <input 
              type="password" 
              id="new-password" 
              v-model="passwordForm.newPassword" 
              required 
              class="form-input"
              placeholder="请输入新密码"
              minlength="6"
            >
          </div>
          <div class="form-group">
            <label for="confirm-password">确认新密码:</label>
            <input 
              type="password" 
              id="confirm-password" 
              v-model="passwordForm.confirmPassword" 
              required 
              class="form-input"
              placeholder="请再次输入新密码"
              minlength="6"
            >
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              {{ isLoading ? '修改中...' : '修改密码' }}
            </button>
          </div>
        </form>
      </div>

      <div class="profile-section">
        <h3>账户信息</h3>
        <div class="info-grid">
          <div class="info-item">
            <label>用户ID:</label>
            <span>{{ authStore.userId }}</span>
          </div>
          <div class="info-item">
            <label>用户名:</label>
            <span>{{ authStore.username }}</span>
          </div>
          <div class="info-item">
            <label>账户类型:</label>
            <span>{{ authStore.userId === 1 ? '管理员账户' : '普通用户账户' }}</span>
          </div>

        </div>
        
        <div class="profile-section">
          <div class="hearts-section">
            <h3>❤️ 生命值系统</h3>
            <HeartsDisplay />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useHeartsStore } from '@/stores/hearts';
import HeartsDisplay from '@/components/HeartsDisplay.vue';
import { useRouter } from 'vue-router';
import { buildApiUrl } from '@/config/api';

const authStore = useAuthStore();
const heartsStore = useHeartsStore();
const router = useRouter();

const isLoading = ref(false);

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// 修改密码
const changePassword = async () => {
  // 验证新密码和确认密码是否一致
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    alert('新密码和确认密码不一致');
    return;
  }

  // 验证新密码长度
  if (passwordForm.value.newPassword.length < 6) {
    alert('新密码长度至少为6位');
    return;
  }

  isLoading.value = true;

  try {
        const response = await fetch(buildApiUrl('/api/change-password'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
      },
      body: JSON.stringify({
        current_password: passwordForm.value.currentPassword,
        new_password: passwordForm.value.newPassword
      }),
    });

    if (response.ok) {
      alert('密码修改成功');
      // 清空表单
      passwordForm.value = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      };
    } else {
      const errorData = await response.json();
      alert(`密码修改失败: ${errorData.message}`);
    }
  } catch (error) {
    console.error('Error changing password:', error);
    alert('修改密码时出错');
  } finally {
    isLoading.value = false;
  }
};

// 页面加载时获取hearts数据
onMounted(async () => {
  await heartsStore.fetchHearts();
});
</script>

<style scoped>
.hearts-display {
  display: flex;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.heart {
  font-size: 1.5rem;
  color: #ff4d4f;
  transition: transform 0.2s;
}

.heart:hover {
  transform: scale(1.2);
}
.user-profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 2rem;
  text-align: center;
}

.profile-header {
  margin-bottom: 3rem;
}

.user-info-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.user-details h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
  font-weight: 600;
}

.user-role {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.profile-section {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
}

.profile-section h3 {
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1rem;
}

.form-input {
  padding: 0.75rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-actions {
  margin-top: 1rem;
}

.btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.info-grid {
  display: grid;
  gap: 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.info-item label {
  font-weight: 600;
  color: #2c3e50;
}

.info-item span {
  color: #495057;
  font-weight: 500;
}

@media (max-width: 768px) {
  .user-profile-container {
    padding: 1rem;
  }
  
  .user-info-card {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-section {
    padding: 1.5rem;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>