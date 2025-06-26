import { ref } from 'vue'

// 全局错误状态
const errorMessage = ref('')
const showError = ref(false)

export function useErrorHandler() {
  const handleError = (error, customMessage = null) => {
    console.error('Error occurred:', error)
    
    let message = customMessage
    
    if (!message) {
      if (error.response?.data?.message) {
        message = error.response.data.message
      } else if (error.message) {
        message = error.message
      } else if (typeof error === 'string') {
        message = error
      } else {
        message = '操作失败，请稍后重试'
      }
    }
    
    errorMessage.value = message
    showError.value = true
  }
  
  const handleHeartsError = (error) => {
    if (error.message?.includes('Failed to fetch hearts')) {
      handleError(error, '获取生命值状态失败，请检查网络连接')
    } else if (error.message?.includes('Failed to lose heart')) {
      handleError(error, '更新生命值失败，请稍后重试')
    } else if (error.message?.includes('Failed to reward heart')) {
      handleError(error, '奖励生命值失败，请稍后重试')
    } else {
      handleError(error, '生命值系统出现问题，请稍后重试')
    }
  }
  
  const clearError = () => {
    errorMessage.value = ''
    showError.value = false
  }
  
  return {
    errorMessage,
    showError,
    handleError,
    handleHeartsError,
    clearError
  }
}