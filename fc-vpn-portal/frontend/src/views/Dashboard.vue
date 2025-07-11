<template>
  <div class="dashboard">
    <b-container>
      <h2 class="mb-4">VPN 服务控制台</h2>
      
      <b-row>
        <b-col md="8">
          <b-card>
            <b-form @submit.prevent="requestService">
              <b-form-group
                label="目标网址"
                label-for="target-url"
                description="请输入您想要访问的网址"
              >
                <b-form-input
                  id="target-url"
                  v-model="form.targetUrl"
                  type="text"
                  placeholder="例如: https://www.google.com"
                  required
                ></b-form-input>
              </b-form-group>

              <b-button type="submit" variant="primary" :disabled="loading || isConnected">
                {{ loading ? '请求中...' : '发起服务请求' }}
              </b-button>
            </b-form>
          </b-card>          <b-alert v-if="error" variant="danger" show class="mt-3">{{ error }}</b-alert>
          <b-alert v-if="success" variant="success" show class="mt-3">{{ success }}</b-alert>
          
          <!-- 监控预览 -->
          <b-card v-if="isConnected" class="mt-4">
            <template v-slot:header>
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">服务监控概览</h5>
                <b-button size="sm" variant="outline-primary" to="/monitor">
                  查看详细监控
                </b-button>
              </div>
            </template>
            <b-row>
              <b-col md="3" class="text-center">
                <h6 class="text-muted">运行时间</h6>
                <span class="h5">{{ formatUptime(connectionDuration) }}</span>
              </b-col>
              <b-col md="3" class="text-center">
                <h6 class="text-muted">状态</h6>
                <b-badge variant="success" class="h6">运行中</b-badge>
              </b-col>
              <b-col md="3" class="text-center">
                <h6 class="text-muted">服务ID</h6>
                <small class="text-monospace">{{ currentServiceId }}</small>
              </b-col>
              <b-col md="3" class="text-center">
                <h6 class="text-muted">目标</h6>
                <small>{{ truncateUrl(currentTargetUrl) }}</small>
              </b-col>
            </b-row>
          </b-card>
        </b-col>
        
        <b-col md="4">
          <NetworkStatus 
            :isConnecting="loading"
            :isConnected="isConnected"
            :serviceId="currentServiceId"
            :targetUrl="currentTargetUrl"
            :connectedAt="connectedAt"
            @disconnect="disconnectService"
          />
        </b-col>
      </b-row>

      <b-card class="mt-4">
        <template v-slot:header>
          <h3 class="mb-0">最近的服务请求</h3>
        </template>
        <b-table 
          :items="serviceHistory" 
          :fields="fields"
          responsive="sm"
          striped
          hover
          v-if="serviceHistory.length > 0"
        >
          <template v-slot:cell(timestamp)="data">
            {{ formatDate(data.value) }}
          </template>
        </b-table>
        <p v-else>暂无服务请求记录</p>
      </b-card>
    </b-container>
  </div>
</template>

<script>
import NetworkStatus from '@/components/NetworkStatus.vue'

export default {
  name: 'Dashboard',
  components: {
    NetworkStatus
  },
  data() {
    return {
      form: {
        targetUrl: ''
      },
      fields: [
        { key: 'service_id', label: '服务ID' },
        { key: 'target', label: '目标网址' },
        { key: 'timestamp', label: '请求时间' },
        { key: 'status', label: '状态' },
        { key: 'cost', label: '费用 ($)' }
      ],
      error: null,
      success: null,
      loading: false,
      isConnected: false,
      currentServiceId: '',
      currentTargetUrl: '',
      connectedAt: null
    }
  },  computed: {
    serviceHistory() {
      return this.$store.state.user.service_history || []
    },
    connectionDuration() {
      if (!this.connectedAt) return 0
      const now = new Date()
      const diffMs = now - this.connectedAt
      return Math.floor(diffMs / 1000) // 返回秒数
    }
  },
  methods: {    requestService() {
      this.loading = true
      this.error = null
      this.success = null
        this.$store.dispatch('requestService', this.form.targetUrl)
        .then(response => {
          const data = response.data
          this.success = `服务请求已创建，服务ID: ${data.service_id}`
          
          // 保存当前连接信息
          this.isConnected = true
          this.currentServiceId = data.service_id
          this.currentTargetUrl = this.form.targetUrl
          this.connectedAt = new Date()
          
          // 自动跳转到代理URL
          if (data.proxy_url) {
            this.success += ` - 正在跳转到目标网站...`
            setTimeout(() => {
              // 在新窗口中打开代理URL
              window.open(data.proxy_url, '_blank')
            }, 1000)
          }
          
          this.form.targetUrl = ''
          this.refreshUserProfile()
        }).catch(err => {
          this.error = (err.response && err.response.data && err.response.data.message) || '请求服务失败，请稍后重试'
        })
        .finally(() => {
          this.loading = false
        })
    },
      disconnectService() {
      if (!this.currentServiceId) {
        return
      }
      
      this.$store.dispatch('disconnectService', this.currentServiceId)
        .then(() => {
          this.isConnected = false
          this.currentServiceId = ''
          this.currentTargetUrl = ''
          this.connectedAt = null
          this.success = '已成功断开连接'
          this.refreshUserProfile()
        })
        .catch(err => {
          this.error = (err.response && err.response.data && err.response.data.message) || '断开连接失败'
        })
    },
    refreshUserProfile() {
      this.$store.dispatch('fetchUserProfile')
    },    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    formatUptime(seconds) {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      
      if (hours > 0) {
        return `${hours}时${minutes}分${secs}秒`
      } else if (minutes > 0) {
        return `${minutes}分${secs}秒`
      } else {
        return `${secs}秒`
      }
    },
    truncateUrl(url) {
      return url && url.length > 30 ? url.substring(0, 30) + '...' : url
    }
  },
  created() {
    this.refreshUserProfile()
  }
}
</script>
