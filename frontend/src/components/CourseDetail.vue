<template>
  <div class="course-detail-container">
    <div v-if="course">
      <h1 class="course-title">{{ course.title }}</h1>
      <p class="course-description">{{ course.description }}</p>
      
      <div v-if="course.audio_url" class="audio-player-container">
        <audio ref="audioPlayer" :src="course.audio_url" class="audio-player" @timeupdate="onTimeUpdate"></audio>
        <div class="controls">
          <button @click="togglePlayPause">{{ isPlaying ? '暂停' : '播放' }}</button>
          <select v-model="playbackRate" @change="setPlaybackRate">
            <option v-for="rate in [0.2, 0.5, 0.8, 1.0, 1.2, 1.5]" :key="rate" :value="rate">{{ rate }}x</option>
          </select>
          <label>
            <input type="checkbox" v-model="loop" @change="toggleLoop"> 无限循环
          </label>
        </div>
      </div>
      <div v-else>
        <p>正在加载音频...</p>
      </div>

      <div v-if="sentences.length > 0" class="interactive-section">
        <div class="sentence-display">
          <p>{{ currentSentence.text }}</p>
        </div>
        <div class="word-pool">
          <span v-for="word in shuffledWords" :key="word.id" class="word" draggable="true" @dragstart="onDragStart(word)" @click="selectWord(word)">{{ word.text }}</span>
        </div>
        <div 
          class="judgement-area"
          @dragover.prevent 
          @drop="onDrop"
        >
          <span v-for="word in composedSentence" :key="word.id" class="word" :class="{ 'incorrect': incorrectWords.includes(word.id) }" @click.stop="deselectWord(word)">{{ word.text }}</span>
        </div>
        <button v-if="incorrectWords.length > 0" @click="resetJudgementAreaIfNeeded" class="retry-button">再来一次</button>
        <button @click="showOriginal = !showOriginal">{{ showOriginal ? '隐藏' : '显示' }}原文</button>
        <p v-if="showOriginal">{{ currentSentence.text }}</p>

        <transition name="fade">
          <div v-if="showSuccessMessage" class="success-notification">
            <p>🎉 恭喜您过关！ 🎉</p>
          </div>
        </transition>

        <div class="navigation-controls">
          <button @click="prevSentence" :disabled="currentSentenceIndex === 0">上一关</button>
          <button @click="nextSentence" :disabled="currentSentenceIndex >= sentences.length - 1">下一关</button>
        </div>

        <div class="level-selection">
          <span 
            v-for="(sentence, index) in sentences" 
            :key="index" 
            class="level-number"
            :class="{ 'active-level': index === currentSentenceIndex }"
            @click="goToSentence(index)">
            {{ index + 1 }}
          </span>
        </div>
      </div>

    </div>
    <div v-else>
      <p>正在加载课程详情...</p>
    </div>
  </div>
</template>

<style scoped>
.course-detail-container {
  width: 90%;
  max-width: 1200px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.course-title {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 1rem;
}

.course-description {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.7;
  margin-bottom: 2rem;
}

.audio-player-container {
  margin-top: 2rem;
}

.audio-player {
  width: 100%;
}

.interactive-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}

.sentence-display {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  min-height: 3em;
}

.word-pool, .judgement-area {
  border: 2px dashed #ccc;
  padding: 1rem;
  margin-top: 1rem;
  min-height: 60px;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-content: flex-start;
  border-radius: 8px;
}

.word {
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  user-select: none; /* Prevent text selection */
}

.word:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
}

.word.incorrect {
  background-color: #dc3545; /* A red color to indicate error */
  animation: shake 0.5s;
}

.retry-button {
  padding: 0.5rem 1.5rem;
  font-size: 1rem;
  border: 1px solid #ffc107;
  background-color: #ffc107;
  color: #212529;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  margin: 0 10px;
}

