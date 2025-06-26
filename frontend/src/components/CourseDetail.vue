<template>
  <div class="course-detail-container">
    <div v-if="course">
      <div class="course-header">
        <h1 class="course-title">{{ course.title }}</h1>
        <div class="course-difficulty">
          <span class="difficulty-label">难度：</span>
          <span :class="['difficulty-badge', course.difficulty]">
            {{ getDifficultyText(course.difficulty) }}
          </span>
        </div>
        <div class="course-controls">
          <div class="practice-mode-toggle">
            <label class="switch">
              <input type="checkbox" v-model="isPracticeMode">
              <span class="slider round"></span>
            </label>
            <span class="practice-mode-label">练习模式</span>
          </div>
        </div>
    </div>
    
    <!-- 固定位置的生命值显示 -->
    <div class="fixed-hearts-container">
      <HeartsDisplay />
    </div>
    
    <div v-if="course">
      </div>
      
      <!-- 消息提醒组件 -->
      <transition name="notification">
        <div v-if="showNotification" :class="['notification-message', notificationType]">
          <div class="notification-content">
            <span class="notification-icon">
              <span v-if="notificationType === 'info'">ℹ️</span>
              <span v-else-if="notificationType === 'success'">✅</span>
              <span v-else-if="notificationType === 'warning'">⚠️</span>
              <span v-else-if="notificationType === 'error'">❌</span>
            </span>
            <span class="notification-text">{{ notificationMessage }}</span>
          </div>
        </div>
      </transition>
      
      <p class="course-description">{{ course.description }}</p>
      

      <!-- 答题区域 - 移到最前面 -->
      <div v-if="sentences.length > 0" class="interactive-section priority-section">
        <div class="sentence-display">
          <p v-if="showOriginal">{{ currentSentence.text }}</p>
          <p v-else style="height: 1.2em;">&nbsp;</p> <!-- Placeholder to maintain layout -->
        </div>
        <div class="game-area-container">
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
          
          <!-- 生命值不足遮罩层 -->
          <div v-if="!canStartGame" class="hearts-overlay">
            <div class="overlay-content">
              <h3>❤️ 生命值不足</h3>
              <p>您的生命值已用完，无法进行挑战模式</p>
              <p>请开启练习模式继续学习</p>
              <button @click="togglePracticeMode" class="practice-btn">开启练习模式</button>
              <div class="recovery-info">
                <span>下次恢复: {{ heartsStore.recoveryCountdown }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 音频播放器 - 移动到判断区下方 -->
        <div v-if="course.audio_url" class="audio-player-container inline-audio" :class="{ disabled: !canStartGame }">
          <audio ref="audioPlayer" :src="course.audio_url" class="audio-player" @timeupdate="onTimeUpdate"></audio>
          <div class="controls">
            <button @click="togglePlayPause" class="styled-button" :disabled="!canStartGame">{{ isPlaying ? '暂停' : '播放' }}</button>
            <select v-model="playbackRate" @change="setPlaybackRate">
              <option v-for="rate in [0.2, 0.5, 0.8, 1.0, 1.2, 1.5]" :key="rate" :value="rate">{{ rate }}x</option>
            </select>
            <label>
              <input type="checkbox" v-model="loop" @change="toggleLoop"> 无限循环
            </label>
          </div>
        </div>
        <div v-else class="audio-loading">
          <p>正在加载音频...</p>
        </div>
        
        <div class="original-text-section">
          <button 
            @click="viewOriginalText"
            :disabled="!canViewOriginal"
            :class="['original-text-btn', { 'disabled': !canViewOriginal }]"
            :title="originalViewHint"
          >
            {{ originalViewHint }}
          </button>
          <div v-if="!isPracticeMode" class="view-info">
            <span class="view-count">本关已查看: {{ originalViewCount[currentSentenceIndex] || 0 }}/{{ maxOriginalViews }}</span>
          </div>
        </div>

        <transition name="fade">
          <div v-if="showSuccessMessage" class="success-notification">
            <p>🎉 恭喜您过关！ 🎉</p>
          </div>
        </transition>
        
        <!-- 课程完成提示 -->
        <transition name="fade">
          <div v-if="showCourseCompletionMessage" class="course-completion-notification">
            <div class="completion-content">
              <div class="completion-icon">🏆</div>
              <h2>恭喜！您已完成所有关卡</h2>
              <p>课程已标记为完成</p>
              <div class="completion-decoration">
                <span>🎉</span>
                <span>✨</span>
                <span>🎊</span>
              </div>
            </div>
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
            :class="{ 'active-level': index === currentSentenceIndex, 'completed': completedLevels.includes(index) }"
            @click="goToSentence(index)">
            {{ index + 1 }}
          </span>
        </div>
      </div>

      
      <!-- 游戏规则说明 -->
      <div class="game-rules-section">
        <div class="rules-header">
          <h2>🎮 游戏规则</h2>
          <button @click="toggleRulesVisibility" class="toggle-rules-btn">
            {{ showRules ? '收起规则' : '查看规则' }}
          </button>
        </div>
        
        <div v-show="showRules" class="rules-content">
          <div class="rules-grid">
            <div class="rule-card hearts-rule">
              <div class="rule-icon">❤️</div>
              <h3>生命值系统</h3>
              <ul>
                <li>每位用户拥有 <strong>5颗生命值</strong></li>
                <li>答错题目会扣除1点生命值</li>
                <li>生命值每小时自动恢复1颗</li>
                <li>新手享有 <strong>3次保护</strong>，答错不扣心</li>
              </ul>
            </div>
            
            <div class="rule-card gameplay-rule">
              <div class="rule-icon">🎯</div>
              <h3>游戏玩法</h3>
              <ul>
                <li>听音频，将单词拖拽组成正确句子</li>
                <li>注意干扰词，不要被误导</li>
                <li>完成所有句子即可通关课程</li>
                <li>支持调节播放速度和循环播放</li>
                <li><strong>查看原文</strong>：需先尝试答题，每关限2次，消耗1❤️</li>
              </ul>
            </div>
            
            <div class="rule-card difficulty-rule">
              <div class="rule-icon">⚡</div>
              <h3>难度机制</h3>
              <ul>
                <li><span class="easy">简单</span>：答错扣除0.5颗心</li>
                <li><span class="normal">普通</span>：答错扣除1颗心</li>
                <li><span class="hard">困难</span>：答错扣除1.5颗心</li>
                <li>难度越高，挑战越大</li>
              </ul>
            </div>
            
            <div class="rule-card reward-rule">
              <div class="rule-icon">🏆</div>
              <h3>奖励系统</h3>
              <ul>
                <li>连续答对 <strong>10题</strong> 奖励1颗心</li>
                <li>完美通关课程奖励 <strong>2颗额外心</strong></li>
                <li>练习模式不消耗生命值</li>
                <li>鼓励持续学习和挑战</li>
              </ul>
            </div>
          </div>
          
          <div class="practice-mode-info">
            <div class="practice-icon">🎓</div>
            <div class="practice-text">
              <h4>练习模式</h4>
              <p>开启练习模式可以无限制地学习，不会消耗生命值，适合反复练习和巩固知识。</p>
            </div>
          </div>
        </div>
      </div>
      


      <div v-if="course.audio_url" class="audio-player-container" :class="{ disabled: !canStartGame }">
        <audio ref="audioPlayer" :src="course.audio_url" class="audio-player" @timeupdate="onTimeUpdate"></audio>
        <div class="controls">
          <button @click="togglePlayPause" class="styled-button" :disabled="!canStartGame">{{ isPlaying ? '暂停' : '播放' }}</button>
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
  margin: 0.5rem auto;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
}

