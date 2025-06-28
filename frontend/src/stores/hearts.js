import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useAuthStore } from './auth'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { buildApiUrl } from '@/config/api'

export const useHeartsStore = defineStore('hearts', () => {
  // 状态
  const currentHearts = ref(5)
  const maxHearts = ref(5)
  const bonusHearts = ref(0)
  const nextRecoveryTime = ref(null)
  const isNewbie = ref(true)
  const newbieProtectionCount = ref(3)
  const consecutiveCorrect = ref(0)
  const lastUpdate = ref(null)
  const cacheTimeout = 30000 // 30秒缓存
  
  // 计算属性
  const totalHearts = computed(() => currentHearts.value + bonusHearts.value)
  const isLowHearts = computed(() => totalHearts.value <= 2)
  const canPlay = computed(() => totalHearts.value > 0)
  const recoveryCountdown = computed(() => {
    if (!nextRecoveryTime.value || currentHearts.value >= maxHearts.value) return null
    
    const now = new Date()
    const recovery = new Date(nextRecoveryTime.value)
    const diff = recovery - now
    
    if (diff <= 0) return null
    
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    const seconds = Math.floor((diff % (1000 * 60)) / 1000)
    
    return { hours, minutes, seconds, total: diff }
  })
  
  // 获取生命值状态（带缓存）
  const fetchHearts = async (forceRefresh = false) => {
    const authStore = useAuthStore()
    if (!authStore.token) return
    
    // 检查缓存是否有效
    if (!forceRefresh && lastUpdate.value) {
      const timeSinceUpdate = Date.now() - lastUpdate.value
      if (timeSinceUpdate < cacheTimeout) {
        return // 使用缓存数据
      }
    }
    
    try {
            const response = await fetch(buildApiUrl('/user/hearts'), {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
        },
      })
      
      if (!response.ok) throw new Error('Failed to fetch hearts')
      
      const data = await response.json()
      updateHeartsData(data)
      lastUpdate.value = Date.now()
      
      return data
    } catch (error) {
      const { handleHeartsError } = useErrorHandler()
      handleHeartsError(error)
      throw error
    }
  }
  
  // 更新生命值数据
  const updateHeartsData = (data) => {
    currentHearts.value = data.current_hearts
    maxHearts.value = data.max_hearts
    bonusHearts.value = data.bonus_hearts || 0
    nextRecoveryTime.value = data.next_recovery_time
    isNewbie.value = data.is_newbie
    newbieProtectionCount.value = data.newbie_protection_count
    consecutiveCorrect.value = data.consecutive_correct
    lastUpdate.value = new Date().toISOString()
  }
  
  // 扣除生命值
  const loseHeart = async (difficulty, options = {}) => {
    const authStore = useAuthStore()
    if (!authStore.token) return
    
    // 支持两种调用方式：
    // 1. loseHeart('view_original') - 查看原文
    // 2. loseHeart('normal', { isPracticeMode: false }) - 答题错误
    let actionType = 'wrong_answer'
    let actualDifficulty = difficulty
    let isPracticeMode = false
    
    if (difficulty === 'view_original') {
      actionType = 'view_original'
      actualDifficulty = 'normal' // 查看原文时难度不重要
    } else {
      const { isPracticeMode: practice = false } = options
      isPracticeMode = practice
    }
    
    try {
            const response = await fetch(buildApiUrl('/user/hearts/lose'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`,
        },
        body: JSON.stringify({
          difficulty: actualDifficulty,
          is_practice_mode: isPracticeMode,
          action_type: actionType
        })
      })
      
      if (!response.ok) throw new Error('Failed to lose heart')
      
      const data = await response.json()
      
      // 更新本地状态
      if (data.success) {
        currentHearts.value = data.current_hearts || currentHearts.value
        bonusHearts.value = data.bonus_hearts || bonusHearts.value
        
        // 如果有新手保护信息，更新相关状态
        if (data.newbie_protection_remaining !== undefined) {
          newbieProtectionCount.value = data.newbie_protection_remaining
        }
      }
      
      return data
    } catch (error) {
      const { handleHeartsError } = useErrorHandler()
      handleHeartsError(error)
      throw error
    }
  }
  
  // 奖励生命值
  const rewardHeart = async (type = 'correct_answer') => {
    const authStore = useAuthStore()
    if (!authStore.token) return
    
    try {
            const response = await fetch(buildApiUrl('/user/hearts/reward'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`,
        },
        body: JSON.stringify({ type })
      })
      
      if (!response.ok) throw new Error('Failed to reward heart')
      
      const data = await response.json()
      
      // 更新本地状态
      if (data.success) {
        currentHearts.value = data.current_hearts
        bonusHearts.value = data.bonus_hearts
        consecutiveCorrect.value = data.consecutive_correct
      }
      
      return data
    } catch (error) {
      const { handleHeartsError } = useErrorHandler()
      handleHeartsError(error)
      throw error
    }
  }
  
  // 更新连续答对计数
  const updateConsecutiveCorrect = async (increment = true) => {
    const authStore = useAuthStore()
    if (!authStore.token) return
    
    try {
            const response = await fetch(buildApiUrl('/hearts/consecutive'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`,
        },
        body: JSON.stringify({ increment })
      })
      
      if (!response.ok) throw new Error('Failed to update consecutive correct')
      
      const data = await response.json()
      
      // 更新本地状态
      if (data.success) {
        consecutiveCorrect.value = data.consecutive_correct
      }
      
      return data
    } catch (error) {
      const { handleHeartsError } = useErrorHandler()
      handleHeartsError(error)
      throw error
    }
  }
  
  // 重置连续答对计数
  const resetConsecutiveCorrect = async () => {
    return await updateConsecutiveCorrect(false)
  }
  
  // 重置状态
  const reset = () => {
    currentHearts.value = 5
    maxHearts.value = 5
    bonusHearts.value = 0
    nextRecoveryTime.value = null
    isNewbie.value = true
    newbieProtectionCount.value = 3
    consecutiveCorrect.value = 0
    lastUpdate.value = null
  }
  
  return {
    // 状态
    currentHearts,
    maxHearts,
    bonusHearts,
    nextRecoveryTime,
    isNewbie,
    newbieProtectionCount,
    consecutiveCorrect,
    lastUpdate,
    
    // 计算属性
    totalHearts,
    isLowHearts,
    canPlay,
    recoveryCountdown,
    
    // 方法
    fetchHearts,
    updateHeartsData,
    loseHeart,
    rewardHeart,
    updateConsecutiveCorrect,
    resetConsecutiveCorrect,
    reset
  }
})