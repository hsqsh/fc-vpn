<template>
  <div class="ip-detection">
    <!-- Page Title -->
    <div class="page-header">      <h1><el-icon><Position /></el-icon> IP Detection Center</h1>
      <p class="subtitle">Detect your real IP and proxy IP to ensure proxy service is working properly</p>
    </div>

    <!-- Quick Detection Cards -->
    <el-row :gutter="20" class="quick-check">
      <el-col :span="12">        <el-card class="ip-card direct-ip">
          <template #header>
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>Direct IP Address</span>
              <el-button 
                type="primary" 
                size="small" 
                @click="checkDirectIP"
                :loading="loadingDirect"
                circle
              >
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="ip-content">
            <div class="ip-display">
              <span class="ip-label">Current IP:</span>
              <span class="ip-value" :class="{ 'loading': loadingDirect }">
                {{ loadingDirect ? 'Detecting...' : (directIP || 'Not detected') }}
              </span>
            </div>
            <div class="ip-status">
              <el-tag :type="directIP ? 'success' : 'info'" size="small">
                {{ directIP ? '✓ Obtained' : 'Pending' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
        <el-col :span="12">
        <el-card class="ip-card proxy-ip">
          <template #header>
            <div class="card-header">
              <el-icon><Connection /></el-icon>
              <span>Proxy IP Address</span>
              <el-button 
                type="primary" 
                size="small" 
                @click="checkProxyIP"
                :loading="loadingProxy"
                :disabled="!proxyRunning"
                circle
              >
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="ip-content">
            <div class="ip-display">
              <span class="ip-label">Proxy IP:</span>
              <span class="ip-value" :class="{ 'loading': loadingProxy }">
                {{ loadingProxy ? 'Detecting...' : (proxyIP || (proxyRunning ? 'Not detected' : 'Proxy not started')) }}
              </span>
            </div>
            <div class="ip-status">
              <el-tag 
                :type="proxyRunning ? (proxyIP ? 'success' : 'warning') : 'danger'" 
                size="small"
              >
                {{ proxyRunning ? (proxyIP ? '✓ Proxy valid' : 'Pending') : '⚠ Proxy not running' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>    <!-- Detailed Information Area -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>Detailed IP Information</span>
              <el-button 
                type="primary" 
                @click="getDetailedInfo"
                :loading="loadingDetails"
                size="small"
              >
                <el-icon><Search /></el-icon>
                Get Detailed Info
              </el-button>
            </div>
          </template>
          
          <div v-if="!detailsLoaded && !loadingDetails" class="no-details">
            <el-empty description="Click the button above to get detailed IP information" />
          </div>
          
          <div v-if="loadingDetails" class="loading-details">
            <el-skeleton :rows="5" animated />
          </div>
          
          <div v-if="detailsLoaded && !loadingDetails">          <el-row :gutter="20">
              <!-- Direct Connection Info -->
              <el-col :span="12">
                <div class="detail-section">
                  <h3><el-icon><Monitor /></el-icon> Direct Connection Info</h3>
                  <div v-if="directDetails.ip" class="detail-content">
                    <div class="detail-item">
                      <span class="label">IP Address:</span>
                      <span class="value">{{ directDetails.ip }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">Country:</span>
                      <span class="value">{{ directDetails.country || 'Unknown' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">Region:</span>
                      <span class="value">{{ directDetails.region || 'Unknown' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">City:</span>
                      <span class="value">{{ directDetails.city || 'Unknown' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">ISP:</span>
                      <span class="value">{{ directDetails.isp || 'Unknown' }}</span>
                    </div>
                  </div>
                  <div v-else class="error-content">
                    <el-alert title="Unable to get direct connection information" type="error" show-icon :closable="false" />
                  </div>
                </div>
              </el-col>
              
              <!-- Proxy Info -->
              <el-col :span="12">
                <div class="detail-section">                  <h3><el-icon><Connection /></el-icon> Proxy Information</h3>
                  <div v-if="proxyDetails.ip" class="detail-content">
                    <div class="detail-item">
                      <span class="label">IP Address:</span>
                      <span class="value">{{ proxyDetails.ip }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">Country:</span>
                      <span class="value">{{ proxyDetails.country || 'Unknown' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">Region:</span>
                      <span class="value">{{ proxyDetails.region || 'Unknown' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">City:</span>
                      <span class="value">{{ proxyDetails.city || 'Unknown' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">ISP:</span>
                      <span class="value">{{ proxyDetails.isp || 'Unknown' }}</span>
                    </div>
                  </div>
                  <div v-else-if="proxyDetails.status" class="info-content">
                    <el-alert :title="proxyDetails.status" type="warning" show-icon :closable="false" />
                  </div>
                  <div v-else class="error-content">
                    <el-alert title="Unable to get proxy information" type="error" show-icon :closable="false" />
                  </div>
                </div>
              </el-col>
            </el-row>
              <!-- Comparison Analysis -->
            <div v-if="comparison && Object.keys(comparison).length > 0" class="comparison-section">
              <h3><el-icon><TrendCharts /></el-icon> Comparison Analysis</h3>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="comparison-item">
                    <el-statistic
                      title="IP Changed"
                      :value="comparison.ip_changed ? 'Yes' : 'No'"
                      :value-style="{ color: comparison.ip_changed ? '#67C23A' : '#F56C6C' }"
                    />
                  </div>
                </el-col>                <el-col :span="8">
                  <div class="comparison-item">
                    <el-statistic
                      title="Location Changed"
                      :value="comparison.location_changed ? 'Yes' : 'No'"
                      :value-style="{ color: comparison.location_changed ? '#67C23A' : '#F56C6C' }"
                    />
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="comparison-item">
                    <el-statistic
                      title="Proxy Effective"
                      :value="comparison.proxy_effective ? 'Effective' : 'Ineffective'"
                      :value-style="{ color: comparison.proxy_effective ? '#67C23A' : '#F56C6C' }"
                    />
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Action Button Area -->
    <el-row style="margin-top: 20px;">      <el-col :span="24">
        <el-card>
          <template #header>
            <span><el-icon><Tools /></el-icon> Quick Actions</span>
          </template>
          <div class="action-buttons">
            <el-button 
              type="primary" 
              @click="checkAll"
              :loading="loadingAll"
              size="large"
            >
              <el-icon><Refresh /></el-icon>
              One-Click Detect All IPs
            </el-button>
            <el-button 
              type="success" 
              @click="copyResults"
              :disabled="!hasResults"
              size="large"
            >
              <el-icon><CopyDocument /></el-icon>
              Copy Detection Results
            </el-button>
            <el-button 
              type="warning" 
              @click="clearResults"
              :disabled="!hasResults"
              size="large"
            >
              <el-icon><Delete /></el-icon>
              Clear Results
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Position, Monitor, Connection, DataAnalysis, Search, 
  Refresh, TrendCharts, Tools, CopyDocument, Delete 
} from '@element-plus/icons-vue'

export default {
  name: 'IPDetection',
  components: {
    Position, Monitor, Connection, DataAnalysis, Search,
    Refresh, TrendCharts, Tools, CopyDocument, Delete
  },
  setup() {
    const directIP = ref('')
    const proxyIP = ref('')
    const proxyRunning = ref(false)
    
    const loadingDirect = ref(false)
    const loadingProxy = ref(false)
    const loadingDetails = ref(false)
    const loadingAll = ref(false)
    
    const detailsLoaded = ref(false)
    const directDetails = ref({})
    const proxyDetails = ref({})
    const comparison = ref({})

    const hasResults = computed(() => directIP.value || proxyIP.value)    // Detect direct IP
    const checkDirectIP = async () => {
      loadingDirect.value = true
      try {
        const response = await fetch('/api/ip/check')
        const data = await response.json()
        
        if (response.ok) {
          directIP.value = data.direct_ip || 'Unable to get'
          ElMessage.success('Direct IP detection completed')
        } else {
          ElMessage.error('Direct IP detection failed')
        }
      } catch (error) {
        ElMessage.error('网络错误: ' + error.message)
      } finally {
        loadingDirect.value = false
      }
    }

    // 检测代理IP
    const checkProxyIP = async () => {
      if (!proxyRunning.value) {
        ElMessage.warning('请先启动代理服务')
        return
      }
      
      loadingProxy.value = true
      try {
        const response = await fetch('/api/ip/check')
        const data = await response.json()
        
        if (response.ok) {
          proxyIP.value = data.proxy_ip || '无法获取'
          if (data.proxy_working) {
            ElMessage.success('代理IP检测完成')
          } else {
            ElMessage.warning('代理可能未正常工作')
          }
        } else {
          ElMessage.error('代理IP检测失败')
        }
      } catch (error) {
        ElMessage.error('网络错误: ' + error.message)
      } finally {
        loadingProxy.value = false
      }
    }

    // 获取详细信息
    const getDetailedInfo = async () => {
      loadingDetails.value = true
      try {
        const response = await fetch('/api/ip/details')
        const data = await response.json()
        
        if (response.ok) {
          directDetails.value = data.direct_info || {}
          proxyDetails.value = data.proxy_info || {}
          comparison.value = data.comparison || {}
          detailsLoaded.value = true
          ElMessage.success('详细信息获取完成')
        } else {
          ElMessage.error('详细信息获取失败')
        }
      } catch (error) {
        ElMessage.error('网络错误: ' + error.message)
      } finally {
        loadingDetails.value = false
      }
    }

    // 一键检测所有
    const checkAll = async () => {
      loadingAll.value = true
      try {
        await Promise.all([
          checkDirectIP(),
          checkProxyIP(),
          getDetailedInfo()
        ])
        ElMessage.success('所有检测完成')
      } catch (error) {
        ElMessage.error('检测过程中出现错误')
      } finally {
        loadingAll.value = false
      }
    }

    // 复制结果
    const copyResults = () => {
      const results = []
      if (directIP.value) results.push(`直连IP: ${directIP.value}`)
      if (proxyIP.value) results.push(`代理IP: ${proxyIP.value}`)
      
      if (directDetails.value.country) {
        results.push(`直连位置: ${directDetails.value.country} ${directDetails.value.city}`)
      }
      if (proxyDetails.value.country) {
        results.push(`代理位置: ${proxyDetails.value.country} ${proxyDetails.value.city}`)
      }
      
      const text = results.join('\n')
      navigator.clipboard.writeText(text).then(() => {
        ElMessage.success('结果已复制到剪贴板')
      }).catch(() => {
        ElMessage.error('复制失败')
      })
    }

    // 清空结果
    const clearResults = () => {
      directIP.value = ''
      proxyIP.value = ''
      directDetails.value = {}
      proxyDetails.value = {}
      comparison.value = {}
      detailsLoaded.value = false
      ElMessage.success('结果已清空')
    }

    // 检查代理状态
    const checkProxyStatus = async () => {
      try {
        const response = await fetch('/api/proxy/status')
        const data = await response.json()
        proxyRunning.value = data.running || false
      } catch (error) {
        console.error('Failed to check proxy status:', error)
      }
    }

    onMounted(() => {
      checkProxyStatus()
      // 定期检查代理状态
      setInterval(checkProxyStatus, 5000)
    })

    return {
      directIP,
      proxyIP,
      proxyRunning,
      loadingDirect,
      loadingProxy,
      loadingDetails,
      loadingAll,
      detailsLoaded,
      directDetails,
      proxyDetails,
      comparison,
      hasResults,
      checkDirectIP,
      checkProxyIP,
      getDetailedInfo,
      checkAll,
      copyResults,
      clearResults
    }
  }
}
</script>

<style scoped>
.ip-detection {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 2.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.subtitle {
  color: #7f8c8d;
  margin: 10px 0 0 0;
  font-size: 1.1rem;
}

.quick-check {
  margin-bottom: 20px;
}

.ip-card {
  height: 180px;
  transition: all 0.3s ease;
}

.ip-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.direct-ip {
  border-left: 4px solid #409EFF;
}

.proxy-ip {
  border-left: 4px solid #67C23A;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: bold;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ip-content {
  padding: 20px 0;
}

.ip-display {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.ip-label {
  font-weight: bold;
  color: #606266;
  min-width: 80px;
}

.ip-value {
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 1.1rem;
  color: #2c3e50;
  padding: 5px 10px;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
  min-width: 150px;
  text-align: center;
}

.ip-value.loading {
  color: #909399;
  font-style: italic;
}

.ip-status {
  display: flex;
  justify-content: center;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item .label {
  font-weight: bold;
  color: #606266;
  min-width: 80px;
}

.detail-item .value {
  color: #2c3e50;
  font-family: 'Monaco', 'Consolas', monospace;
  text-align: right;
}

.comparison-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px solid #f0f0f0;
}

.comparison-section h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.comparison-item {
  text-align: center;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.no-details, .loading-details {
  padding: 40px 0;
  text-align: center;
}

.error-content, .info-content {
  padding: 10px 0;
}

@media (max-width: 768px) {
  .ip-detection {
    padding: 10px;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .action-buttons .el-button {
    width: 100%;
    max-width: 300px;
  }
}
</style>
