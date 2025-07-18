<template>
  <div class="pod-monitor">    <!-- Page Header -->
    <div class="page-header">
      <h1><el-icon><Monitor /></el-icon> Kubernetes Pod Monitor Dashboard</h1>
      <p class="subtitle">Real-time monitoring of Pod status and resource usage in the cluster</p>
    </div>    <!-- Cluster Overview -->
    <el-row :gutter="20" class="cluster-overview">
      <el-col :span="6">
        <el-card class="overview-card pods-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ totalPods }}</div>
              <div class="stat-label">Pod number</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card running-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><VideoPlay /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ runningPods }}</div>
              <div class="stat-label">running</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card pending-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ pendingPods }}</div>
              <div class="stat-label">waiting</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card failed-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ failedPods }}</div>
              <div class="stat-label">Failed</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>    <!-- Namespace Filter -->
    <el-row style="margin: 20px 0;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span><el-icon><Filter /></el-icon> Filters</span>
          </template>
          <div class="filter-controls">
            <el-form :model="filters" inline>
              <el-form-item label="Namespace:">
                <el-select v-model="filters.namespace" placeholder="Select Namespace" style="width: 200px;">
                  <el-option label="All" value="" />
                  <el-option 
                    v-for="ns in namespaces" 
                    :key="ns" 
                    :label="ns" 
                    :value="ns" 
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="Status:">
                <el-select v-model="filters.status" placeholder="Select Status" style="width: 150px;">
                  <el-option label="All" value="" />
                  <el-option label="Running" value="Running" />
                  <el-option label="Pending" value="Pending" />                  <el-option label="Succeeded" value="Succeeded" />
                  <el-option label="Failed" value="Failed" />
                </el-select>
              </el-form-item>
              <el-form-item label="Search:">
                <el-input 
                  v-model="filters.search" 
                  placeholder="Enter Pod Name" 
                  style="width: 200px;"
                  clearable
                />
              </el-form-item>              <el-form-item>
                <el-button type="primary" @click="refreshData" :loading="loading">
                  <el-icon><Refresh /></el-icon>
                  Refresh
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>    <!-- Pod List -->
    <el-row>
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="table-header">
              <span><el-icon><List /></el-icon> Pod Details</span>
              <div class="header-actions">
                <el-button-group>
                  <el-button 
                    :type="viewMode === 'table' ? 'primary' : 'default'"
                    @click="viewMode = 'table'"
                    size="small"
                  >                    <el-icon><Grid /></el-icon>
                    Table View
                  </el-button>
                  <el-button 
                    :type="viewMode === 'card' ? 'primary' : 'default'"
                    @click="viewMode = 'card'"
                    size="small"
                  >
                    <el-icon><Postcard /></el-icon>
                    Card View
                  </el-button>
                </el-button-group>
              </div>
            </div>
          </template>          <!-- Table View -->
          <div v-if="viewMode === 'table'">
            <el-table 
              :data="filteredPods" 
              style="width: 100%"
              :loading="loading"
              stripe
              highlight-current-row
            >
              <el-table-column prop="name" label="Pod Name" min-width="200">
                <template #default="scope">
                  <div class="pod-name">
                    <el-icon :class="getStatusIcon(scope.row.status)"></el-icon>
                    <span>{{ scope.row.name }}</span>
                  </div>
                </template>
              </el-table-column>              <el-table-column prop="namespace" label="Namespace" width="120">
                <template #default="scope">
                  <el-tag size="small">{{ scope.row.namespace }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="Status" width="100">
                <template #default="scope">
                  <el-tag :type="getStatusType(scope.row.status)" size="small">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="node" label="Node" width="150" />              <el-table-column label="CPU Usage" width="120">
                <template #default="scope">
                  <el-progress 
                    :percentage="scope.row.cpu.percentage"
                    :status="scope.row.cpu.percentage > 80 ? 'exception' : 'success'"
                    :stroke-width="8"
                  />
                  <div class="resource-text">{{ scope.row.cpu.used }}/{{ scope.row.cpu.limit }}</div>
                </template>
              </el-table-column>
              <el-table-column label="Memory Usage" width="120">
                <template #default="scope">
                  <el-progress 
                    :percentage="scope.row.memory.percentage"
                    :status="scope.row.memory.percentage > 80 ? 'exception' : 'success'"
                    :stroke-width="8"
                  />
                  <div class="resource-text">{{ scope.row.memory.used }}/{{ scope.row.memory.limit }}</div>
                </template>
              </el-table-column>              <el-table-column prop="restarts" label="Restarts" width="100" align="center" />
              <el-table-column prop="age" label="Age" width="120" />
              <el-table-column label="Actions" width="180" fixed="right">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="viewPodDetails(scope.row)">
                    <el-icon><View /></el-icon>
                    Details
                  </el-button>
                  <el-button type="success" size="small" @click="viewLogs(scope.row)">
                    <el-icon><Document /></el-icon>
                    Logs
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- Card View -->
          <div v-if="viewMode === 'card'" class="pods-grid">
            <div 
              v-for="pod in filteredPods" 
              :key="pod.name"
              class="pod-card"
              :class="[`pod-${pod.status.toLowerCase()}`]"
            >
              <div class="pod-card-header">
                <div class="pod-title">
                  <el-icon :class="getStatusIcon(pod.status)"></el-icon>
                  <span class="pod-name-text">{{ pod.name }}</span>
                </div>
                <el-tag :type="getStatusType(pod.status)" size="small">
                  {{ pod.status }}
                </el-tag>
              </div>
              
              <div class="pod-card-content">                <div class="pod-info">
                  <div class="info-item">
                    <span class="info-label">Namespace:</span>
                    <el-tag size="small">{{ pod.namespace }}</el-tag>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Node:</span>
                    <span>{{ pod.node }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Age:</span>
                    <span>{{ pod.age }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Restarts:</span>
                    <el-tag :type="pod.restarts > 0 ? 'warning' : 'success'" size="small">
                      {{ pod.restarts }}
                    </el-tag>
                  </div>
                </div>
                
                <div class="resource-usage">
                  <div class="resource-item">
                    <span class="resource-label">CPU Usage</span>
                    <el-progress 
                      :percentage="pod.cpu.percentage"
                      :status="pod.cpu.percentage > 80 ? 'exception' : 'success'"
                      :stroke-width="6"
                    />
                    <span class="resource-text">{{ pod.cpu.used }}/{{ pod.cpu.limit }}</span>
                  </div>
                  <div class="resource-item">
                    <span class="resource-label">Memory Usage</span>
                    <el-progress 
                      :percentage="pod.memory.percentage"
                      :status="pod.memory.percentage > 80 ? 'exception' : 'success'"
                      :stroke-width="6"
                    />
                    <span class="resource-text">{{ pod.memory.used }}/{{ pod.memory.limit }}</span>
                  </div>
                </div>
              </div>
              
              <div class="pod-card-actions">
                <el-button type="primary" size="small" @click="viewPodDetails(pod)">
                  <el-icon><View /></el-icon>
                  Details
                </el-button>
                <el-button type="success" size="small" @click="viewLogs(pod)">
                  <el-icon><Document /></el-icon>
                  Logs
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Pod Details Dialog -->
    <el-dialog 
      v-model="showPodDialog" 
      :title="`Pod Details - ${selectedPod?.name}`"
      width="80%"
      top="5vh"
    >
      <div v-if="selectedPod" class="pod-details">        <el-tabs v-model="activeTab">
          <el-tab-pane label="Basic Info" name="info">
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">Pod Name:</span>
                <span class="detail-value">{{ selectedPod.name }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Namespace:</span>
                <span class="detail-value">{{ selectedPod.namespace }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Status:</span>
                <el-tag :type="getStatusType(selectedPod.status)">{{ selectedPod.status }}</el-tag>
              </div>
              <div class="detail-item">
                <span class="detail-label">Node:</span>
                <span class="detail-value">{{ selectedPod.node }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">IP Address:</span>
                <span class="detail-value">{{ selectedPod.ip }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Created:</span>
                <span class="detail-value">{{ selectedPod.created }}</span>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="Resource Usage" name="resources">
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="resource-chart">
                  <h4>CPU Usage Trend</h4>
                  <v-chart :option="cpuChartOption" style="height: 200px;" />
                </div>
              </el-col>
              <el-col :span="12">
                <div class="resource-chart">
                  <h4>Memory Usage Trend</h4>
                  <v-chart :option="memoryChartOption" style="height: 200px;" />
                </div>
              </el-col>
            </el-row>
          </el-tab-pane>
            <el-tab-pane label="Container Info" name="containers">
            <el-table :data="selectedPod.containers" style="width: 100%">
              <el-table-column prop="name" label="Container Name" />
              <el-table-column prop="image" label="Image" />
              <el-table-column prop="status" label="Status">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 'Running' ? 'success' : 'danger'">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="restarts" label="Restarts" />
              <el-table-column prop="ready" label="Ready">
                <template #default="scope">
                  <el-tag :type="scope.row.ready ? 'success' : 'warning'">
                    {{ scope.row.ready ? 'Yes' : 'No' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>    <!-- Log Viewer Dialog -->
    <el-dialog 
      v-model="showLogsDialog" 
      :title="`Pod Logs - ${selectedPod?.name}`"
      width="90%"
      top="5vh"
    >
      <div class="logs-container">
        <div class="logs-toolbar">
          <el-button type="primary" size="small" @click="refreshLogs">
            <el-icon><Refresh /></el-icon>
            Refresh Logs
          </el-button>
          <el-button type="success" size="small" @click="downloadLogs">
            <el-icon><Download /></el-icon>
            Download Logs
          </el-button>
          <el-switch 
            v-model="autoRefreshLogs" 
            active-text="Auto Refresh"
            style="margin-left: 20px;"
          />
        </div>
        <div class="logs-content">
          <pre v-for="(log, index) in podLogs" :key="index" class="log-line">{{ log }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Monitor, Box, VideoPlay, Clock, WarningFilled, Filter, Refresh, 
  List, Grid, Postcard, View, Document, Download 
} from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

export default {
  name: 'PodMonitor',
  components: {
    VChart,
    Monitor, Box, VideoPlay, Clock, WarningFilled, Filter, Refresh,
    List, Grid, Postcard, View, Document, Download
  },
  setup() {
    const loading = ref(false)
    const viewMode = ref('table')
    const showPodDialog = ref(false)
    const showLogsDialog = ref(false)
    const selectedPod = ref(null)
    const activeTab = ref('info')
    const autoRefreshLogs = ref(false)
    
    const filters = ref({
      namespace: '',
      status: '',
      search: ''
    })

    // Mock Pod data
    const pods = ref([
      {
        name: 'nginx-deployment-7848d4b86f-9k2xc',
        namespace: 'default',
        status: 'Running',
        node: 'worker-node-1',
        ip: '10.244.1.10',
        age: '2d 14h',
        restarts: 0,
        created: '2024-07-13 10:30:25',
        cpu: { used: '150m', limit: '500m', percentage: 30 },
        memory: { used: '128Mi', limit: '256Mi', percentage: 50 },
        containers: [
          { name: 'nginx', image: 'nginx:1.21', status: 'Running', restarts: 0, ready: true }
        ]
      },
      {
        name: 'redis-master-6dd5c4b9f-x7k9s',
        namespace: 'database',
        status: 'Running',
        node: 'worker-node-2',
        ip: '10.244.2.15',
        age: '5d 8h',
        restarts: 1,
        created: '2024-07-10 09:15:42',
        cpu: { used: '200m', limit: '300m', percentage: 67 },
        memory: { used: '450Mi', limit: '512Mi', percentage: 88 },
        containers: [
          { name: 'redis', image: 'redis:6.2', status: 'Running', restarts: 1, ready: true }
        ]
      },
      {
        name: 'api-server-84d9c5b6f8-m4n2p',
        namespace: 'app',
        status: 'Running',
        node: 'worker-node-1',
        ip: '10.244.1.25',
        age: '1d 3h',
        restarts: 0,
        created: '2024-07-14 12:45:18',
        cpu: { used: '100m', limit: '1000m', percentage: 10 },
        memory: { used: '200Mi', limit: '1Gi', percentage: 20 },
        containers: [
          { name: 'api-server', image: 'myapp:v1.2.3', status: 'Running', restarts: 0, ready: true },
          { name: 'sidecar', image: 'sidecar:latest', status: 'Running', restarts: 0, ready: true }
        ]
      },
      {
        name: 'frontend-web-5f6d8c7b9-qt8rw',
        namespace: 'app',
        status: 'Pending',
        node: '-',
        ip: '-',
        age: '5m',
        restarts: 0,
        created: '2024-07-15 16:20:12',
        cpu: { used: '0m', limit: '500m', percentage: 0 },
        memory: { used: '0Mi', limit: '512Mi', percentage: 0 },
        containers: [
          { name: 'frontend', image: 'frontend:v2.1.0', status: 'Waiting', restarts: 0, ready: false }
        ]
      },
      {
        name: 'worker-job-1689423600-xz9k5',
        namespace: 'jobs',
        status: 'Failed',
        node: 'worker-node-3',
        ip: '10.244.3.8',
        age: '2h',
        restarts: 3,
        created: '2024-07-15 14:00:00',
        cpu: { used: '0m', limit: '200m', percentage: 0 },
        memory: { used: '0Mi', limit: '128Mi', percentage: 0 },
        containers: [
          { name: 'worker', image: 'worker:v1.0.0', status: 'Error', restarts: 3, ready: false }
        ]
      },
      {
        name: 'monitoring-prometheus-0',
        namespace: 'monitoring',
        status: 'Running',
        node: 'master-node-1',
        ip: '10.244.0.50',
        age: '7d 12h',
        restarts: 0,
        created: '2024-07-08 08:30:00',
        cpu: { used: '800m', limit: '1000m', percentage: 80 },
        memory: { used: '1.8Gi', limit: '2Gi', percentage: 90 },
        containers: [
          { name: 'prometheus', image: 'prom/prometheus:v2.40.0', status: 'Running', restarts: 0, ready: true }
        ]
      }
    ])

    const podLogs = ref([
      '[2024-07-15 16:25:30] INFO Starting application...',
      '[2024-07-15 16:25:31] INFO Loading configuration from /etc/config/app.yaml',
      '[2024-07-15 16:25:32] INFO Database connection established',
      '[2024-07-15 16:25:33] INFO Server listening on port 8080',
      '[2024-07-15 16:25:45] INFO Received GET request for /health',
      '[2024-07-15 16:25:45] INFO Health check passed',
      '[2024-07-15 16:26:00] INFO Received POST request for /api/users',
      '[2024-07-15 16:26:01] INFO User created successfully',
      '[2024-07-15 16:26:15] WARN Database connection pool nearly full (8/10)',
      '[2024-07-15 16:26:30] INFO Garbage collection completed in 45ms'
    ])

    // Computed properties
    const namespaces = computed(() => {
      return [...new Set(pods.value.map(pod => pod.namespace))]
    })

    const totalPods = computed(() => pods.value.length)
    const runningPods = computed(() => pods.value.filter(pod => pod.status === 'Running').length)
    const pendingPods = computed(() => pods.value.filter(pod => pod.status === 'Pending').length)
    const failedPods = computed(() => pods.value.filter(pod => pod.status === 'Failed').length)

    const filteredPods = computed(() => {
      return pods.value.filter(pod => {
        if (filters.value.namespace && pod.namespace !== filters.value.namespace) return false
        if (filters.value.status && pod.status !== filters.value.status) return false
        if (filters.value.search && !pod.name.toLowerCase().includes(filters.value.search.toLowerCase())) return false
        return true
      })
    })

    const cpuChartOption = computed(() => ({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00']
      },
      yAxis: { type: 'value', name: 'CPU (%)' },
      series: [{
        name: 'CPU Usage',
        type: 'line',
        data: [25, 30, 28, 35, 32, 30, 33],
        smooth: true,
        lineStyle: { color: '#409EFF' },
        areaStyle: { color: 'rgba(64, 158, 255, 0.1)' }
      }]
    }))

    const memoryChartOption = computed(() => ({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00']
      },      yAxis: { type: 'value', name: 'Memory (%)' },
      series: [{
        name: 'Memory Usage',
        type: 'line',
        data: [45, 50, 48, 55, 52, 50, 53],
        smooth: true,
        lineStyle: { color: '#67C23A' },
        areaStyle: { color: 'rgba(103, 194, 58, 0.1)' }
      }]
    }))

    // Methods
    const getStatusType = (status) => {
      const statusMap = {
        'Running': 'success',
        'Pending': 'warning',
        'Succeeded': 'success',
        'Failed': 'danger',
        'Unknown': 'info'
      }
      return statusMap[status] || 'info'
    }

    const getStatusIcon = (status) => {
      const iconMap = {
        'Running': 'VideoPlay',
        'Pending': 'Clock',
        'Succeeded': 'CircleCheck',
        'Failed': 'CircleClose',
        'Unknown': 'QuestionFilled'
      }
      return iconMap[status] || 'QuestionFilled'
    }

    const refreshData = () => {
      loading.value = true      // Simulate data refresh
      setTimeout(() => {
        // Randomly update some data
        pods.value.forEach(pod => {
          if (pod.status === 'Running') {
            pod.cpu.percentage = Math.floor(Math.random() * 100)
            pod.memory.percentage = Math.floor(Math.random() * 100)
          }
        })
        loading.value = false
        ElMessage.success('Data refreshed')
      }, 1000)
    }

    const viewPodDetails = (pod) => {
      selectedPod.value = pod
      showPodDialog.value = true
    }

    const viewLogs = (pod) => {
      selectedPod.value = pod
      showLogsDialog.value = true
    }

    const refreshLogs = () => {
      // Simulate log refresh
      const newLog = `[${new Date().toISOString().slice(0, 19)}] INFO New log entry generated`
      podLogs.value.push(newLog)
      if (podLogs.value.length > 50) {
        podLogs.value.shift()
      }
      ElMessage.success('Logs refreshed')
    }

    const downloadLogs = () => {
      const content = podLogs.value.join('\n')
      const blob = new Blob([content], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${selectedPod.value?.name}-logs.txt`
      a.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('Log download completed')
    }

    let refreshInterval = null

    onMounted(() => {
      refreshData()
      // Auto refresh data every 30 seconds
      refreshInterval = setInterval(() => {
        if (!loading.value) {
          refreshData()
        }
      }, 30000)
    })

    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
    })

    return {
      loading,
      viewMode,
      showPodDialog,
      showLogsDialog,
      selectedPod,
      activeTab,
      autoRefreshLogs,
      filters,
      pods,
      podLogs,
      namespaces,
      totalPods,
      runningPods,
      pendingPods,
      failedPods,
      filteredPods,
      cpuChartOption,
      memoryChartOption,
      getStatusType,
      getStatusIcon,
      refreshData,
      viewPodDetails,
      viewLogs,
      refreshLogs,
      downloadLogs
    }
  }
}
</script>

<style scoped>
.pod-monitor {
  padding: 20px;
  max-width: 1400px;
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

.cluster-overview {
  margin-bottom: 20px;
}

.overview-card {
  height: 120px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.pods-card { border-left: 4px solid #409EFF; }
.running-card { border-left: 4px solid #67C23A; }
.pending-card { border-left: 4px solid #E6A23C; }
.failed-card { border-left: 4px solid #F56C6C; }

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 20px;
}

.stat-icon {
  font-size: 3rem;
  margin-right: 20px;
  opacity: 0.8;
}

.pods-card .stat-icon { color: #409EFF; }
.running-card .stat-icon { color: #67C23A; }
.pending-card .stat-icon { color: #E6A23C; }
.failed-card .stat-icon { color: #F56C6C; }

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #2c3e50;
  line-height: 1;
}

.stat-label {
  font-size: 1rem;
  color: #7f8c8d;
  margin-top: 5px;
}

.filter-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pod-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.resource-text {
  font-size: 0.8rem;
  color: #606266;
  margin-top: 2px;
}

.pods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.pod-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
  background: white;
}

.pod-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.pod-running { border-left: 4px solid #67C23A; }
.pod-pending { border-left: 4px solid #E6A23C; }
.pod-failed { border-left: 4px solid #F56C6C; }
.pod-succeeded { border-left: 4px solid #67C23A; }

.pod-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.pod-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pod-name-text {
  font-weight: bold;
  color: #2c3e50;
}

.pod-card-content {
  margin-bottom: 15px;
}

.pod-info {
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 5px 0;
}

.info-label {
  font-weight: bold;
  color: #606266;
}

.resource-usage {
  margin-top: 15px;
}

.resource-item {
  margin-bottom: 15px;
}

.resource-label {
  display: block;
  font-size: 0.9rem;
  color: #606266;
  margin-bottom: 5px;
}

.pod-card-actions {
  display: flex;
  gap: 10px;
}

.pod-card-actions .el-button {
  flex: 1;
}

.pod-details {
  min-height: 400px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.detail-label {
  font-weight: bold;
  color: #495057;
}

.detail-value {
  color: #2c3e50;
  font-family: 'Monaco', 'Consolas', monospace;
}

.resource-chart {
  text-align: center;
}

.resource-chart h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.logs-container {
  height: 500px;
  display: flex;
  flex-direction: column;
}

.logs-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.logs-content {
  flex: 1;
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 6px;
  overflow-y: auto;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
}

.log-line {
  margin: 0;
  padding: 2px 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

@media (max-width: 768px) {
  .pod-monitor {
    padding: 10px;
  }
  
  .pods-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .table-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
