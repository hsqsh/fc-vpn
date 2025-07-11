<template>
  <div class="monitor">
    <b-container fluid>
      <h2 class="mb-4">
        <i class="fas fa-chart-line"></i>
        流量监控中心
      </h2>
      
      <TrafficMonitor />
    </b-container>
  </div>
</template>

<script>
import TrafficMonitor from '@/components/TrafficMonitor.vue'

export default {
  name: 'Monitor',
  components: {
    TrafficMonitor
  }
}
</script>

<style scoped>
.monitor {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px 0;
}

h2 {
  color: #2c3e50;
  font-weight: 600;
}
</style>
