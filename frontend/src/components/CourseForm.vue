<template>
  <div class="form-container">
    <h1 class="page-title">{{ isEditMode ? '编辑课程' : '创建新课程' }}</h1>
    <form @submit.prevent="submitForm" class="course-form">
      <div class="form-group">
        <label for="title">课程标题</label>
        <input type="text" id="title" v-model="course.title" required placeholder="例如：商务英语听力第一单元">
      </div>
      <div class="form-group">
        <label for="description">课程描述</label>
        <textarea id="description" v-model="course.description" placeholder="简要介绍课程内容"></textarea>
      </div>
      <div class="form-group">
        <label for="audio">音频文件 (MP3)</label>
        <input type="file" id="audio" @change="onAudioFileChange" :required="!isEditMode" accept=".mp3">
        <p v-if="isEditMode && course.audio_filename" class="current-file">当前文件: {{ course.audio_filename }}</p>
      </div>
      <div class="form-group">
        <label for="subtitles">字幕文件 (SRT)</label>
        <input type="file" id="subtitles" @change="onSubtitleFileChange" accept=".srt">
        <p v-if="isEditMode && course.srt_filename" class="current-file">当前文件: {{ course.srt_filename }}</p>
      </div>
      <button type="submit" class="submit-btn">{{ isEditMode ? '更新课程' : '创建课程' }}</button>
    </form>
  </div>
</template>

<style scoped>
.form-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 2rem;
  color: #333;
  text-align: center;
  margin-bottom: 2rem;
}

.course-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #555;
}

.form-group input[type="text"],
.form-group textarea,
.form-group input[type="file"] {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input[type="text"]:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
}

.submit-btn {
  padding: 0.75rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
  align-self: center;
}

.submit-btn:hover {
  background-color: #0056b3;
}
</style>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter, useRoute } from 'vue-router';

const course = ref({ title: '', description: '', audio_filename: '', srt_filename: '' });
const audioFile = ref(null);
const subtitleFile = ref(null);
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

const isEditMode = computed(() => !!route.params.id);

const fetchCourse = async () => {
  if (isEditMode.value) {
    try {
      const response = await fetch(`http://localhost:5000/api/courses/${route.params.id}`);
      if (response.ok) {
        course.value = await response.json();
      } else {
        console.error('Failed to fetch course data');
      }
    } catch (error) {
      console.error('Error fetching course:', error);
    }
  }
};

const onAudioFileChange = (e) => {
  audioFile.value = e.target.files[0];
};

const onSubtitleFileChange = (e) => {
  subtitleFile.value = e.target.files[0];
};

const submitForm = async () => {
  const formData = new FormData();
  formData.append('title', course.value.title);
  formData.append('description', course.value.description);
  if (audioFile.value) {
    formData.append('audio_file', audioFile.value);
  }
  if (subtitleFile.value) {
    formData.append('subtitle_file', subtitleFile.value);
  }

  const url = isEditMode.value ? `http://localhost:5000/api/courses/${route.params.id}` : 'http://localhost:5000/api/courses';
  const method = isEditMode.value ? 'PUT' : 'POST';

  try {
    const response = await fetch(url, {
      method: method,
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
      },
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      router.push(`/courses/${data.course_id}`);
    } else {
      const error = await response.json();
      alert(`操作失败: ${error.message}`);
    }
  } catch (error) {
    console.error('操作课程时出错:', error);
    alert('操作课程时出错');
  }
};

// VIP权限检查
const checkVipPermission = () => {
  if (!authStore.isVip) {
    alert('只有VIP用户才能创建课程');
    router.push('/courses');
    return false;
  }
  return true;
};

onMounted(() => {
  if (!isEditMode.value && !checkVipPermission()) {
    return;
  }
  fetchCourse();
});
</script>