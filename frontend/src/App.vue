<template>
  <div id="app">
    <el-container class="main-container">
      <el-header class="header">
        <div class="header-content">
          <h1><el-icon><Connection /></el-icon> Proxy Service Platform</h1>
          <div class="header-actions">
            <el-button 
              type="primary" 
              size="small" 
              @click="toggleSidebar"
              :icon="sidebarCollapsed ? Menu : Fold"
              circle
            />
            <div class="status-indicator">
              <el-tag :type="proxyStatus.running ? 'success' : 'danger'">
                {{ proxyStatus.running ? 'Running' : 'Stopped' }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-header>
      
      <el-container>
        <el-aside :width="sidebarCollapsed ? '64px' : '200px'" class="sidebar">
          <el-menu
            :default-active="$route.path"
            class="sidebar-menu"
            :collapse="sidebarCollapsed"
            router
            background-color="#304156"
            text-color="#bfcbd9"
            active-text-color="#409EFF"
          >
            <el-menu-item index="/">
              <el-icon><Monitor /></el-icon>
              <template #title>Console</template>
            </el-menu-item>
            
            <el-menu-item index="/ip-detection">
              <el-icon><Position /></el-icon>
              <template #title>IP test</template>
            </el-menu-item>
            
            <el-menu-item index="/pod-monitor">
              <el-icon><DataBoard /></el-icon>
              <template #title>Pod monitoring</template>
            </el-menu-item>
            
            <el-menu-item index="/settings">
              <el-icon><Setting /></el-icon>
              <template #title>set</template>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { io } from 'socket.io-client'
import { Connection, Monitor, Position, DataBoard, Setting, Menu, Fold } from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    Connection, Monitor, Position, DataBoard, Setting, Menu, Fold
  },
  setup() {
    const proxyStatus = ref({
      running: false,
      port: 8888,
      connections: 0,
      total_bytes: 0
    })

    const sidebarCollapsed = ref(false)

    let socket = null

    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
    }

    const fetchProxyStatus = async () => {
      try {
        const response = await fetch('/api/proxy/status')
        const data = await response.json()
        proxyStatus.value = data
      } catch (error) {
        console.error('Failed to fetch proxy status:', error)
      }
    };
    
    onMounted(() => {
      // 连接WebSocket - 动态获取后端地址
      const socketUrl = import.meta.env.PROD ? window.location.origin : 'http://localhost:5000'
      socket = io(socketUrl)
      
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

    return {
      proxyStatus,
      sidebarCollapsed,
      toggleSidebar
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
  z-index: 1000;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar-menu {
  border-right: none;
  height: 100%;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

.main-content {
  background: #f5f5f5;
  padding: 20px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content h1 {
    font-size: 1.2rem;
  }
  
  .header-actions {
    gap: 10px;
  }
  
  .main-content {
    padding: 10px;
  }
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