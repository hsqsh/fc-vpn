<template>
  <div class="profile">
    <b-container>
      <h2 class="mb-4">用户资料</h2>
      
      <b-card v-if="user">
        <b-card-title>个人信息</b-card-title>
        <b-row>
          <b-col md="3" class="font-weight-bold">用户名</b-col>
          <b-col>{{ user.username }}</b-col>
        </b-row>
        <b-row class="mt-2" v-if="user.email">
          <b-col md="3" class="font-weight-bold">电子邮箱</b-col>
          <b-col>{{ user.email }}</b-col>
        </b-row>
        <b-row class="mt-2">
          <b-col md="3" class="font-weight-bold">账户余额</b-col>
          <b-col>${{ user.account_balance }}</b-col>
        </b-row>
      </b-card>

      <b-card class="mt-4">
        <template v-slot:header>
          <h3 class="mb-0">服务记录</h3>
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
export default {
  name: 'Profile',
  data() {
    return {
      fields: [
        { key: 'service_id', label: '服务ID' },
        { key: 'target', label: '目标网址' },
        { key: 'timestamp', label: '请求时间' },
        { key: 'status', label: '状态' },
        { key: 'cost', label: '费用 ($)' }
      ]
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    serviceHistory() {
      return this.$store.state.user.service_history || []
    }
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString()
    }
  },
  created() {
    this.$store.dispatch('fetchUserProfile')
  }
}
</script>
