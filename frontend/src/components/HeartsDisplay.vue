<template>
  <div class="hearts-display-container">
    <!-- 生命值显示 -->
    <div class="hearts-main" :class="{ 'low-hearts': heartsStore.isLowHearts }">
      <div class="hearts-row">
        <!-- 基础生命值 -->
        <span 
          v-for="n in heartsStore.maxHearts" 
          :key="`heart-${n}`" 
          class="heart" 
          :class="{
            'filled': n <= heartsStore.currentHearts,
            'empty': n > heartsStore.currentHearts,
            'pulse': heartsStore.isLowHearts && n <= heartsStore.currentHearts
          }"
        >
          {{ n <= heartsStore.currentHearts ? '❤️' : '🤍' }}
        </span>
        
        <!-- 额外生命值 -->
        <span 
          v-for="n in heartsStore.bonusHearts" 
          :key="`bonus-${n}`" 
          class="heart bonus-heart"
        >
          ✨
        </span>
      </div>
      
      <!-- 数字显示 -->
      <div class="hearts-count">
        <span class="current">{{ heartsStore.totalHearts }}</span>
        <span class="separator">/</span>
        <span class="max">{{ heartsStore.maxHearts }}</span>
        <span v-if="heartsStore.bonusHearts > 0" class="bonus">
          (+{{ heartsStore.bonusHearts }})
        </span>
      </div>
    </div>
    
    <!-- 恢复倒计时 -->
    <div v-if="heartsStore.recoveryCountdown" class="recovery-countdown">
      <div class="countdown-icon">⏰</div>
      <div class="countdown-text">
        下次恢复: {{ formatCountdown(heartsStore.recoveryCountdown) }}
      </div>
    </div>
    
    <!-- 新手保护提示 -->
    <div v-if="heartsStore.isNewbie" class="newbie-protection">
      <div class="protection-icon">🛡️</div>
      <div class="protection-text">
        新手保护: 还有 {{ heartsStore.newbieProtectionCount }} 次
      </div>
    </div>
    
    <!-- 连续答对显示 -->
    <div v-if="heartsStore.consecutiveCorrect > 0" class="consecutive-correct">
      <div class="streak-icon">🔥</div>
      <div class="streak-text">
        连续答对: {{ heartsStore.consecutiveCorrect }} 题
        <span v-if="heartsStore.consecutiveCorrect % 10 === 9" class="next-reward">
          (再答对1题获得奖励!)
        </span>
      </div>
    </div>
    
    <!-- 低生命值警告 -->
    <div v-if="heartsStore.isLowHearts" class="low-hearts-warning">
      <div class="warning-icon">⚠️</div>
      <div class="warning-text">
        生命值不足！小心答题
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useHeartsStore } from '@/stores/hearts'

const heartsStore = useHeartsStore()
const countdownInterval = ref(null)

// 格式化倒计时
const formatCountdown = (countdown) => {
  if (!countdown) return ''
  
  const { hours, minutes, seconds } = countdown
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  } else {
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }
}

// 启动倒计时更新
const startCountdownUpdate = () => {
  if (countdownInterval.value) return
  
  countdownInterval.value = setInterval(() => {
    // 触发响应式更新
    if (heartsStore.recoveryCountdown && heartsStore.recoveryCountdown.total <= 0) {
      // 倒计时结束，刷新生命值状态
      heartsStore.fetchHearts()
    }
  }, 1000)
}

// 停止倒计时更新
const stopCountdownUpdate = () => {
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
    countdownInterval.value = null
  }
}

onMounted(() => {
  heartsStore.fetchHearts()
  startCountdownUpdate()
})

onUnmounted(() => {
  stopCountdownUpdate()
})
</script>

<style scoped>
.hearts-display-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  border: 2px solid #dee2e6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.hearts-display-container.low-hearts {
  border-color: #dc3545;
  background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
  animation: gentle-pulse 2s infinite;
}

.hearts-main {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.hearts-row {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}

.heart {
  font-size: 1.8rem;
  transition: all 0.3s ease;
  cursor: default;
}

.heart.filled {
  transform: scale(1);
  filter: drop-shadow(0 2px 4px rgba(255, 77, 79, 0.3));
}

.heart.empty {
  opacity: 0.6;
  transform: scale(0.9);
}

.heart.pulse {
  animation: heart-pulse 1.5s infinite;
}

.heart.bonus-heart {
  color: #ffd700;
  animation: sparkle 2s infinite;
}

.hearts-count {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 600;
  font-size: 1.1rem;
}

.current {
  color: #dc3545;
  font-size: 1.2rem;
}

.separator {
  color: #6c757d;
}

.max {
  color: #6c757d;
}

.bonus {
  color: #ffd700;
  font-size: 0.9rem;
  font-weight: 500;
}

.recovery-countdown {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(13, 110, 253, 0.1);
  border-radius: 8px;
  font-size: 0.9rem;
  color: #0d6efd;
}

.countdown-icon {
  font-size: 1.1rem;
}

.newbie-protection {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(25, 135, 84, 0.1);
  border-radius: 8px;
  font-size: 0.9rem;
  color: #198754;
}

.protection-icon {
  font-size: 1.1rem;
}

.consecutive-correct {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(255, 193, 7, 0.1);
  border-radius: 8px;
  font-size: 0.9rem;
  color: #ff6b35;
}

.streak-icon {
  font-size: 1.1rem;
  animation: flame-flicker 1s infinite alternate;
}

.next-reward {
  font-weight: 600;
  color: #198754;
}

.low-hearts-warning {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(220, 53, 69, 0.1);
  border-radius: 8px;
  font-size: 0.9rem;
  color: #dc3545;
  font-weight: 500;
}

.warning-icon {
  font-size: 1.1rem;
  animation: warning-blink 1s infinite;
}

/* 动画效果 */
@keyframes heart-pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

@keyframes gentle-pulse {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(220, 53, 69, 0.2);
  }
  50% {
    box-shadow: 0 4px 16px rgba(220, 53, 69, 0.3);
  }
}

@keyframes sparkle {
  0%, 100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
  50% {
    transform: scale(1.1) rotate(180deg);
    opacity: 0.8;
  }
}

@keyframes flame-flicker {
  0% {
    transform: scale(1) rotate(-1deg);
  }
  100% {
    transform: scale(1.05) rotate(1deg);
  }
}

@keyframes warning-blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hearts-display-container {
    padding: 0.75rem;
  }
  
  .heart {
    font-size: 1.5rem;
  }
  
  .hearts-count {
    font-size: 1rem;
  }
  
  .current {
    font-size: 1.1rem;
  }
}
</style>