.retry-button:hover {
  background-color: #e0a800;
  border-color: #d39e00;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

[draggable="true"] {
  cursor: grab;
}

[draggable="true"]:active {
  cursor: grabbing;
}

.navigation-controls {
  margin-top: 1.5rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.navigation-controls button {
  padding: 0.5rem 1.5rem;
  font-size: 1rem;
  border: 1px solid #007bff;
  background-color: white;
  color: #007bff;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.navigation-controls button:hover:not(:disabled) {
  background-color: #007bff;
  color: white;
}

.navigation-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.level-selection {
  margin-top: 1.5rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
}

.level-number {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ccc;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.level-number:hover {
  background-color: #f0f0f0;
  border-color: #007bff;
}

.level-number.active-level {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
  font-weight: bold;
}

.success-notification {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(28, 155, 7, 0.9);
  color: white;
  padding: 2rem 4rem;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  z-index: 1000;
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const course = ref({});
const sentences = ref([]);
const currentSentenceIndex = ref(0);
const audioPlayer = ref(null);
const isPlaying = ref(false);
const playbackRate = ref(1.0);
const loop = ref(false);
const shuffledWords = ref([]);
const composedSentence = ref([]);
const showOriginal = ref(false);
const draggedWord = ref(null);
const showSuccessMessage = ref(false);
const incorrectWords = ref([]);



const currentSentence = computed(() => sentences.value[currentSentenceIndex.value] || {});

const fetchCourse = async () => {
  const courseId = route.params.id;
  try {
    const response = await fetch(`http://localhost:5000/api/courses/${courseId}`);
    if (!response.ok) {
      throw new Error('获取课程详情失败');
    }
    const data = await response.json();
    course.value = data;
    if (data.audio_filename) {
      course.value.audio_url = `http://localhost:5000/uploads/${data.audio_filename}`;
    }
    if (data.srt_filename) {
      fetchSentences(courseId);
    }
  } catch (error) {
    console.error('获取课程详情时出错:', error);
  }
};

const fetchSentences = async (courseId) => {
  try {
    const response = await fetch(`http://localhost:5000/api/courses/${courseId}/sentences`);
    if (!response.ok) {
      throw new Error('获取句子失败');
    }
    sentences.value = await response.json();
    prepareCurrentSentence();
    playCurrentSentence();
  } catch (error) {
    console.error('获取句子时出错:', error);
  }
};

const prepareCurrentSentence = () => {
  if (!currentSentence.value || !currentSentence.value.text) return;

  const originalWords = currentSentence.value.text.split(/\s+/).map((w, i) => ({ id: i, text: w, isDistractor: false }));

  // Create a pool of all words from all sentences to pick distractors from
  const allWords = new Set();
  sentences.value.forEach(sentence => {
    sentence.text.split(/\s+/).forEach(word => allWords.add(word));
  });

  const currentSentenceWords = new Set(originalWords.map(w => w.text));
  const distractorPool = [...allWords].filter(word => !currentSentenceWords.has(word));

  const numDistractors = Math.floor(Math.random() * 3) + 1; // 1 to 3 distractors
  const distractors = [];
  for (let i = 0; i < numDistractors && distractorPool.length > 0; i++) {
    const randomIndex = Math.floor(Math.random() * distractorPool.length);
    const distractorText = distractorPool.splice(randomIndex, 1)[0];
    distractors.push({ id: `distractor-${i}`, text: distractorText, isDistractor: true });
  }

  shuffledWords.value = [...originalWords, ...distractors].sort(() => Math.random() - 0.5);
  composedSentence.value = [];
  incorrectWords.value = [];
};

const togglePlayPause = () => {
  if (audioPlayer.value && currentSentence.value) {
    const { currentTime } = audioPlayer.value;
    const { start_time, end_time } = currentSentence.value;

    if (isPlaying.value) {
      audioPlayer.value.pause();
    } else {
      // 如果当前时间不在当前句子范围内，则从头播放
      if (currentTime < start_time || currentTime >= end_time) {
        audioPlayer.value.currentTime = start_time;
      }
      audioPlayer.value.play();
    }
    isPlaying.value = !isPlaying.value;
  }
};

const setPlaybackRate = () => {
  if (audioPlayer.value) {
    audioPlayer.value.playbackRate = playbackRate.value;
  }
};

const toggleLoop = () => {
  if (audioPlayer.value) {
    audioPlayer.value.loop = loop.value;
  }
};

const onTimeUpdate = () => {
  if (!audioPlayer.value || !currentSentence.value) return;
  const { currentTime } = audioPlayer.value;
  const { start_time, end_time } = currentSentence.value;
  if (currentTime >= end_time) {
    if (loop.value) {
      audioPlayer.value.currentTime = start_time;
      audioPlayer.value.play();
    } else {
      isPlaying.value = false;
      audioPlayer.value.pause();
    }
  }
};

const nextSentence = () => {
  if (currentSentenceIndex.value < sentences.value.length - 1) {
    currentSentenceIndex.value++;
    prepareCurrentSentence();
    playCurrentSentence();
  }
};

const prevSentence = () => {
  if (currentSentenceIndex.value > 0) {
    currentSentenceIndex.value--;
    prepareCurrentSentence();
    playCurrentSentence();
  }
};

const goToSentence = (index) => {
  if (index >= 0 && index < sentences.value.length) {
    currentSentenceIndex.value = index;
    prepareCurrentSentence();
    playCurrentSentence();
  }
};

const playCurrentSentence = () => {
  if (audioPlayer.value && currentSentence.value) {
    audioPlayer.value.currentTime = currentSentence.value.start_time;
    audioPlayer.value.play();
    isPlaying.value = true;
  }
};

const onDragStart = (word) => {
  draggedWord.value = word;
};

const onDrop = () => {
  if (draggedWord.value) {
    selectWord(draggedWord.value);
    draggedWord.value = null;
  }
};

const selectWord = (word) => {
  shuffledWords.value = shuffledWords.value.filter(w => w.id !== word.id);
  composedSentence.value.push(word);
  checkCompletion();
};

const deselectWord = (word) => {
  if (incorrectWords.value.length > 0) return;
  composedSentence.value = composedSentence.value.filter(w => w.id !== word.id);
  shuffledWords.value.push(word);
  shuffledWords.value.sort(() => Math.random() - 0.5);
};

const resetJudgementAreaIfNeeded = () => {
  // Return all words from judgement area to the pool
  shuffledWords.value.push(...composedSentence.value);
  composedSentence.value = [];
  shuffledWords.value.sort(() => Math.random() - 0.5);
  incorrectWords.value = [];
};

const checkCompletion = () => {
  if (showSuccessMessage.value) return;

  const userWords = composedSentence.value.filter(w => !w.isDistractor);
  const originalWords = currentSentence.value.text.split(/\s+/);

  if (userWords.length === originalWords.length) {
    const composedText = userWords.map(w => w.text).join(' ');
    if (composedText === currentSentence.value.text) {
      incorrectWords.value = [];
      showSuccessMessage.value = true;
      setTimeout(() => {
        showSuccessMessage.value = false;
        if (currentSentenceIndex.value < sentences.value.length - 1) {
          nextSentence();
        } else {
          // Course finished
        }
      }, 1500);
    } else {
      // Find incorrect words among the non-distractor words
      incorrectWords.value = userWords
        .filter((word, index) => word.text !== originalWords[index])
        .map(word => word.id);
      // Also mark any distractor words in the judgement area as incorrect
      composedSentence.value.forEach(word => {
        if (word.isDistractor) {
          incorrectWords.value.push(word.id);
        }
      });
    }
  } else if (composedSentence.value.length >= originalWords.length) {
    // Handle case where user has dragged distractor words and filled the area
    incorrectWords.value = composedSentence.value
      .filter(word => word.isDistractor || originalWords.indexOf(word.text) === -1)
      .map(word => word.id);
  }
};

onMounted(() => {
  fetchCourse();
});
</script>