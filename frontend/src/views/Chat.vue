<template>
  <div class="chat-container">
    <el-card class="chat-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>🧠 大学生心理疗愈智能体</span>
        </div>
      </template>
      
      <el-scrollbar height="400px" class="message-list">
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          :class="['message-item', msg.role]"
        >
          <div class="message-bubble" v-loading="msg.isLoading">{{ msg.content }}</div>
        </div>
      </el-scrollbar>

      <div class="input-area">
        <el-input 
          v-model="inputText" 
          placeholder="有什么心事，都可以跟我说说..." 
          @keyup.enter="sendMessage"
          :disabled="isSending"
        >
          <template #append>
            <el-button type="primary" @click="sendMessage" :loading="isSending">发送</el-button>
          </template>
        </el-input>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

// 初始化一条欢迎语，更贴合你的疗愈 Agent 定位
const messages = ref([
  { role: 'assistant', content: '你好！我是基于火山 HiAgent 构建的心理疗愈智能体。无论学业压力还是生活烦恼，都可以跟我倾诉哦。' }
])

const inputText = ref('')
const isSending = ref(false) // 这是一个开关，记录当前是否正在等待 AI 回复

const sendMessage = async () => {
  // 如果输入为空，或者正在发送中，就不执行任何操作
  if (!inputText.value.trim() || isSending.value) return 
  
  // 1. 把用户的话立刻显示到屏幕上
  let userText = inputText.value
  messages.value.push({ role: 'user', content: userText })
  inputText.value = ''
  
  // 2. 开启“发送中”状态，锁住输入框和按钮
  isSending.value = true
  
  // 3. 在屏幕上放一个占位气泡，显示“...”表示 AI 正在思考
  messages.value.push({ role: 'assistant', content: '...', isLoading: true })
  
  try {
    // 4. 关键点：服务员 Axios 发起真正的 POST 请求，带上用户的消息
    const response = await axios.post('http://127.0.0.1:8000/api/chat', {
      message: userText
    })
    
    // 5. 收到回复后，先把那个占位的“...”气泡删掉
    messages.value.pop()
    
    // 6. 把后端传回来的真实回复追加到屏幕上
    messages.value.push({ 
      role: 'assistant', 
      content: response.data.reply 
    })
    
  } catch (error) {
    // 如果网络断了或后端报错，给用户一个优雅的提示
    messages.value.pop()
    messages.value.push({ 
      role: 'assistant', 
      content: '抱歉，我的思绪暂时飘远了（服务器连接断开），请检查后端是否在运行哦。' 
    })
    console.error(error)
  } finally {
    // 7. 无论成功还是失败，最后都要解锁输入框
    isSending.value = false
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.chat-card {
  width: 100%;
  max-width: 800px; /* 限制聊天框最大宽度 */
  border-radius: 12px;
}

.card-header {
  font-weight: bold;
  font-size: 18px;
  color: #2c3e50;
}

.message-list {
  padding: 10px;
  background-color: #f9f9fa; /* 淡淡的灰色背景 */
  border-radius: 8px;
}

.message-item {
  display: flex;
  margin-bottom: 15px;
}

/* 气泡通用样式 */
.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.5;
  word-wrap: break-word;
}

/* AI 的气泡靠左 */
.assistant {
  justify-content: flex-start;
}
.assistant .message-bubble {
  background-color: #ffffff;
  border: 1px solid #ebeef5;
  color: #333;
}

/* 用户的气泡靠右，背景变色 */
.user {
  justify-content: flex-end;
}
.user .message-bubble {
  background-color: #95d475; /* 清新的绿色 */
  color: white;
}

.input-area {
  margin-top: 20px;
}
</style>