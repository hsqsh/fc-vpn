<template>
  <div class="traffic-monitor">
    <b-card class="mb-4">
      <template v-slot:header>
        <h3 class="mb-0">
          <span>实时流量监控</span>
          <b-badge variant="success" class="ml-2" v-if="isConnected">实时</b-badge>
          <b-badge variant="secondary" class="ml-2" v-else>离线</b-badge>
        </h3>
      </template>

      <!-- 总览统计 -->
      <b-row class="mb-4">
        <b-col md="3">
          <b-card class="text-center h-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <h4>{{ formatBytes(summary.total_bytes_sent) }}</h4>
            <small>上传流量</small>
          </b-card>
        </b-col>
        <b-col md="3">
          <b-card class="text-center h-100" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
            <h4>{{ formatBytes(summary.total_bytes_received) }}</h4>
            <small>下载流量</small>
          </b-card>
        </b-col>
        <b-col md="3">
          <b-card class="text-center h-100" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white;">
            <h4>{{ summary.active_connections }}</h4>
            <small>活跃连接</small>
          </b-card>
        </b-col>
        <b-col md="3">
          <b-card class="text-center h-100" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white;">
            <h4>{{ summary.total_services }}</h4>
            <small>运行服务</small>
          </b-card>
        </b-col>
      </b-row>

      <!-- 流量图表 -->
      <b-row>
        <b-col md="6">
          <h5>流量趋势</h5>
          <apexchart 
            type="line" 
            height="300" 
            :options="trafficChartOptions" 
            :series="trafficChartSeries"
          ></apexchart>
        </b-col>
        <b-col md="6">
          <h5>连接统计</h5>
          <apexchart 
            type="donut" 
            height="300" 
            :options="connectionChartOptions" 
            :series="connectionChartSeries"
          ></apexchart>
        </b-col>
      </b-row>
    </b-card>

    <!-- 服务详情 -->
    <b-card>
      <template v-slot:header>
        <h4 class="mb-0">活跃服务详情</h4>
      </template>

      <b-table 
        :items="services" 
        :fields="serviceFields"
        responsive="sm"
        striped
        hover
        v-if="services.length > 0"
      >
        <template v-slot:cell(target_url)="data">
          <a :href="data.value" target="_blank" class="text-primary">{{ truncateUrl(data.value) }}</a>
        </template>
        
        <template v-slot:cell(uptime)="data">
          {{ formatUptime(data.item.stats.uptime_seconds) }}
        </template>
        
        <template v-slot:cell(bytes_sent)="data">
          {{ formatBytes(data.item.stats.bytes_sent) }}
        </template>
        
        <template v-slot:cell(bytes_received)="data">
          {{ formatBytes(data.item.stats.bytes_received) }}
        </template>
        
        <template v-slot:cell(connections)="data">
          <b-badge variant="info">{{ data.item.stats.connections_active }}</b-badge>
          /
          <b-badge variant="secondary">{{ data.item.stats.connections_total }}</b-badge>
        </template>
      </b-table>
      
      <p v-else class="text-muted">暂无活跃服务</p>
    </b-card>
  </div>
</template>

<script>
export default {
  name: 'TrafficMonitor',
  data() {
    return {
      monitoringData: null,
      isConnected: false,
      pollInterval: null,
      trafficHistory: [],
      serviceFields: [
        { key: 'service_id', label: '服务ID' },
        { key: 'target_url', label: '目标地址' },
        { key: 'uptime', label: '运行时间' },
        { key: 'bytes_sent', label: '上传' },
        { key: 'bytes_received', label: '下载' },
        { key: 'connections', label: '连接 (活跃/总计)' }
      ]
    }
  },
  computed: {
    summary() {
      return this.monitoringData ? this.monitoringData.summary : {
        total_services: 0,
        total_bytes_sent: 0,
        total_bytes_received: 0,
        total_connections: 0,
        active_connections: 0
      }
    },
    services() {
      return this.monitoringData ? this.monitoringData.services : []
    },
    trafficChartOptions() {
      return {
        chart: {
          id: 'traffic-chart',
          animations: {
            enabled: true,
            easing: 'linear',
            dynamicAnimation: {
              speed: 1000
            }
          },
          toolbar: {
            show: false
          }
        },
        xaxis: {
          type: 'datetime',
          range: 60000 * 5 // 显示最近5分钟
        },
        yaxis: {
          title: {
            text: '字节 (Bytes)'
          },
          labels: {
            formatter: (value) => this.formatBytes(value)
          }
        },
        stroke: {
          curve: 'smooth',
          width: 2
        },
        colors: ['#667eea', '#f093fb'],
        legend: {
          show: true
        }
      }
    },
    trafficChartSeries() {
      const now = new Date().getTime()
      const sent = this.summary.total_bytes_sent
      const received = this.summary.total_bytes_received
      
      return [
        {
          name: '上传流量',
          data: [[now, sent]]
        },
        {
          name: '下载流量', 
          data: [[now, received]]
        }
      ]
    },
    connectionChartOptions() {
      return {
        chart: {
          type: 'donut'
        },
        labels: ['活跃连接', '空闲'],
        colors: ['#43e97b', '#e0e0e0'],
        legend: {
          position: 'bottom'
        },
        plotOptions: {
          pie: {
            donut: {
              size: '70%'
            }
          }
        }
      }
    },
    connectionChartSeries() {
      const active = this.summary.active_connections
      const idle = Math.max(0, this.summary.total_connections - active)
      return [active, idle]
    }
  },
  methods: {
    async fetchMonitoringData() {
      try {
        const response = await this.$store.dispatch('fetchMonitoringData')
        this.monitoringData = response.data
        this.isConnected = true
        
        // 更新流量历史
        const now = new Date().getTime()
        this.trafficHistory.push({
          timestamp: now,
          sent: this.summary.total_bytes_sent,
          received: this.summary.total_bytes_received
        })
        
        // 只保留最近10个数据点
        if (this.trafficHistory.length > 10) {
          this.trafficHistory.shift()
        }
        
      } catch (error) {
        console.error('Failed to fetch monitoring data:', error)
        this.isConnected = false
      }
    },
    startPolling() {
      this.fetchMonitoringData()
      this.pollInterval = setInterval(() => {
        this.fetchMonitoringData()
      }, 3000) // 每3秒更新一次
    },
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },
    formatBytes(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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
      return url.length > 40 ? url.substring(0, 40) + '...' : url
    }
  },
  mounted() {
    this.startPolling()
  },
  beforeDestroy() {
    this.stopPolling()
  }
}
</script>

<style scoped>
.traffic-monitor {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.card {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: none;
  border-radius: 10px;
}

.table {
  font-size: 0.9rem;
}
</style>
