<template>
  <div class="user-management-container">
    <div class="header-section">
      <h1 class="page-title">用户管理</h1>
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-info">
            <h3>{{ stats.total_users }}</h3>
            <p>总用户数</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📚</div>
          <div class="stat-info">
            <h3>{{ stats.total_courses }}</h3>
            <p>总课程数</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📝</div>
          <div class="stat-info">
            <h3>{{ stats.total_sentences }}</h3>
            <p>总句子数</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <h3>{{ stats.average_courses_per_user }}</h3>
            <p>平均课程/用户</p>
          </div>
        </div>
      </div>
    </div>

    <div class="users-section">
      <div class="section-header">
        <h2>用户列表</h2>
        <button @click="refreshUsers" class="btn btn-secondary refresh-btn">
          🔄 刷新
        </button>
      </div>
      
      <div class="users-grid">
        <div v-for="user in users" :key="user.id" class="user-card">
          <div class="user-header">
            <div class="user-avatar">
              {{ user.username.charAt(0).toUpperCase() }}
            </div>
            <div class="user-info">
              <h3 class="user-name">
                {{ user.username }}
                <span v-if="user.is_admin" class="admin-badge">管理员</span>
                <span v-if="user.is_vip" class="vip-badge">VIP</span>
              </h3>
              <p class="user-stats">创建了 {{ user.created_courses }} 门课程</p>
            </div>
          </div>
          
          <div class="user-actions">
            <button @click="viewUser(user.id)" class="action-btn view-btn">
              👁️ 查看详情
            </button>
            <button 
              v-if="!user.is_admin && authStore.isAdmin" 
              @click="showEditUser(user)" 
              class="action-btn edit-btn"
            >
              ✏️ 编辑
            </button>
            <button 
              v-if="!user.is_admin && authStore.isAdmin" 
              @click="showDeleteConfirm(user.id, user.username)" 
              class="action-btn delete-btn"
            >
              🗑️ 删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户详情模态框 -->
    <div v-if="showUserDetail" class="modal-overlay" @click="closeUserDetail">
      <div class="modal-dialog" @click.stop>
        <div class="modal-header">
          <h3>用户详情</h3>
          <button @click="closeUserDetail" class="close-btn">×</button>
        </div>
        <div class="modal-body" v-if="selectedUser">
          <div class="user-detail-info">
            <div class="detail-item">
              <label>用户名:</label>
              <span>{{ selectedUser.username }}</span>
            </div>
            <div class="detail-item">
              <label>用户ID:</label>
              <span>{{ selectedUser.id }}</span>
            </div>
            <div class="detail-item">
              <label>创建课程数:</label>
              <span>{{ selectedUser.created_courses }}</span>
            </div>
            <div class="detail-item">
              <label>角色:</label>
              <span>{{ selectedUser.is_admin ? '管理员' : '普通用户' }}</span>
            </div>
            <div class="detail-item">
              <label>VIP状态:</label>
              <span :class="selectedUser.is_vip ? 'vip-badge' : 'normal-badge'">
                {{ selectedUser.is_vip ? 'VIP用户' : '普通用户' }}
              </span>
            </div>
          </div>
          
          <div v-if="selectedUser.courses && selectedUser.courses.length > 0" class="user-courses">
            <h4>创建的课程:</h4>
            <div class="course-list">
              <div v-for="course in selectedUser.courses" :key="course.id" class="course-item">
                <router-link :to="`/courses/${course.id}`" class="course-link">
                  {{ course.title }}
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑用户模态框 -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-dialog" @click.stop>
        <div class="modal-header">
          <h3>编辑用户</h3>
          <button @click="closeEditModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="updateUser">
            <div class="form-group">
              <label for="edit-username">用户名:</label>
              <input 
                type="text" 
                id="edit-username" 
                v-model="editForm.username" 
                required 
                class="form-input"
              >
            </div>
            <div class="form-group">
              <label for="edit-password">新密码 (留空则不修改):</label>
              <input 
                type="password" 
                id="edit-password" 
                v-model="editForm.password" 
                class="form-input"
                placeholder="留空则不修改密码"
              >
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="editForm.is_vip" 
                  class="form-checkbox"
                >
                VIP用户
              </label>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeEditModal" class="btn btn-secondary">取消</button>
              <button type="submit" class="btn btn-primary">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="showConfirmDialog" class="confirm-overlay" @click="cancelDelete">
      <div class="confirm-dialog" @click.stop>
        <div class="confirm-header">
          <h3>确认删除用户</h3>
        </div>
        <div class="confirm-body">
          <p>您确定要删除用户 <strong>"{{ userToDelete.username }}"</strong> 吗？</p>
          <p class="warning-text">此操作将同时删除该用户创建的所有课程和相关数据，且无法撤销！</p>
        </div>
        <div class="confirm-actions">
          <button @click="cancelDelete" class="btn-cancel">取消</button>
          <button @click="confirmDelete" class="btn-confirm">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { buildApiUrl } from '@/config/api';

