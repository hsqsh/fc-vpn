<template>
  <div class="settings">
    <el-card>
      <template #header>
        <span><el-icon><Setting /></el-icon> Proxy Settings</span>
      </template>
      
      <el-form :model="settings" label-width="120px">
        <el-form-item label="Default Port:">
          <el-input-number
            v-model="settings.defaultPort"
            :min="1024"
            :max="65535"
          />
        </el-form-item>
        
        <el-form-item label="Max Connections:">
          <el-input-number
            v-model="settings.maxConnections"
            :min="1"
            :max="1000"
          />
        </el-form-item>
        
        <el-form-item label="Connection Timeout:">
          <el-input-number
            v-model="settings.timeout"
            :min="5"
            :max="300"
          />
          <span style="margin-left: 10px;">seconds</span>
        </el-form-item>
        
        <el-form-item label="Log Level:">
          <el-select v-model="settings.logLevel">
            <el-option label="DEBUG" value="DEBUG" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Enable Logging:">
          <el-switch v-model="settings.enableLogging" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveSettings">Save Settings</el-button>
          <el-button @click="resetSettings">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>
      <el-card style="margin-top: 20px;">
      <template #header>
        <span><el-icon><Monitor /></el-icon> System Information</span>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="App Version">v1.0.0</el-descriptions-item>
        <el-descriptions-item label="Backend API">Flask + SocketIO</el-descriptions-item>
        <el-descriptions-item label="Frontend Framework">Vue 3 + Element Plus</el-descriptions-item>
        <el-descriptions-item label="Supported Protocol">SOCKS5</el-descriptions-item>
        <el-descriptions-item label="Deployment Environment">Local / Kubernetes</el-descriptions-item>
        <el-descriptions-item label="Developer">VPN Proxy Team</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting, Monitor } from '@element-plus/icons-vue'

export default {
  name: 'Settings',
  components: {
    Setting,
    Monitor
  },
  setup() {
    const settings = ref({
      defaultPort: 8888,
      maxConnections: 100,
      timeout: 30,
      logLevel: 'INFO',
      enableLogging: true
    });
    
    const saveSettings = () => {
      // Save settings to localStorage
      localStorage.setItem('proxySettings', JSON.stringify(settings.value))
      ElMessage.success('Settings saved')
    }

    const resetSettings = () => {
      settings.value = {
        defaultPort: 8888,
        maxConnections: 100,
        timeout: 30,
        logLevel: 'INFO',
        enableLogging: true
      }
      ElMessage.info('Settings reset')
    }

    onMounted(() => {
      // Load settings from localStorage
      const saved = localStorage.getItem('proxySettings')
      if (saved) {
        try {
          settings.value = { ...settings.value, ...JSON.parse(saved) }
        } catch (error) {
          console.error('Failed to load settings:', error)
        }
      }
    })

    return {
      settings,
      saveSettings,
      resetSettings
    }
  }
}
</script>

<style scoped>
.settings {
  padding: 20px;
}
</style>
