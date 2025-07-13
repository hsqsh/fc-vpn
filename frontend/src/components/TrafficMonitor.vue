<template>
  <div class="traffic-monitor">
    <div class="traffic-stats">
      <div class="stat-item">
        <div class="stat-label">实时上行</div>
        <div class="stat-value">{{ formatBytes(status.total_traffic_up) }}</div>
        <div class="stat-rate">{{ formatRate(uploadRate) }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">实时下行</div>
        <div class="stat-value">{{ formatBytes(status.total_traffic_down) }}</div>
        <div class="stat-rate">{{ formatRate(downloadRate) }}</div>
      </div>
    </div>
    
    <div class="traffic-chart">
      <div class="chart-title">流量趋势</div>
      <div class="chart-container">
        <div class="chart-bar upload" :style="{ height: uploadPercentage + '%' }"></div>
        <div class="chart-bar download" :style="{ height: downloadPercentage + '%' }"></div>
      </div>
      <div class="chart-labels">
        <span>上传</span>
        <span>下载</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrafficMonitor',
  props: {
    status: {
      type: Object,
      default: () => ({
        active_connections: 0,
        total_connections: 0,
        total_traffic_up: 0,
        total_traffic_down: 0
      })
    }
  },
  data() {
    return {
      uploadRate: 0,
      downloadRate: 0,
      lastUpload: 0,
      lastDownload: 0,
      lastUpdate: Date.now()
    }
  },
  computed: {
    uploadPercentage() {
      const max = Math.max(this.status.total_traffic_up, this.status.total_traffic_down, 1)
      return (this.status.total_traffic_up / max) * 100
    },
    downloadPercentage() {
      const max = Math.max(this.status.total_traffic_up, this.status.total_traffic_down, 1)
      return (this.status.total_traffic_down / max) * 100
    }
  },
  watch: {
    status: {
      handler(newStatus) {
        this.updateRates(newStatus)
      },
      deep: true
    }
  },
  mounted() {
    this.lastUpload = this.status.total_traffic_up
    this.lastDownload = this.status.total_traffic_down
    this.lastUpdate = Date.now()
  },
  methods: {
    formatBytes(bytes, decimals = 2) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const dm = decimals < 0 ? 0 : decimals
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
    },
    formatRate(bytesPerSecond) {
      return this.formatBytes(bytesPerSecond) + '/s'
    },
    updateRates(newStatus) {
      const now = Date.now()
      const timeDiff = (now - this.lastUpdate) / 1000 // 转换为秒
      
      if (timeDiff > 0) {
        this.uploadRate = (newStatus.total_traffic_up - this.lastUpload) / timeDiff
        this.downloadRate = (newStatus.total_traffic_down - this.lastDownload) / timeDiff
      }
      
      this.lastUpload = newStatus.total_traffic_up
      this.lastDownload = newStatus.total_traffic_down
      this.lastUpdate = now
    }
  }
}
</script>

<style scoped>
.traffic-monitor {
  padding: 8px 0;
}
.traffic-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}
.stat-item {
  text-align: center;
  flex: 1;
}
.stat-label {
  font-size: 0.85em;
  color: #b0b3b8;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 1.1em;
  font-weight: 600;
  color: #e5e6e7;
  margin-bottom: 2px;
}
.stat-rate {
  font-size: 0.8em;
  color: #3b82f6;
}
.traffic-chart {
  margin-bottom: 16px;
}
.chart-title {
  font-size: 0.9em;
  color: #b0b3b8;
  margin-bottom: 8px;
}
.chart-container {
  display: flex;
  justify-content: center;
  align-items: end;
  height: 60px;
  gap: 8px;
  margin-bottom: 8px;
}
.chart-bar {
  width: 20px;
  border-radius: 2px;
  transition: height 0.3s ease;
}
.chart-bar.upload {
  background: linear-gradient(to top, #3b82f6, #60a5fa);
}
.chart-bar.download {
  background: linear-gradient(to top, #22c55e, #4ade80);
}
.chart-labels {
  display: flex;
  justify-content: center;
  gap: 16px;
  font-size: 0.8em;
  color: #b0b3b8;
}
.connection-info {
  font-size: 0.9em;
}
.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}
.info-row .label {
  color: #b0b3b8;
}
.info-row .value {
  color: #e5e6e7;
  font-weight: 500;
}
</style> 