const authStore = useAuthStore();
const router = useRouter();

const users = ref([]);
const stats = ref({
  total_users: 0,
  total_courses: 0,
  total_sentences: 0,
  average_courses_per_user: 0
});

const showUserDetail = ref(false);
const selectedUser = ref(null);
const showEditModal = ref(false);
const editForm = ref({ username: '', password: '', is_vip: false });
const editingUserId = ref(null);
const showConfirmDialog = ref(false);
const userToDelete = ref({ id: null, username: '' });

// 检查权限
const checkPermission = () => {
  if (!authStore.isAdmin) {
    alert('您没有权限访问用户管理页面');
    router.push('/courses');
    return false;
  }
  return true;
};

// 获取用户统计信息
const fetchStats = async () => {
  try {
        const response = await fetch(buildApiUrl('/users/stats'), {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
      },
    });
    
    if (response.ok) {
      stats.value = await response.json();
    }
  } catch (error) {
    console.error('Error fetching stats:', error);
  }
};

// 获取用户列表
const fetchUsers = async () => {
  try {
        const response = await fetch(buildApiUrl('/users'), {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
      },
    });
    
    if (response.ok) {
      users.value = await response.json();
    } else {
      const errorData = await response.json();
      alert(`获取用户列表失败: ${errorData.message}`);
    }
  } catch (error) {
    console.error('Error fetching users:', error);
    alert('获取用户列表时出错');
  }
};

// 查看用户详情
const viewUser = async (userId) => {
  try {
        const response = await fetch(buildApiUrl(`/users/${userId}`), {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
      },
    });
    
    if (response.ok) {
      selectedUser.value = await response.json();
      showUserDetail.value = true;
    } else {
      const errorData = await response.json();
      alert(`获取用户详情失败: ${errorData.message}`);
    }
  } catch (error) {
    console.error('Error fetching user detail:', error);
    alert('获取用户详情时出错');
  }
};

// 显示编辑用户模态框
const showEditUser = (user) => {
  editForm.value = {
    username: user.username,
    password: '',
    is_vip: user.is_vip
  };
  editingUserId.value = user.id;
  showEditModal.value = true;
};

