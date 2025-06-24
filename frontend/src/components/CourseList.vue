<template>
  <div class="course-list-container">
    <h1 class="page-title">所有课程</h1>
    <div class="course-grid">
      <div v-for="course in courses" :key="course.id" class="course-card">
        <router-link :to="`/courses/${course.id}`" class="course-link">
          <h2 class="course-title">{{ course.title }}</h2>
          <p class="course-description">{{ course.description }}</p>
        </router-link>
        <div v-if="authStore.isAuthenticated && course.user_id === authStore.userId" class="management-actions">
          <router-link :to="`/courses/edit/${course.id}`" class="action-btn edit-btn">编辑</router-link>
          <button @click="deleteCourse(course.id)" class="action-btn delete-btn">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';

const courses = ref([]);
const authStore = useAuthStore();

const fetchCourses = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/courses/all');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    courses.value = await response.json();
  } catch (error) {
    console.error('There was a problem with the fetch operation:', error);
  }
};

const deleteCourse = async (courseId) => {
  if (!confirm('您确定要删除这门课程吗？')) {
    return;
  }

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
.course-list-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 2.5rem;
  color: #333;
  text-align: center;
  margin-bottom: 2rem;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.course-card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.course-link {
  display: block;
  padding: 1.5rem;
  text-decoration: none;
  color: inherit;
}

.course-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #007bff;
  margin: 0 0 0.5rem 0;
}

.course-description {
  font-size: 1rem;
  color: #666;
  line-height: 1.6;
}

.management-actions {
  padding: 0 1.5rem 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease, visibility 0.3s ease;
}

.course-card:hover .management-actions {
  opacity: 1;
  visibility: visible;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease, color 0.3s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.edit-btn {
  background-color: #ffc107;
  color: #333;
}

.edit-btn:hover {
  background-color: #e0a800;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
}

.delete-btn:hover {
  background-color: #c82333;
}
</style>