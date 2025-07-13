<template>
  <div class="settings">
    <el-card>
      <template #header>
        <span><el-icon><Setting /></el-icon> 代理设置</span>
      </template>
      
      <el-form :model="settings" label-width="120px">
        <el-form-item label="默认端口:">
          <el-input-number
            v-model="settings.defaultPort"
            :min="1024"
            :max="65535"
          />
        </el-form-item>
        
        <el-form-item label="最大连接数:">
          <el-input-number
            v-model="settings.maxConnections"
            :min="1"
            :max="1000"
          />
        </el-form-item>
        
        <el-form-item label="连接超时:">
          <el-input-number
            v-model="settings.timeout"
            :min="5"
            :max="300"
          />
          <span style="margin-left: 10px;">秒</span>
        </el-form-item>
        
        <el-form-item label="日志级别:">
          <el-select v-model="settings.logLevel">
            <el-option label="DEBUG" value="DEBUG" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="启用日志:">
          <el-switch v-model="settings.enableLogging" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
          <el-button @click="resetSettings">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <span><el-icon><Monitor /></el-icon> 系统信息</span>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="应用版本">v1.0.0</el-descriptions-item>
        <el-descriptions-item label="后端API">Flask + SocketIO</el-descriptions-item>
        <el-descriptions-item label="前端框架">Vue 3 + Element Plus</el-descriptions-item>
        <el-descriptions-item label="支持协议">SOCKS5</el-descriptions-item>
        <el-descriptions-item label="部署环境">本地 / Kubernetes</el-descriptions-item>
        <el-descriptions-item label="开发者">VPN Proxy Team</el-descriptions-item>
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
    })

    const saveSettings = () => {
      // 保存设置到 localStorage
      localStorage.setItem('proxySettings', JSON.stringify(settings.value))
      ElMessage.success('设置已保存')
    }

    const resetSettings = () => {
      settings.value = {
        defaultPort: 8888,
        maxConnections: 100,
        timeout: 30,
        logLevel: 'INFO',
        enableLogging: true
      }
      ElMessage.info('设置已重置')
    }

    onMounted(() => {
      // 从 localStorage 加载设置
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
