<template>
  <div id="app">
    <el-container class="main-container">
      <el-header class="header">
        <div class="header-content">
          <h1><el-icon><Connection /></el-icon> 代理服务管理平台</h1>
          <div class="status-indicator">
            <el-tag :type="proxyStatus.running ? 'success' : 'danger'">
              {{ proxyStatus.running ? '运行中' : '已停止' }}
            </el-tag>
          </div>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { io } from 'socket.io-client'
import { Connection } from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    Connection
  },
  setup() {
    const proxyStatus = ref({
      running: false,
      port: 8888,
      connections: 0,
      total_bytes: 0
    })

    let socket = null

    onMounted(() => {
      // 连接WebSocket
      socket = io('http://localhost:5000')
      
      socket.on('proxy_stats', (data) => {
        proxyStatus.value = data
      })

      socket.on('connect', () => {
        console.log('Connected to server')
      })

      socket.on('disconnect', () => {
        console.log('Disconnected from server')
      })

      // 获取初始状态
      fetchProxyStatus()
    })

    onUnmounted(() => {
      if (socket) {
        socket.disconnect()
      }
    })

    const fetchProxyStatus = async () => {
      try {
        const response = await fetch('/api/proxy/status')
        const data = await response.json()
        proxyStatus.value = data
      } catch (error) {
        console.error('Failed to fetch proxy status:', error)
      }
    }

    return {
      proxyStatus
    }
  }
}
</script>

<style scoped>
.main-container {
  height: 100vh;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-content h1 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-content {
  background: #f5f5f5;
  padding: 20px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>

<style>
body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

#app {
  min-height: 100vh;
}
</style>