.course-detail-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  z-index: 1;
}

.course-detail-container > * {
  position: relative;
  z-index: 2;
}

.course-title {
  font-size: 2.2rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
  font-weight: 700;
  text-align: center;
  letter-spacing: -0.02em;
}

.course-difficulty {
  text-align: center;
  margin-bottom: 1rem;
}

.difficulty-label {
  font-size: 1rem;
  color: #666;
  margin-right: 0.5rem;
}

.difficulty-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.difficulty-badge.easy {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.difficulty-badge.normal {
  background: linear-gradient(135deg, #FF9800, #f57c00);
  color: white;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}

.difficulty-badge.hard {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
}

.course-description {
  font-size: 1rem;
  color: #555;
  line-height: 1.4;
  margin-bottom: 1rem;
  text-align: center;
  font-weight: 400;
}

.audio-player-container {
  margin-top: 2rem;
  background: rgba(255, 255, 255, 0.8);
  padding: 1.5rem;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

/* 内联音频播放器样式 - 居左排列 */
.inline-audio {
  margin: 1rem 0;
  padding: 1rem;
  background: rgba(240, 248, 255, 0.9);
  border-radius: 10px;
  border-left: 4px solid #4CAF50;
  text-align: left;
}

.inline-audio .controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.audio-loading {
  margin: 1rem 0;
  padding: 0.5rem;
  text-align: left;
  color: #666;
  font-style: italic;
}

.audio-player {
  width: 100%;
}

.interactive-section {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.sentence-display {
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 1rem;
  min-height: 2.5em;
  text-align: center;
  color: #333;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.word-pool, .judgement-area {
  border: 2px dashed rgba(102, 126, 234, 0.3);
  padding: 1.5rem;
  min-height: 80px;
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  align-content: flex-start;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(5px);
  transition: all 0.3s ease;
}

.word-pool {
  margin-top: calc(1.5rem - 50px);
  height: 160px;
  overflow-y: auto;
}

.judgement-area {
  margin-top: calc(1.5rem - 50px + 30px);
  height: 120px;
  overflow-y: auto;
}

.word-pool:hover, .judgement-area:hover {
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(255, 255, 255, 0.7);
}

.word {
  padding: 0.7rem 1.2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  font-weight: 500;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  border: none;
}

.word:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%);
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.styled-button {
  padding: 0.7rem 1.5rem;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  border: none;
  font-size: 1rem;
  font-weight: 500;
  margin: 0 8px;
  box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
}

.styled-button:hover {
  background: linear-gradient(135deg, #e91e63 0%, #f093fb 100%);
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(245, 87, 108, 0.4);
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
  margin-top: 2rem;
  display: flex;
  justify-content: center;
  gap: 1.5rem;
}

.navigation-controls button {
  padding: 0.8rem 2rem;
  font-size: 1rem;
  border: 2px solid transparent;
  background: linear-gradient(white, white) padding-box, linear-gradient(135deg, #667eea, #764ba2) border-box;
  color: #667eea;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
}

.navigation-controls button:hover:not(:disabled) {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.navigation-controls button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.level-selection {
  margin-top: 2rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.8rem;
}

.level-number {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  color: #667eea;
}

.level-number:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
  transform: scale(1.1);
}

.level-number.active-level {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-color: transparent;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.level-number.completed {
  background-color: #a9a9a9; /* DarkGray */
  color: #fff;
}



.success-notification {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  padding: 2.5rem 4rem;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(79, 172, 254, 0.3);
  z-index: 1000;
  font-size: 1.8rem;
  font-weight: 600;
  text-align: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 课程完成提示 */
.course-completion-notification {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3rem 4rem;
  border-radius: 25px;
  box-shadow: 0 25px 50px rgba(102, 126, 234, 0.4);
  z-index: 1001;
  text-align: center;
  backdrop-filter: blur(15px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  min-width: 400px;
  max-width: 500px;
}

.completion-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.completion-icon {
  font-size: 4rem;
  margin-bottom: 0.5rem;
  animation: bounce 2s infinite;
}

.completion-content h2 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.completion-content p {
  margin: 0;
  font-size: 1.2rem;
  opacity: 0.9;
  font-weight: 500;
}

.completion-decoration {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.completion-decoration span {
  font-size: 1.5rem;
  animation: sparkle 1.5s infinite alternate;
}

.completion-decoration span:nth-child(2) {
  animation-delay: 0.3s;
}

.completion-decoration span:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

@keyframes sparkle {
  0% {
    transform: scale(1) rotate(0deg);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.2) rotate(180deg);
    opacity: 1;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 课程头部样式 */
.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.course-controls {
  display: flex;
  align-items: center;
  gap: 2rem;
}

/* 练习模式切换开关 */
.practice-mode-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 34px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #667eea;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.practice-mode-label {
  font-size: 0.9rem;
  color: #667eea;
  font-weight: 500;
}

/* 游戏区域容器 */
.game-area-container {
  position: relative;
}

/* 生命值不足遮罩层 */
.hearts-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  border-radius: 15px;
  backdrop-filter: blur(5px);
}

.overlay-content {
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  color: white;
  padding: 2rem;
  border-radius: 15px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3);
  max-width: 400px;
  width: 90%;
}

.overlay-content h3 {
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
}

.overlay-content p {
  margin: 0 0 1rem 0;
  opacity: 0.9;
}

.overlay-content .practice-btn {
  background: white;
  color: #ff6b6b;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 1rem 0;
}

.overlay-content .practice-btn:hover {
  background: #f0f0f0;
  transform: translateY(-2px);
}

.overlay-content .recovery-info {
  margin-top: 1rem;
  font-size: 0.9rem;
  opacity: 0.8;
}

.practice-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid white;
  padding: 0.8rem 1.5rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.practice-btn:hover {
  background: white;
  color: #ff6b6b;
}

.recovery-info {
  font-size: 0.9rem;
  opacity: 0.8;
}

/* 禁用状态 */
.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.disabled button {
  cursor: not-allowed;
}

/* 显示原文区域样式 */
.original-text-section {
  margin: 1.5rem 0;
  text-align: center;
}

.original-text-btn {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  color: #333;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 154, 158, 0.3);
  min-width: 200px;
  position: relative;
}

.original-text-btn:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 154, 158, 0.4);
}

.original-text-btn.disabled {
  background: #e0e0e0;
  color: #999;
  cursor: not-allowed;
  box-shadow: none;
}

.view-info {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #666;
}

.view-count {
  background: rgba(255, 255, 255, 0.8);
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  border: 1px solid #ddd;
  display: inline-block;
}

/* 游戏规则样式 */
.game-rules-section {
  margin: 2rem 0;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid #e1e8f0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.rules-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.rules-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
  font-weight: 600;
}

.toggle-rules-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.toggle-rules-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.rules-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.rules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.rule-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border-left: 4px solid;
}

.rule-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.hearts-rule {
  border-left-color: #ff6b6b;
}

.gameplay-rule {
  border-left-color: #4ecdc4;
}

.difficulty-rule {
  border-left-color: #ffe66d;
}

.reward-rule {
  border-left-color: #a8e6cf;
}

.rule-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  display: block;
}

.rule-card h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 600;
}

.rule-card ul {
  margin: 0;
  padding-left: 1.2rem;
  list-style: none;
}

.rule-card li {
  margin-bottom: 0.5rem;
  color: #555;
  line-height: 1.5;
  position: relative;
}

.rule-card li::before {
  content: '•';
  color: #667eea;
  font-weight: bold;
  position: absolute;
  left: -1rem;
}

.rule-card strong {
  color: #2c3e50;
  font-weight: 600;
}

.difficulty-rule .easy {
  background: #d4edda;
  color: #155724;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.difficulty-rule .normal {
  background: #fff3cd;
  color: #856404;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.difficulty-rule .hard {
  background: #f8d7da;
  color: #721c24;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.practice-mode-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.practice-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.practice-text h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.practice-text p {
  margin: 0;
  opacity: 0.9;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .course-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .course-controls {
    justify-content: space-between;
  }
  
  .warning-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .rules-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .rules-grid {
    grid-template-columns: 1fr;
  }
  
  .practice-mode-info {
    flex-direction: column;
    text-align: center;
  }
  
  /* 小屏幕上调整固定生命值位置 */
  .fixed-hearts-container {
    top: 10px;
    right: 10px;
    padding: 6px 8px;
    transform: scale(0.9);
  }
}

/* 优先显示的答题区域样式 */
.priority-section {
  background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%);
  border: 2px solid #4a90e2;
  border-radius: 16px;
  padding: 20px;
  margin: 10px 0;
  box-shadow: 0 8px 24px rgba(74, 144, 226, 0.15);
  position: relative;
}

.priority-section::before {
  content: '🎯 答题区域';
  position: absolute;
  top: -12px;
  left: 20px;
  background: #4a90e2;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

/* 固定位置的生命值显示 */
.fixed-hearts-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 999;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 8px 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 消息提醒组件样式 */
.notification-message {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  max-width: 400px;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-weight: 500;
  font-size: 14px;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.notification-icon {
  font-size: 16px;
}

.notification-text {
  flex: 1;
}

/* 不同类型的消息样式 */
.notification-message.info {
  background-color: #e3f2fd;
  color: #1976d2;
  border-left: 4px solid #2196f3;
}

.notification-message.success {
  background-color: #e8f5e8;
  color: #2e7d32;
  border-left: 4px solid #4caf50;
}

.notification-message.warning {
  background-color: #fff3e0;
  color: #f57c00;
  border-left: 4px solid #ff9800;
}

.notification-message.error {
  background-color: #ffebee;
  color: #d32f2f;
  border-left: 4px solid #f44336;
}

/* 过渡动画 */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

</style>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '@/stores/auth';
import { useHeartsStore } from '@/stores/hearts';
import HeartsDisplay from '@/components/HeartsDisplay.vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const heartsStore = useHeartsStore();

// 练习模式状态
const isPracticeMode = ref(false);
const perfectCourse = ref(true);
// 游戏规则显示状态
const showRules = ref(false);
const course = ref(null);
const sentences = ref([]);
const currentSentenceIndex = ref(0);
const audioPlayer = ref(null);
const isPlaying = ref(false);
const playbackRate = ref(1.0);
const loop = ref(false);
const showOriginal = ref(false);
const shuffledWords = ref([]);
const composedSentence = ref([]);
const draggedWord = ref(null);
const incorrectWords = ref([]);
const showSuccessMessage = ref(false);
const showCourseCompletionMessage = ref(false);
const completedLevels = ref([]);

// 显示原文相关状态
const originalViewCount = ref({}); // 记录每关查看原文的次数
const hasAttempted = ref({}); // 记录每关是否已尝试答题
const showOriginalCost = 1; // 查看原文消耗的生命值
const maxOriginalViews = 2; // 每关最多查看原文次数

// 消息提醒相关状态
const notificationMessage = ref('');
const showNotification = ref(false);
const notificationType = ref('info'); // 'info', 'success', 'warning', 'error'

const courseId = route.params.id;

// 页面加载时获取课程详情和完成状态
onMounted(async () => {
  await fetchCourseDetails();
  await fetchCompletedLevels();
});

const fetchCourseDetails = async () => {
  try {
    // 获取课程基本信息（不需要认证）
    const courseResponse = await axios.get(`http://localhost:5000/api/courses/${courseId}`);
    course.value = courseResponse.data;
    console.log('Course data loaded:', course.value);
    
    if (courseResponse.data.audio_filename) {
        course.value.audio_url = `http://localhost:5000/uploads/${courseResponse.data.audio_filename}`;
    }
    
    // 获取句子数据（不需要认证）
    const sentencesResponse = await axios.get(`http://localhost:5000/api/courses/${courseId}/sentences`);
    sentences.value = sentencesResponse.data.map(s => ({ ...s, id: s.id || Math.random() }));
    console.log('Sentences data loaded:', sentences.value.length, 'sentences');
    
    if (sentences.value.length > 0) {
      prepareCurrentSentence();
      playCurrentSentence();
    } else {
      console.warn('No sentences found for course', courseId);
    }
  } catch (error) {
    console.error('Failed to fetch course details:', error);
    console.error('Error details:', error.response?.data || error.message);
  }
};

const fetchCompletedLevels = async () => {
  try {
    const token = localStorage.getItem('token');
    // 如果没有token，说明用户未登录，不需要获取完成状态
    if (!token) {
      completedLevels.value = [];
      return;
    }
    
    const response = await axios.get(`http://localhost:5000/api/courses/${courseId}/levels/completed`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    completedLevels.value = response.data;
  } catch (error) {
    console.error('Failed to fetch completed levels:', error);
    // 如果获取失败，设置为空数组
    completedLevels.value = [];
  }
};

const markLevelAsComplete = async (levelIndex) => {
  if (completedLevels.value.includes(levelIndex)) return;
  try {
    const token = localStorage.getItem('token');
    await axios.post(`http://localhost:5000/api/courses/${courseId}/levels/${levelIndex}/complete`, {}, {
      headers: { Authorization: `Bearer ${token}` },
    });
    completedLevels.value.push(levelIndex);
  } catch (error) {
    console.error(`Failed to mark level ${levelIndex} as complete:`, error);
  }
};

const markCourseAsFullyCompleted = async () => {
  try {
    const token = localStorage.getItem('token');
    await axios.post(`http://localhost:5000/api/courses/${courseId}/complete`, {}, {
      headers: { Authorization: `Bearer ${token}` },
    });
    showCourseCompletionMessage.value = true;
    setTimeout(() => {
      showCourseCompletionMessage.value = false;
      router.push('/courses');
    }, 3000);
  } catch (error) {
    console.error('Failed to mark course as fully completed:', error);
  }
};

// 切换练习模式
const togglePracticeMode = () => {
  isPracticeMode.value = !isPracticeMode.value;
};

// 切换游戏规则显示
const toggleRulesVisibility = () => {
  showRules.value = !showRules.value;
};

// 显示消息提醒
const showMessage = (message, type = 'info', duration = 3000) => {
  notificationMessage.value = message;
  notificationType.value = type;
  showNotification.value = true;
  
  setTimeout(() => {
    showNotification.value = false;
  }, duration);
};

// 查看原文方法
const viewOriginalText = async () => {
  const currentLevel = currentSentenceIndex.value;
  
  // 练习模式下直接显示
  if (isPracticeMode.value) {
    showOriginal.value = true;
    return;
  }
  
  // 检查是否可以查看
  if (!canViewOriginal.value) {
    return;
  }
  
  try {
    // 扣除生命值
    await heartsStore.loseHeart('view_original');
    
    // 增加查看次数
    if (!originalViewCount.value[currentLevel]) {
      originalViewCount.value[currentLevel] = 0;
    }
    originalViewCount.value[currentLevel]++;
    
    // 显示原文
    showOriginal.value = true;
    
    // 3秒后自动隐藏
    setTimeout(() => {
      showOriginal.value = false;
    }, 3000);
    
  } catch (error) {
    console.error('查看原文失败:', error);
  }
};

// 记录用户已尝试答题
const markAsAttempted = () => {
  const currentLevel = currentSentenceIndex.value;
  hasAttempted.value[currentLevel] = true;
};

// 获取难度显示文本
const getDifficultyText = (difficulty) => {
  const difficultyMap = {
    'easy': '简单',
    'normal': '普通',
    'hard': '困难'
  };
  return difficultyMap[difficulty] || '未知';
};

// 检查是否可以开始游戏
const canStartGame = computed(() => {
  return isPracticeMode.value || heartsStore.canPlay;
});

// 检查是否可以查看原文
const canViewOriginal = computed(() => {
  const currentLevel = currentSentenceIndex.value;
  const viewCount = originalViewCount.value[currentLevel] || 0;
  const attempted = hasAttempted.value[currentLevel] || false;
  
  // 练习模式下无限制
  if (isPracticeMode.value) return true;
  
  // 正常模式下需要满足条件：已尝试答题 && 查看次数未超限 && 有足够生命值
  return attempted && viewCount < maxOriginalViews && heartsStore.canPlay;
});

// 获取查看原文的提示信息
const originalViewHint = computed(() => {
  const currentLevel = currentSentenceIndex.value;
  const viewCount = originalViewCount.value[currentLevel] || 0;
  const attempted = hasAttempted.value[currentLevel] || false;
  
  if (isPracticeMode.value) {
    return '练习模式：无限制查看';
  }
  
  if (!attempted) {
    return '请先尝试答题后再查看原文';
  }
  
  if (!heartsStore.canPlay) {
    return '生命值不足，无法查看原文';
  }
  
  const remainingViews = maxOriginalViews - viewCount;
  if (remainingViews <= 0) {
    return '本关查看次数已用完';
  }
  
  return `查看原文 (剩余${remainingViews}次，消耗${showOriginalCost}❤️)`;
});

onMounted(async () => {
  await fetchCourseDetails();
  await fetchCompletedLevels();
  // 初始化hearts store
  await heartsStore.fetchHearts();
  // 重新进入课程时重置连续答对计数器
  await heartsStore.resetConsecutiveCorrect();
});

const currentSentence = computed(() => {
  return sentences.value[currentSentenceIndex.value] || {};
});

watch(currentSentenceIndex, () => {
  if (audioPlayer.value) {
    audioPlayer.value.pause();
    isPlaying.value = false;
  }
  prepareCurrentSentence();
  playCurrentSentence();
});

const prepareCurrentSentence = () => {
  if (!currentSentence.value || !currentSentence.value.text) return;

  const clean = (text) => text.replace(/[.,?]/g, '');
  const originalWords = currentSentence.value.text.split(/\s+/).filter(w => w).map((word, index) => ({
    id: `word-${index}`,
    text: clean(word),
    isDistractor: false
  }));

  const allOtherWords = sentences.value
    .filter((_, index) => index !== currentSentenceIndex.value)
    .flatMap(s => s.text.split(/\s+/).filter(w => w).map(w => clean(w)));

  const distractors = [];
  // 随机生成1-3个干扰词
  const numDistractors = Math.min(Math.floor(Math.random() * 3) + 1, allOtherWords.length);
  while (distractors.length < numDistractors && allOtherWords.length > 0) {
    const randomIndex = Math.floor(Math.random() * allOtherWords.length);
    const randomWord = allOtherWords.splice(randomIndex, 1)[0];
    if (!originalWords.some(w => w.text === randomWord) && !distractors.some(d => d.text === randomWord)) {
      distractors.push({ id: `distractor-${distractors.length}`, text: randomWord, isDistractor: true });
    }
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
  if (currentTime >= end_time + 0.2) { 
    if (loop.value) {
      audioPlayer.value.currentTime = start_time;
      audioPlayer.value.play();
    } else {
      isPlaying.value = false;
      audioPlayer.value.pause();
      audioPlayer.value.currentTime = start_time;
    }
  }
};

const nextSentence = () => {
  if (currentSentenceIndex.value < sentences.value.length - 1) {
    currentSentenceIndex.value++;
  }
};

const prevSentence = () => {
  if (currentSentenceIndex.value > 0) {
    currentSentenceIndex.value--;
  }
};

const goToSentence = (index) => {
  if (index >= 0 && index < sentences.value.length) {
    currentSentenceIndex.value = index;
  }
};

const playCurrentSentence = () => {
  if (audioPlayer.value && currentSentence.value && currentSentence.value.start_time !== undefined) {
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

// 实时检查当前选择的词语是否正确
const checkCurrentWordCorrectness = async (selectedWord) => {
  const clean = (text) => text.replace(/[.,?]/g, '');
  const originalWords = currentSentence.value.text.split(/\s+/).filter(w => w).map(w => clean(w));
  const currentPosition = composedSentence.value.length - 1; // 当前选择词语的位置
  
  // 检查是否选择了干扰词
  if (selectedWord.isDistractor) {
    perfectCourse.value = false;
    incorrectWords.value.push(selectedWord.id);
    
    try {
      const difficulty = course.value?.difficulty || 'normal';
      const result = await heartsStore.loseHeart(difficulty, { isPracticeMode: isPracticeMode.value });
      
      if (result && result.message) {
        if (result.message.includes('新手保护')) {
          showMessage(result.message, 'success');
        } else if (result.message.includes('练习模式')) {
          showMessage(result.message, 'info');
        } else if (result.hearts_lost > 0) {
          showMessage(`选择了干扰词！扣除${result.hearts_lost}点生命值`, 'error');
        }
      }
    } catch (error) {
      console.error('Failed to update hearts:', error);
      showMessage('更新生命值失败', 'error');
    }
    return;
  }
  
  // 检查词语是否在正确位置
  if (currentPosition < originalWords.length) {
    const expectedWord = originalWords[currentPosition];
    if (clean(selectedWord.text) !== expectedWord) {
      perfectCourse.value = false;
      incorrectWords.value.push(selectedWord.id);
      
      try {
        const difficulty = course.value?.difficulty || 'normal';
        const result = await heartsStore.loseHeart(difficulty, { isPracticeMode: isPracticeMode.value });
        
        if (result && result.message) {
          if (result.message.includes('新手保护')) {
            showMessage(result.message, 'success');
          } else if (result.message.includes('练习模式')) {
            showMessage(result.message, 'info');
          } else if (result.hearts_lost > 0) {
            showMessage(`词语位置错误！扣除${result.hearts_lost}点生命值`, 'error');
          }
        }
      } catch (error) {
        console.error('Failed to update hearts:', error);
        showMessage('更新生命值失败', 'error');
      }
    }
  }
};

const selectWord = async (word) => {
  // 记录用户已尝试答题
  markAsAttempted();
  
  shuffledWords.value = shuffledWords.value.filter(w => w.id !== word.id);
  composedSentence.value.push(word);
  
  // 实时判断当前选择的词语是否正确
  await checkCurrentWordCorrectness(word);
  
  checkCompletion();
};

const deselectWord = (word) => {
  // 移除阻止点击的条件，允许用户随时点击单词返回候选区
  composedSentence.value = composedSentence.value.filter(w => w.id !== word.id);
  shuffledWords.value.push(word);
  shuffledWords.value.sort(() => Math.random() - 0.5);
  
  // 如果移除的是错误单词，从错误列表中移除
  if (incorrectWords.value.includes(word.id)) {
    incorrectWords.value = incorrectWords.value.filter(id => id !== word.id);
  }
};

const resetJudgementAreaIfNeeded = () => {
  shuffledWords.value.push(...composedSentence.value);
  composedSentence.value = [];
  shuffledWords.value.sort(() => Math.random() - 0.5);
  incorrectWords.value = [];
};

const checkCompletion = async () => {
  if (showSuccessMessage.value) return;

  const userWords = composedSentence.value.filter(w => !w.isDistractor);
  
  const clean = (text) => text.replace(/[.,?]/g, '');
  const originalWords = currentSentence.value.text.split(/\s+/).filter(w => w).map(w => clean(w));
  
  if (userWords.length === originalWords.length) {
    const composedText = userWords.map(w => w.text).join(' ');
    const originalText = originalWords.join(' ');
  
    if (composedText === originalText) {
      // 答对了
      incorrectWords.value = [];
      
      // 直接调用奖励接口，后端会自动处理连续答对计数和奖励逻辑
      try {
        const rewardResult = await heartsStore.rewardHeart('correct_answer');
        
        // 显示奖励提示
        if (rewardResult && rewardResult.hearts_rewarded > 0 && rewardResult.message) {
          ElMessage({
            message: rewardResult.message,
            type: 'success',
            duration: 3000,
            showClose: true
          });
        }
      } catch (error) {
        console.error('Failed to reward heart:', error);
      }
      
      showSuccessMessage.value = true;
      markLevelAsComplete(currentSentenceIndex.value);
      
      setTimeout(async () => {
        showSuccessMessage.value = false;
        if (currentSentenceIndex.value < sentences.value.length - 1) {
          nextSentence();
        } else {
          // 课程完成
          const allLevelsCompleted = sentences.value.every((_, index) => completedLevels.value.includes(index));
          if (allLevelsCompleted) {
            markCourseAsFullyCompleted();
            // 完美通关奖励
            if (perfectCourse.value) {
              try {
                await heartsStore.rewardHeart('perfect_course');
              } catch (error) {
                console.error('Failed to reward perfect course:', error);
              }
            }
          }
        }
      }, 1000);
    } else {
      // 答错了 - 扣血逻辑已移至实时检查，这里只处理显示逻辑
      perfectCourse.value = false;
      
      // 标记所有错误的词语（用于显示红色高亮）
      incorrectWords.value = userWords
        .filter((word, index) => word.text !== originalWords[index])
        .map(word => word.id);
      composedSentence.value.forEach(word => {
        if (word.isDistractor) {
          incorrectWords.value.push(word.id);
        }
      });
    }
  } else if (composedSentence.value.length >= originalWords.length) {
    incorrectWords.value = composedSentence.value
      .filter(word => word.isDistractor || originalWords.indexOf(word.text) === -1)
      .map(word => word.id);
  }
};
</script>