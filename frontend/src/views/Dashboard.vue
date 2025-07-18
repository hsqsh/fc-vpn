<template>
  <div class="dashboard">    <!-- Control Panel -->
    <el-row :gutter="20" class="control-panel">
      <!-- Usage Instructions Warning -->
      <el-col :span="24" style="margin-bottom: 20px;">
        <el-alert
          title="⚠️ Important Usage Instructions"
          type="warning"
          :closable="false"
          show-icon
        >
          <template #default>
            <div class="usage-instructions">
              <p><strong>Proxy Service Usage Flow:</strong></p>
              <ol>
                <li>🌐 <strong>Direct Access</strong> to this management website (currently in progress)</li>
                <li>🚀 Click "Start Proxy" button to launch server-side proxy service</li>
                <li>⚙️ Configure proxy settings in your browser/client: <span class="proxy-config">{{ getProxyConfig() }}</span></li>
                <li>🔄 Use proxy to access other websites, <strong style="color: #f56c6c;">but continue direct access to this management site</strong></li>
              </ol>
              <p class="warning-text">
                <el-icon><WarningFilled /></el-icon>
                <strong>Warning</strong>: Do not access this management website through proxy, or you will lose access after closing proxy!
              </p>
            </div>
          </template>
        </el-alert>
      </el-col>
      
      <el-col :span="8">        <el-card>
          <template #header>
            <span><el-icon><VideoPlay /></el-icon> Proxy Control</span>
          </template>
          <div class="control-buttons">
            <el-button
              :type="proxyStatus.running ? 'danger' : 'success'"
              :icon="proxyStatus.running ? VideoPause : VideoPlay"
              @click="toggleProxy"
              :loading="loading"
              size="large"
            >
              {{ proxyStatus.running ? 'Stop Proxy' : 'Start Proxy' }}
            </el-button>
            <el-button
              type="primary"
              :icon="Refresh"
              @click="testConnection"
              :loading="testing"
              size="large"
            >
              Test Connection
            </el-button>
          </div>
          
          <div class="config-section">
            <el-form-item label="Proxy Type:">
              <el-select
                v-model="proxyType"
                :disabled="proxyStatus.running"
                style="width: 140px;"
              >
                <el-option label="HTTP Proxy" value="http" />
                <el-option label="SOCKS5 Proxy" value="socks5" />
              </el-select>
            </el-form-item>
            <el-form-item label="Port:">
              <el-input-number
                v-model="port"
                :min="1024"
                :max="65535"
                :disabled="proxyStatus.running"
              />
            </el-form-item>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">        <el-card>
          <template #header>
            <span><el-icon><Monitor /></el-icon> Real-time Status</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="5">
              <el-statistic
                title="Proxy Type"
                :value="proxyStatus.proxy_type ? proxyStatus.proxy_type.toUpperCase() : 'HTTP'"
              />
            </el-col>
            <el-col :span="5">
              <el-statistic
                title="Current Connections"
                :value="proxyStatus.connections"
                suffix="connections"
              />
            </el-col>
            <el-col :span="5">
              <el-statistic
                title="Total Traffic"
                :value="formatBytes(proxyStatus.total_bytes)"
              />
            </el-col>
            <el-col :span="5">
              <el-statistic
                title="Running Port"
                :value="portInfo.port || proxyStatus.port"
                :suffix="portInfo.k8s_mode ? ' (dynamic)' : ''"
              />
            </el-col>
            <el-col :span="4">
              <el-statistic
                title="Uptime"
                :value="uptime"
              />
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>    
    <!-- Port Information Display -->
    <el-row :gutter="20" style="margin-top: 20px;" v-if="portInfo.running">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span><el-icon><Monitor /></el-icon> Port Details</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Actual Port">
              <el-tag :type="portInfo.k8s_mode ? 'warning' : 'success'">
                {{ portInfo.port }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Configured Port">{{ portInfo.configured_port }}</el-descriptions-item>
            <el-descriptions-item label="Environment Mode">
              <el-tag :type="portInfo.k8s_mode ? 'primary' : 'info'">
                {{ portInfo.k8s_mode ? 'Kubernetes' : 'Local Environment' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Pod Name" v-if="portInfo.k8s_mode">{{ portInfo.pod_name }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span><el-icon><DataAnalysis /></el-icon> Traffic Statistics</span>
          </template>
          <div class="traffic-info">
            <p>Total Connections: {{ proxyStatus.connections }}</p>
            <p>Total Traffic: {{ formatBytes(proxyStatus.total_bytes) }}</p>
            <p>Active Connections: {{ activeConnections.length }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>    
    <!-- Connection Monitoring -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span><el-icon><Connection /></el-icon> Active Connections</span>
          </template>
          <div class="connections-list">
            <el-empty v-if="activeConnections.length === 0" description="No active connections" />
            <div v-else>
              <div
                v-for="connection in activeConnections"
                :key="connection"
                class="connection-item"
              >
                <el-tag size="small">{{ connection }}</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span><el-icon><DataAnalysis /></el-icon> System Information</span>
          </template>
          <div class="traffic-info">
            <p v-if="!portInfo.running">Total Connections: {{ proxyStatus.connections }}</p>
            <p v-if="!portInfo.running">Total Traffic: {{ formatBytes(proxyStatus.total_bytes) }}</p>
            <p v-if="!portInfo.running">Active Connections: {{ activeConnections.length }}</p>
            <p>Proxy Status: {{ proxyStatus.running ? 'Running' : 'Stopped' }}</p>
            <p>Environment: {{ portInfo.k8s_mode ? 'Kubernetes' : 'Local' }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>    
    <!-- Connection Testing -->
    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span><el-icon><Link /></el-icon> Proxy Connection Test</span>
          </template>
          
          <el-form :model="testForm" inline>
            <el-form-item label="Test Target:">
              <el-select v-model="testForm.url" placeholder="Select test target" style="width: 300px;">
                <el-option label="httpbin.org (IP Detection)" value="http://httpbin.org/ip" />
                <el-option label="Google (Search Engine)" value="http://www.google.com" />
                <el-option label="Baidu (Search Engine)" value="http://www.baidu.com" />
                <el-option label="GitHub (Code Repository)" value="https://github.com" />
                <el-option label="Custom URL" value="custom" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="testForm.url === 'custom'" label="Custom URL:">
              <el-input
                v-model="testForm.customUrl"
                placeholder="Enter complete URL"
                style="width: 300px;"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                @click="testConnection"
                :loading="testing"
                :disabled="!proxyStatus.running"
              >
                Start Test
              </el-button>
            </el-form-item>
          </el-form>
          
          <div v-if="testResult" style="margin-top: 15px;">
            <el-alert
              :title="testResult.success ? '✅ Proxy Connection Successful' : '❌ Proxy Connection Failed'"
              :type="testResult.success ? 'success' : 'error'"
              :description="testResult.message"
              show-icon
            >
              <template v-if="testResult.success && testResult.details" #default>
                <div style="margin-top: 10px;">
                  <p><strong>Response Time:</strong> {{ testResult.details.response_time }}</p>
                  <p><strong>Target Address:</strong> {{ testResult.details.target }}</p>
                </div>
              </template>
            </el-alert>
          </div>
          <div v-if="!proxyStatus.running" style="margin-top: 15px;">
            <el-alert
              title="Proxy Service Not Running"
              description="Please start the proxy service before performing connection test"
              type="warning"
              show-icon
              :closable="false"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  VideoPlay,
  VideoPause,
  Refresh,
  Monitor,
  Connection,
  DataAnalysis,
  Link,
  WarningFilled
} from '@element-plus/icons-vue'
import { io } from 'socket.io-client'

export default {
  name: 'Dashboard',  components: {
    VideoPlay,
    VideoPause,
    Refresh,
    Monitor,
    Connection,
    DataAnalysis,
    Link,
    WarningFilled
  },
  setup() {
    const proxyStatus = ref({
      running: false,
      port: 8888,
      proxy_type: 'http',
      connections: 0,
      total_bytes: 0,
      active_connections: [],
      start_time: null
    })

    const portInfo = ref({
      port: null,
      configured_port: null,
      running: false,
      k8s_mode: false,
      pod_name: null
    })

    const port = ref(8888)
    const proxyType = ref('http')
    const loading = ref(false)
    const testing = ref(false)
    const testForm = ref({ 
      url: 'http://httpbin.org/ip',
      customUrl: ''
    })
    const testResult = ref(null)

    let socket = null

    const activeConnections = computed(() => proxyStatus.value.active_connections || [])
    
    const uptime = computed(() => {
      if (!proxyStatus.value.start_time) return 'Not Running'
      const start = new Date(proxyStatus.value.start_time * 1000)
      const now = new Date()
      const diff = Math.floor((now - start) / 1000)
      const hours = Math.floor(diff / 3600)
      const minutes = Math.floor((diff % 3600) / 60)
      const seconds = diff % 60
      return `${hours}h ${minutes}m ${seconds}s`
    })

    const formatBytes = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const getProxyConfig = () => {
      if (portInfo.value.running && portInfo.value.port) {
        const hostname = window.location.hostname
        return `${hostname}:${portInfo.value.port} (${proxyStatus.value.proxy_type?.toUpperCase() || 'HTTP'})`
      } else if (proxyStatus.value.running) {
        const hostname = window.location.hostname
        return `${hostname}:${proxyStatus.value.port} (${proxyStatus.value.proxy_type?.toUpperCase() || 'HTTP'})`
      }      return 'Proxy service not started'
    }

    const toggleProxy = async () => {
      loading.value = true
      try {
        const endpoint = proxyStatus.value.running ? '/api/proxy/stop' : '/api/proxy/start'
        const body = proxyStatus.value.running ? {} : { 
          port: port.value,
          proxy_type: proxyType.value
        }
        
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        })

        const data = await response.json()
        if (response.ok) {
          proxyStatus.value = data.status;
          ElMessage.success(data.message)
          // Get port info immediately after startup
          if (data.status.running) {
            setTimeout(fetchPortInfo, 1000)
          }
        } else {
          ElMessage.error(data.error)
        }
      } catch (error) {
        ElMessage.error('Operation failed: ' + error.message)      } finally {
        loading.value = false
      }
    }

    const testConnection = async () => {
      if (!proxyStatus.value.running) {
        ElMessage.warning('Please start proxy service first')
        return
      }

      testing.value = true
      testResult.value = null
      
      try {
        let testUrl = testForm.value.url === 'custom' ? testForm.value.customUrl : testForm.value.url
        
        if (!testUrl) {
          ElMessage.error('Please enter test URL')
          testing.value = false
          return
        }

        if (testForm.value.url === 'custom') {
          if (!testUrl.startsWith('http://') && !testUrl.startsWith('https://')) {
            testUrl = 'http://' + testUrl
          }
        }

        const response = await fetch('/api/proxy/test', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: testUrl })
        })

        const data = await response.json()
        
        if (data.success) {
          testResult.value = {
            success: true,
            message: data.message,
            details: {
              response_time: data.response_time,
              target: data.target
            }
          }
          ElMessage.success('Proxy test successful!')
        } else {
          testResult.value = {
            success: false,
            message: data.error
          }
          ElMessage.error('Proxy test failed')
        }
      } catch (error) {
        testResult.value = {
          success: false,
          message: 'Network error: ' + error.message
        }
        ElMessage.error('Test failed: ' + error.message)
      } finally {
        testing.value = false
      }
    }

    const fetchPortInfo = async () => {
      try {
        const response = await fetch('/api/proxy/port')
        const data = await response.json()
        if (response.ok) {
          portInfo.value = data
        }
      } catch (error) {
        console.error('Failed to fetch port info:', error)
      }
    }

    const fetchProxyStatus = async () => {
      try {
        const response = await fetch('/api/proxy/status')
        const data = await response.json()
        proxyStatus.value = data      } catch (error) {
        console.error('Failed to fetch proxy status:', error)
      }
    }

    onMounted(() => {
      // Connect WebSocket - dynamically get backend address
      const socketUrl = import.meta.env.PROD ? window.location.origin : 'http://localhost:5000'
      socket = io(socketUrl)
      
      socket.on('proxy_stats', (data) => {
        proxyStatus.value = data
      })

      socket.on('connect', () => {
        console.log('Connected to server')
        fetchProxyStatus()
        fetchPortInfo()
      })

      socket.on('disconnect', () => {
        console.log('Disconnected from server')
      })

      fetchProxyStatus()
      fetchPortInfo()
      
      // Update port info periodically
      setInterval(() => {
        if (proxyStatus.value.running) {
          fetchPortInfo()
        }
      }, 5000)
    })

    onUnmounted(() => {      if (socket) {
        socket.disconnect()
      }
    })

    return {
      proxyStatus,
      portInfo,
      port,
      proxyType,
      loading,
      testing,
      testForm,
      testResult,
      activeConnections,
      uptime,
      formatBytes,
      getProxyConfig,
      toggleProxy,
      testConnection
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.control-panel {
  margin-bottom: 20px;
}

.control-buttons {
  margin-bottom: 20px;
}

.control-buttons .el-button {
  margin-right: 10px;
  margin-bottom: 10px;
}

.config-section .el-form-item {
  margin-bottom: 10px;
}

.connections-list {
  max-height: 200px;
  overflow-y: auto;
}

.connection-item {
  margin-bottom: 8px;
}

.traffic-info p {
  margin: 10px 0;
  font-size: 14px;
}

.usage-instructions {
  font-size: 14px;
}

.usage-instructions ol {
  margin: 10px 0;
  padding-left: 20px;
}

.usage-instructions li {
  margin: 8px 0;
  line-height: 1.5;
}

.proxy-config {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  font-weight: bold;
  color: #409eff;
}

.warning-text {
  color: #f56c6c;
  margin-top: 10px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>
