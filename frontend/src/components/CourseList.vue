<template>
  <div class="course-list-container">
    <h1 class="page-title">所有课程</h1>
    
    <!-- 难度筛选器 -->
    <div class="filter-section">
      <label class="filter-label">按难度筛选：</label>
      <select v-model="selectedDifficulty" @change="filterCourses" class="difficulty-filter">
        <option value="all">全部难度</option>
        <option value="easy">简单</option>
        <option value="normal">普通</option>
        <option value="hard">困难</option>
      </select>
    </div>
    
    <div class="course-grid">
      <div v-for="course in filteredCourses" :key="course.id" class="course-card" :class="{ 'completed': course.completed }">
        <div v-if="course.completed" class="completion-badge">
          <span class="completion-icon">✓</span>
          <span class="completion-text">已完成</span>
        </div>
        <router-link :to="`/courses/${course.id}`" class="course-link">
          <h2 class="course-title">{{ course.title }}</h2>
          <p class="course-description">{{ course.description }}</p>
          <div class="course-difficulty">
            <span class="difficulty-label">难度：</span>
            <span :class="['difficulty-badge', course.difficulty]">
              {{ getDifficultyText(course.difficulty) }}
            </span>
          </div>
        </router-link>
        <div v-if="authStore.isAuthenticated && (authStore.isAdmin || course.user_id === authStore.userId)" class="management-actions">
          <router-link :to="`/courses/edit/${course.id}`" class="action-btn edit-btn">编辑</router-link>
          <button @click="showDeleteConfirm(course.id, course.title)" class="action-btn delete-btn">删除</button>
        </div>
      </div>
    </div>
    
    <!-- 自定义确认对话框 -->
    <div v-if="showConfirmDialog" class="confirm-overlay" @click="cancelDelete">
      <div class="confirm-dialog" @click.stop>
        <div class="confirm-header">
          <h3>确认删除</h3>
        </div>
        <div class="confirm-body">
          <p>您确定要删除课程 <strong>"{{ courseToDelete.title }}"</strong> 吗？</p>
          <p class="warning-text">此操作无法撤销！</p>
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
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';

const courses = ref([]);
const selectedDifficulty = ref('all');
const authStore = useAuthStore();
const showConfirmDialog = ref(false);
const courseToDelete = ref({ id: null, title: '' });

// 难度文本映射
const getDifficultyText = (difficulty) => {
  const difficultyMap = {
    'easy': '简单',
    'normal': '普通',
    'hard': '困难'
  };
  return difficultyMap[difficulty] || '未知';
};

// 筛选后的课程列表
const filteredCourses = computed(() => {
  if (selectedDifficulty.value === 'all') {
    return courses.value;
  }
  return courses.value.filter(course => course.difficulty === selectedDifficulty.value);
});

// 筛选函数
const filterCourses = () => {
  // 筛选逻辑已通过computed属性实现
};

const fetchCourses = async () => {
  try {
    const headers = {};
    if (authStore.isAuthenticated) {
      headers['Authorization'] = `Bearer ${authStore.token}`;
    }
    
    const response = await fetch('http://127.0.0.1:5000/api/courses/all', {
      headers
    });
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    courses.value = await response.json();
  } catch (error) {
    console.error('There was a problem with the fetch operation:', error);
  }
};

const showDeleteConfirm = (courseId, courseTitle) => {
  courseToDelete.value = { id: courseId, title: courseTitle };
  showConfirmDialog.value = true;
};

const cancelDelete = () => {
  showConfirmDialog.value = false;
  courseToDelete.value = { id: null, title: '' };
};

const confirmDelete = async () => {
  const courseId = courseToDelete.value.id;
  showConfirmDialog.value = false;
  
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/courses/${courseId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
      },
    });

    if (response.ok) {
      // Remove the course from the list
      courses.value = courses.value.filter(course => course.id !== courseId);
    } else {
      const errorData = await response.json();
      alert(`删除失败: ${errorData.message}`);
    }
  } catch (error) {
    console.error('Error deleting course:', error);
    alert('删除课程时出错。');
  }
  
  courseToDelete.value = { id: null, title: '' };
};

onMounted(async () => {
  await fetchCourses();
  console.log('Auth Store User ID:', authStore.userId);
  courses.value.forEach(course => {
    console.log(`Course: ${course.title}, User ID: ${course.user_id}, Show Buttons: ${authStore.isAuthenticated && course.user_id === authStore.userId}`);
  });
});
</script>

<style scoped>
.page-title {
  color: white !important;
  text-align: center;
  margin-bottom: var(--spacing-xl);
  font-size: var(--font-size-xxl);
  font-weight: 700;
  background: none !important;
  -webkit-background-clip: unset !important;
  -webkit-text-fill-color: white !important;
  background-clip: unset !important;
}

.course-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-xl);
  min-height: 100vh;
  background: var(--gradient-primary);
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-xl);
}

.course-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
  position: relative;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.course-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-xl);
}

.course-link {
  display: block;
  padding: var(--spacing-xl);
  text-decoration: none;
  color: inherit;
}

.course-title {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--primary-color);
  margin: 0 0 var(--spacing-sm) 0;
  transition: color var(--transition-normal);
}

.course-card:hover .course-title {
  color: var(--primary-hover);
}

.course-description {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  line-height: 1.6;
}

.management-actions {
  padding: 0 var(--spacing-xl) var(--spacing-lg);
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  opacity: 0;
  visibility: hidden;
  transition: opacity var(--transition-normal), visibility var(--transition-normal);
}

.course-card:hover .management-actions {
  opacity: 1;
  visibility: visible;
}

.action-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--border-radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
  text-decoration: none;
  display: inline-block;
  text-align: center;
  font-size: var(--font-size-sm);
}

.edit-btn {
  background: var(--warning-color);
  color: var(--text-primary);
}

.edit-btn:hover {
  background: var(--warning-hover);
  transform: translateY(-2px);
}

.delete-btn {
  background: var(--danger-color);
  color: white;
}

.delete-btn:hover {
  background: var(--danger-hover);
  transform: translateY(-2px);
}

/* 自定义确认对话框样式 */
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

.confirm-header {
  background: linear-gradient(135deg, #667eea, #764ba2);
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
  color: #ff6b6b !important;
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
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  color: white;
}

.btn-confirm:hover {
  background: linear-gradient(135deg, #ff5252, #e53935);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}

/* 筛选器样式 */
.filter-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.filter-label {
  font-weight: 600;
  color: white;
  font-size: 1rem;
}

.difficulty-filter {
  padding: 0.5rem 1rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.difficulty-filter:hover {
  border-color: rgba(255, 255, 255, 0.4);
  background: white;
}

.difficulty-filter:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

/* 课程难度标签样式 */
.course-difficulty {
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.difficulty-label {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
}

.difficulty-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.difficulty-badge.easy {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.difficulty-badge.normal {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.difficulty-badge.hard {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

@media (max-width: 768px) {
  .course-list-container {
    padding: var(--spacing-lg);
  }
  
  .course-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }
  
  .course-link {
    padding: var(--spacing-lg);
  }
  
  .filter-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .difficulty-filter {
    width: 100%;
  }
}

/* 已完成课程样式 */
.course-card.completed {
  background: #f0f0f0;
  border-color: #ddd;
}

.completion-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, #4caf50, #45a049);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
  z-index: 10;
}

.completion-icon {
  font-size: 14px;
  font-weight: bold;
}

.completion-text {
  font-size: 11px;
}

.course-card.completed .course-title {
  color: #888;
}

.course-card.completed:hover {
  transform: none;
  box-shadow: var(--shadow-lg);
}
</style>