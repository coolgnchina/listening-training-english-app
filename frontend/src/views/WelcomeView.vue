<template>
  <div class="welcome-container">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">欢迎来到听力训练</h1>
        <p class="hero-subtitle">提升您的英语听力技能，从这里开始</p>
        <div class="hero-actions">
          <router-link to="/courses" class="btn btn-primary btn-large hero-cta-btn">开始学习</router-link>
          <router-link v-if="!authStore.isAuthenticated" to="/login" class="btn btn-secondary btn-large">立即登录</router-link>
        </div>
      </div>
      <div class="hero-image">
        <div class="floating-card">
          <div class="card-icon">🎧</div>
          <h3>智能听力训练</h3>
          <p>个性化学习路径</p>
        </div>
        <div class="floating-card delay-1">
          <div class="card-icon">📚</div>
          <h3>丰富课程内容</h3>
          <p>从基础到高级</p>
        </div>
        <div class="floating-card delay-2">
          <div class="card-icon">🏆</div>
          <h3>成就系统</h3>
          <p>激励持续学习</p>
        </div>
      </div>
    </div>
    
    <div class="features-section">
      <div class="container">
        <h2 class="section-title">为什么选择我们？</h2>
        <div class="features-grid">
          <div class="feature-card card">
            <div class="feature-icon">🎯</div>
            <h3>精准训练</h3>
            <p>针对性的听力练习，快速提升理解能力</p>
          </div>
          <div class="feature-card card">
            <div class="feature-icon">📱</div>
            <h3>随时随地</h3>
            <p>支持多设备学习，随时随地提升听力</p>
          </div>
          <div class="feature-card card">
            <div class="feature-icon">📊</div>
            <h3>进度跟踪</h3>
            <p>详细的学习报告，清晰了解学习进度</p>
          </div>
          <div class="feature-card card">
            <div class="feature-icon">🌟</div>
            <h3>趣味学习</h3>
            <p>游戏化学习体验，让学习变得更有趣</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="cta-section">
      <div class="container">
        <div class="cta-content">
          <h2>准备好开始您的听力训练之旅了吗？</h2>
          <p>加入我们，体验最专业的英语听力训练平台</p>
          <div class="cta-actions">
            <router-link v-if="!authStore.isAuthenticated" to="/register" class="btn btn-primary btn-large">免费注册</router-link>
            <router-link to="/courses" class="btn btn-secondary btn-large">浏览课程</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
</script>

<style scoped>
.welcome-container {
  min-height: 100vh;
}

.hero-section {
  min-height: 100vh;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  padding: var(--spacing-xl);
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><defs><radialGradient id="a" cx=".5" cy=".5" r=".5"><stop offset="0%" stop-color="%23ffffff" stop-opacity=".1"/><stop offset="100%" stop-color="%23ffffff" stop-opacity="0"/></radialGradient></defs><circle cx="200" cy="200" r="100" fill="url(%23a)"/><circle cx="800" cy="300" r="150" fill="url(%23a)"/><circle cx="400" cy="700" r="120" fill="url(%23a)"/></svg>') no-repeat center center;
  background-size: cover;
  opacity: 0.3;
}

.hero-content {
  flex: 1;
  max-width: 600px;
  z-index: 2;
  position: relative;
}

.hero-title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 800;
  color: white;
  margin-bottom: var(--spacing-lg);
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.hero-subtitle {
  font-size: var(--font-size-xl);
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: var(--spacing-2xl);
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}

.btn-large {
  padding: var(--spacing-lg) var(--spacing-2xl);
  font-size: var(--font-size-lg);
  border-radius: var(--border-radius-lg);
}

.hero-image {
  flex: 1;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2;
}

.floating-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-xl);
  text-align: center;
  box-shadow: var(--shadow-lg);
  animation: float 6s ease-in-out infinite;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.floating-card:nth-child(1) {
  top: 20%;
  left: 10%;
}

.floating-card:nth-child(2) {
  top: 50%;
  right: 20%;
}

.floating-card:nth-child(3) {
  bottom: 20%;
  left: 20%;
}

.delay-1 {
  animation-delay: -2s;
}

.delay-2 {
  animation-delay: -4s;
}

.card-icon {
  font-size: 2rem;
  margin-bottom: var(--spacing-sm);
}

.floating-card h3 {
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  color: var(--text-primary);
}

.floating-card p {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.features-section {
  padding: var(--spacing-3xl) 0;
  background: var(--background-light);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-xl);
  margin-top: var(--spacing-2xl);
}

.feature-card {
  text-align: center;
  padding: var(--spacing-2xl);
  transition: transform var(--transition-normal);
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-lg);
}

.feature-card h3 {
  font-size: var(--font-size-xl);
  font-weight: 600;
  margin-bottom: var(--spacing-md);
  color: var(--text-primary);
}

.feature-card p {
  color: var(--text-secondary);
  line-height: 1.6;
}

.cta-section {
  padding: var(--spacing-3xl) 0;
  background: var(--gradient-secondary);
  text-align: center;
}

.cta-content h2 {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: white;
  margin-bottom: var(--spacing-lg);
}

.cta-content p {
  font-size: var(--font-size-lg);
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: var(--spacing-2xl);
}

.cta-actions {
  display: flex;
  gap: var(--spacing-lg);
  justify-content: center;
  flex-wrap: wrap;
}

/* 首页主要按钮样式增强 */
.hero-cta-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
  color: white !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
  border: 3px solid rgba(255, 255, 255, 0.3);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.hero-cta-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.hero-cta-btn:hover {
  transform: translateY(-3px) scale(1.05) !important;
  box-shadow: 0 12px 35px rgba(255, 107, 107, 0.6) !important;
  border-color: rgba(255, 255, 255, 0.5);
}

.hero-cta-btn:hover::before {
  left: 100%;
}

.hero-cta-btn:active {
  transform: translateY(-1px) scale(1.02) !important;
}

/* 添加脉冲动画 */
@keyframes pulse {
  0% {
    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
  }
  50% {
    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.6), 0 0 0 10px rgba(255, 107, 107, 0.1);
  }
  100% {
    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
  }
}

.hero-cta-btn {
  animation: pulse 2s infinite;
}

@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    text-align: center;
    padding: var(--spacing-lg);
  }
  
  .hero-image {
    margin-top: var(--spacing-2xl);
    position: relative;
    height: 300px;
  }
  
  .floating-card {
    position: relative;
    margin: var(--spacing-md);
    display: inline-block;
  }
  
  .floating-card:nth-child(1),
  .floating-card:nth-child(2),
  .floating-card:nth-child(3) {
    position: relative;
    top: auto;
    left: auto;
    right: auto;
    bottom: auto;
  }
  
  .hero-actions,
  .cta-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn-large {
    width: 100%;
    max-width: 300px;
  }
}
</style>