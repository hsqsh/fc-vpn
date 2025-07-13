<template>
  <div class="network-status">
    <div class="status-indicator">
      <div class="status-dot" :class="statusClass"></div>
      <span class="status-text">{{ statusText }}</span>
    </div>
    <div class="connection-info">
      <div class="info-item">
        <span class="label">连接质量:</span>
        <span class="value">{{ connectionQuality }}</span>
      </div>
      <div class="info-item">
        <span class="label">延迟:</span>
        <span class="value">{{ latency }}ms</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NetworkStatus',
  props: {
    status: {
      type: String,
      default: 'online',
      validator: value => ['online', 'offline', 'connecting', 'error'].includes(value)
    }
  },
  computed: {
    statusClass() {
      return {
        'online': this.status === 'online',
        'offline': this.status === 'offline',
        'connecting': this.status === 'connecting',
        'error': this.status === 'error'
      }
    },
    statusText() {
      const statusMap = {
        'online': '在线',
        'offline': '离线',
        'connecting': '连接中',
        'error': '连接错误'
      }
      return statusMap[this.status] || '未知'
    },
    connectionQuality() {
      // 模拟连接质量检测
      if (this.status === 'online') {
        return '良好'
      } else if (this.status === 'connecting') {
        return '检测中'
      } else {
        return '无连接'
      }
    },
    latency() {
      // 模拟延迟检测
      if (this.status === 'online') {
        return Math.floor(Math.random() * 50) + 10 // 10-60ms
      } else {
        return '--'
      }
    }
  }
}
</script>

<style scoped>
.network-status {
  padding: 8px 0;
}
.status-indicator {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
  animation: pulse 2s infinite;
}
.status-dot.online {
  background-color: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.4);
}
.status-dot.offline {
  background-color: #ef4444;
}
.status-dot.connecting {
  background-color: #f59e42;
  animation: pulse 1s infinite;
}
.status-dot.error {
  background-color: #ef4444;
  animation: pulse 0.5s infinite;
}
.status-text {
  font-weight: 500;
  color: #e5e6e7;
}
.connection-info {
  font-size: 0.9em;
}
.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}
.info-item .label {
  color: #b0b3b8;
}
.info-item .value {
  color: #e5e6e7;
  font-weight: 500;
}
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style> 