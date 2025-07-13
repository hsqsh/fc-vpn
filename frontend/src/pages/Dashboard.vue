<template>
  <div class="dashboard">
    <div class="header">
      <h1>FC-VPN Dashboard</h1>
      <div class="user-info">
        <span v-if="userInfo.isLoggedIn" class="username">
          Welcome, {{ userInfo.username }}
        </span>
        <a v-else @click.prevent="goLogin" href="/login" class="login-link">
          Not logged in
        </a>
      </div>
    </div>
    <div class="status-cards">
      <div class="card">
        <h2>网络状态</h2>
        <NetworkStatus :status="networkStatus" />
      </div>
      <div class="card">
        <h2>代理信息</h2>
        <div>代理IP: <b>{{ proxyIp }}</b></div>
        <div>活跃连接: <b>{{ proxyStatus.active_connections }}</b></div>
      </div>
      <div class="card">
        <h2>K8s Pods</h2>
        <div>数量: <b>{{ pods.length }}</b></div>
        <ul>
          <li v-for="pod in pods" :key="pod.name">
            {{ pod.name }} - <span :class="pod.status.toLowerCase()">{{ pod.status }}</span> ({{ pod.ip }})
          </li>
        </ul>
      </div>
      <div class="card">
        <h2>K8s Nodes</h2>
        <div>数量: <b>{{ nodes.length }}</b></div>
        <ul>
          <li v-for="node in nodes" :key="node.name">
            {{ node.name }} - <span :class="node.status.toLowerCase()">{{ node.status }}</span>
          </li>
        </ul>
      </div>
    </div>
    <div class="traffic-section">
      <h2>流量转发状态</h2>
      <TrafficMonitor :status="proxyStatus" />
    </div>
  </div>
</template>

<script>
import NetworkStatus from '../components/NetworkStatus.vue';
import TrafficMonitor from '../components/TrafficMonitor.vue';

export default {
  name: 'Dashboard',
  components: {
    NetworkStatus,
    TrafficMonitor
  },
  data() {
    return {
      userInfo: {
        username: '',
        isLoggedIn: false
      },
      networkStatus: 'online', // 可根据实际API动态获取
      proxyIp: '',
      proxyStatus: {
        active_connections: 0,
        total_connections: 0,
        total_traffic_up: 0,
        total_traffic_down: 0
      },
      pods: [],
      nodes: []
    };
  },
  mounted() {
    this.loadUserInfo();
    this.fetchProxyStatus();
    this.fetchPods();
    this.fetchNodes();
    this.fetchProxyIp();
  },
  methods: {
    loadUserInfo() {
      const user = localStorage.getItem('user');
      if (user) {
        this.userInfo = JSON.parse(user);
      }
    },
    goLogin() {
      this.$router.push('/login');
    },
    async fetchProxyStatus() {
      try {
        const res = await fetch('/proxy/status');
        if (res.ok) {
          this.proxyStatus = await res.json();
        }
      } catch (e) {}
    },
    async fetchPods() {
      try {
        const res = await fetch('/k8s/pods');
        if (res.ok) {
          const data = await res.json();
          this.pods = data.pods || [];
        }
      } catch (e) {}
    },
    async fetchNodes() {
      try {
        const res = await fetch('/k8s/nodes');
        if (res.ok) {
          const data = await res.json();
          this.nodes = data.nodes || [];
        }
      } catch (e) {}
    },
    async fetchProxyIp() {
      try {
        // 这里假设后端有 /proxy/ip 接口，返回 { ip: 'x.x.x.x' }
        const res = await fetch('/proxy/ip');
        if (res.ok) {
          const data = await res.json();
          this.proxyIp = data.ip;
        } else {
          // 兜底用本地IP
          this.proxyIp = window.location.hostname;
        }
      } catch (e) {
        this.proxyIp = window.location.hostname;
      }
    }
  }
};
</script>

<style scoped>
.dashboard {
  background: linear-gradient(180deg, #f8fafc 0%, #e5e7eb 20%, #d1d5db 40%, #9ca3af 60%, #6b7280 80%, #374151 100%);
  min-height: 100vh;
  padding: 32px;
  color: #e5e6e7;
  font-family: 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}
.header h1 {
  margin: 0;
  color: #6b7280;
  font-weight: 500;
  letter-spacing: 1px;
}
.user-info {
  display: flex;
  align-items: center;
}
.username {
  color: #6b7280;
  font-weight: 500;
}
.login-link {
  color: #b0b3b8;
  text-decoration: underline;
  cursor: pointer;
  font-size: 0.98em;
}
.login-link:hover {
  color: #3b82f6;
}
.status-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-bottom: 32px;
}
.card {
  background: rgba(24, 26, 27, 0.85);
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.12);
  padding: 24px 20px;
  min-width: 240px;
  flex: 1 1 240px;
  border: 1px solid rgba(35, 37, 38, 0.6);
}
.card h2 {
  font-size: 1.1rem;
  margin-bottom: 12px;
  color: #fff;
  font-weight: 500;
  letter-spacing: 0.5px;
}
.card ul {
  padding-left: 18px;
  margin: 0;
}
.card li {
  margin-bottom: 4px;
  font-size: 0.98em;
  color: #e5e6e7;
}
.card .running {
  color: #22c55e;
}
.card .pending, .card .notready {
  color: #f59e42;
}
.card .failed {
  color: #ef4444;
}
.traffic-section {
  background: rgba(24, 26, 27, 0.85);
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.12);
  padding: 24px 20px;
  border: 1px solid rgba(35, 37, 38, 0.6);
}
.traffic-section h2 {
  color: #fff;
  font-weight: 500;
  letter-spacing: 0.5px;
  margin-bottom: 16px;
}
</style> 