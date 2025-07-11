<template>
  <b-card class="network-status">
    <template v-slot:header>
      <h3 class="mb-0">
        <span>网络状态</span>
        <b-spinner v-if="isConnecting" small class="ml-2" variant="primary" label="正在连接..."></b-spinner>
      </h3>
    </template>
    
    <b-row>
      <b-col md="4" class="font-weight-bold">连接状态</b-col>
      <b-col>
        <b-badge :variant="statusVariant">{{ statusText }}</b-badge>
      </b-col>
    </b-row>
    
    <b-row class="mt-2">
      <b-col md="4" class="font-weight-bold">服务ID</b-col>
      <b-col>{{ serviceId || '无活动连接' }}</b-col>
    </b-row>

    <b-row class="mt-2" v-if="isConnected">
      <b-col md="4" class="font-weight-bold">目标地址</b-col>
      <b-col>{{ targetUrl }}</b-col>
    </b-row>

    <b-row class="mt-2" v-if="isConnected">
      <b-col md="4" class="font-weight-bold">已连接时间</b-col>
      <b-col>{{ connectedTime }}</b-col>
    </b-row>

    <template v-slot:footer v-if="isConnected">
      <b-button variant="danger" size="sm" @click="disconnect">断开连接</b-button>
    </template>
  </b-card>
</template>

<script>
export default {
  name: 'NetworkStatus',
  props: {
    isConnecting: {
      type: Boolean,
      default: false
    },
    isConnected: {
      type: Boolean,
      default: false
    },
    serviceId: {
      type: String,
      default: ''
    },
    targetUrl: {
      type: String,
      default: ''
    },
    connectedAt: {
      type: Date,
      default: null
    }
  },
  computed: {
    statusText() {
      if (this.isConnecting) return '正在连接'
      if (this.isConnected) return '已连接'
      return '未连接'
    },
    statusVariant() {
      if (this.isConnecting) return 'warning'
      if (this.isConnected) return 'success'
      return 'secondary'
    },
    connectedTime() {
      if (!this.connectedAt) return ''
      
      const now = new Date()
      const diffMs = now - this.connectedAt
      const diffMins = Math.floor(diffMs / 60000)
      const diffSecs = Math.floor((diffMs % 60000) / 1000)
      
      return `${diffMins}分钟 ${diffSecs}秒`
    }
  },
  methods: {
    disconnect() {
      this.$emit('disconnect')
    }
  }
}
</script>
