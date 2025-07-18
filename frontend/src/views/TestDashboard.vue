<template>
  <div class="test-dashboard">
    <h1>Test Dashboard</h1>
    <p>This is a test page to verify the frontend is working.</p>
    <el-button type="primary">Test Button</el-button>
    <div>
      <h2>Proxy Status:</h2>
      <pre>{{ JSON.stringify(proxyStatus, null, 2) }}</pre>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'TestDashboard',
  setup() {
    const proxyStatus = ref({
      running: true,
      port: 8888,
      connections: 0,
      total_bytes: 0
    })

    const fetchProxyStatus = async () => {
      try {
        const response = await fetch('/api/proxy/status')
        const data = await response.json()
        proxyStatus.value = { ...data, running: true }
        console.log('Fetched proxy status:', data)
      } catch (error) {
        console.error('Failed to fetch proxy status:', error)
      }
    }

    onMounted(() => {
      console.log('Test Dashboard mounted')
      fetchProxyStatus()
    })

    return {
      proxyStatus
    }
  }
}
</script>

<style scoped>
.test-dashboard {
  padding: 20px;
}

pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
}
</style>