// 更新用户
const updateUser = async () => {
  try {
    const updateData = {
      username: editForm.value.username,
      is_vip: editForm.value.is_vip
    };
    
    if (editForm.value.password) {
      updateData.password = editForm.value.password;
    }
    
        const response = await fetch(buildApiUrl(`/users/${editingUserId.value}`), {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`,
      },
      body: JSON.stringify(updateData),
    });
    
    if (response.ok) {
      alert('用户更新成功');
      closeEditModal();
      await fetchUsers();
    } else {
      const errorData = await response.json();
      alert(`更新用户失败: ${errorData.message}`);
    }
  } catch (error) {
    console.error('Error updating user:', error);
    alert('更新用户时出错');
  }
};

// 显示删除确认对话框
const showDeleteConfirm = (userId, username) => {
  userToDelete.value = { id: userId, username: username };
  showConfirmDialog.value = true;
};

// 确认删除用户
const confirmDelete = async () => {
  const userId = userToDelete.value.id;
  showConfirmDialog.value = false;
  
  try {
        const response = await fetch(buildApiUrl(`/users/${userId}`), {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
      },
    });
    
    if (response.ok) {
      alert('用户删除成功');
      await fetchUsers();
      await fetchStats();
    } else {
      const errorData = await response.json();
      alert(`删除用户失败: ${errorData.message}`);
    }
  } catch (error) {
    console.error('Error deleting user:', error);
    alert('删除用户时出错');
  }
  
  userToDelete.value = { id: null, username: '' };
};

// 取消删除
const cancelDelete = () => {
  showConfirmDialog.value = false;
  userToDelete.value = { id: null, username: '' };
};

// 关闭模态框
const closeUserDetail = () => {
  showUserDetail.value = false;
  selectedUser.value = null;
};

const closeEditModal = () => {
  showEditModal.value = false;
  editForm.value = { username: '', password: '' };
  editingUserId.value = null;
};

// 刷新数据
const refreshUsers = async () => {
  await fetchUsers();
  await fetchStats();
};

// 页面加载时检查权限并获取数据
onMounted(async () => {
  if (checkPermission()) {
    await fetchUsers();
    await fetchStats();
  }
});
</script>

<style scoped>
.user-management-container {
  max-width: 1200px;
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

.header-section {
  margin-bottom: 3rem;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-icon {
  font-size: 2.5rem;
  opacity: 0.9;
}

.stat-info h3 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
}

.stat-info p {
  margin: 0.5rem 0 0 0;
  opacity: 0.9;
  font-size: 0.9rem;
}

.users-section {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  font-size: 1.8rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.user-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.user-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
}

.user-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.admin-badge {
  background: #ff6b6b;
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
}

.user-stats {
  color: #6c757d;
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
}

.user-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.view-btn {
  background: #17a2b8;
  color: white;
}

.view-btn:hover {
  background: #138496;
  transform: translateY(-1px);
}

.edit-btn {
  background: #ffc107;
  color: #212529;
}

.edit-btn:hover {
  background: #e0a800;
  transform: translateY(-1px);
}

.delete-btn {
  background: #dc3545;
  color: white;
}

.delete-btn:hover {
  background: #c82333;
  transform: translateY(-1px);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-dialog {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 2rem;
}

.user-detail-info {
  margin-bottom: 2rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e9ecef;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item label {
  font-weight: 600;
  color: #495057;
}

.detail-item span {
  color: #6c757d;
}

.user-courses h4 {
  color: #495057;
  margin-bottom: 1rem;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.course-item {
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.course-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.course-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

/* 确认对话框样式 */
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.confirm-dialog {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 90%;
  overflow: hidden;
  animation: slideIn 0.3s ease-out;
}

.confirm-header {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  padding: 20px;
  text-align: center;
}

.confirm-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.confirm-body {
  padding: 24px;
  text-align: center;
}

.confirm-body p {
  margin: 0 0 12px 0;
  color: #333;
  line-height: 1.5;
}

.warning-text {
  color: #dc3545 !important;
  font-weight: 500;
  font-size: 0.9rem;
}

.confirm-actions {
  padding: 0 24px 24px 24px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-cancel,
.btn-confirm {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 100px;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.btn-cancel:hover {
  background: #e0e0e0;
  transform: translateY(-1px);
}

.btn-confirm {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
}

.btn-confirm:hover {
  background: linear-gradient(135deg, #c82333, #a71e2a);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

@media (max-width: 768px) {
  .user-management-container {
    padding: 1rem;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .users-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .user-actions {
    justify-content: center;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>