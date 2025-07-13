<template>
  <div class="dashboard">
    <div class="header">
      <h1>BabelNet Dashboard</h1>
      <div class="user-info">
        <div v-if="userInfo.isLoggedIn" class="user-dropdown" @click="toggleDropdown">
          <span class="username">
            Welcome, {{ userInfo.username }}
          </span>
          <span class="dropdown-arrow">▼</span>
          <div v-if="showDropdown" class="dropdown-menu">
            <div class="dropdown-item" @click="logout">
              <span class="logout-icon">🚪</span>
              退出登录
            </div>
          </div>
        </div>
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
        <h2>代理状态</h2>
        <div class="status-item">
          <span class="label">状态:</span>
          <span class="value" :class="proxyStatus.status">{{ proxyStatus.status }}</span>
        </div>
        <div class="status-item">
          <span class="label">代理IP:</span>
          <span class="value">{{ proxyIp }}</span>
        </div>
        <div class="status-item">
          <span class="label">活跃连接:</span>
          <span class="value">{{ proxyStatus.active_connections }}</span>
        </div>
      </div>
      <div class="card">
        <h2>流量监控</h2>
        <TrafficMonitor :status="proxyStatus" />
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
      showDropdown: false,
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
    // 添加点击外部关闭下拉菜单的事件监听
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeDestroy() {
    // 移除事件监听
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    loadUserInfo() {
      const user = localStorage.getItem('user');
      if (user) {
        try {
          this.userInfo = JSON.parse(user);
        } catch (e) {
          this.userInfo = {
            username: '',
            isLoggedIn: false
          };
        }
      }
    },
    goLogin() {
      this.$router.push('/login');
    },
    toggleDropdown() {
      this.showDropdown = !this.showDropdown;
    },
    logout() {
      // 清除本地存储的用户信息
      localStorage.removeItem('user');
      // 重置用户状态
      this.userInfo = {
        username: '',
        isLoggedIn: false
      };
      // 关闭下拉菜单
      this.showDropdown = false;
      // 显示退出成功消息
      this.showLogoutMessage();
    },
    handleClickOutside(event) {
      // 检查点击是否在下拉菜单外部
      const dropdown = this.$el.querySelector('.user-dropdown');
      if (dropdown && !dropdown.contains(event.target)) {
        this.showDropdown = false;
      }
    },
    showLogoutMessage() {
      // 创建一个临时的成功消息
      const message = document.createElement('div');
      message.textContent = '已成功退出登录';
      message.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #22c55e;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        font-size: 14px;
        animation: slideIn 0.3s ease-out;
      `;
      
      // 添加动画样式
      const style = document.createElement('style');
      style.textContent = `
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `;
      document.head.appendChild(style);
      
      document.body.appendChild(message);
      
      // 3秒后自动移除
      setTimeout(() => {
        if (message.parentNode) {
          message.parentNode.removeChild(message);
        }
        if (style.parentNode) {
          style.parentNode.removeChild(style);
        }
      }, 3000);
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
    },
    formatBytes(bytes, decimals = 2) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
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
.user-dropdown {
  position: relative;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background-color 0.2s;
}
.user-dropdown:hover {
  background-color: rgba(107, 114, 128, 0.1);
}
.dropdown-arrow {
  font-size: 12px;
  color: #6b7280;
  transition: transform 0.2s;
}
.user-dropdown:hover .dropdown-arrow {
  transform: rotate(180deg);
}
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: rgba(24, 26, 27, 0.95);
  border: 1px solid rgba(35, 37, 38, 0.8);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  min-width: 140px;
  z-index: 1000;
  margin-top: 4px;
}
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: #e5e6e7;
  font-size: 14px;
  transition: background-color 0.2s;
  border-radius: 4px;
  margin: 4px;
}
.dropdown-item:hover {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}
.logout-icon {
  font-size: 16px;
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
.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.status-item .label {
  color: #b0b3b8;
  font-size: 0.9em;
  font-weight: 400;
}
.status-item .value {
  color: #e5e6e7;
  font-weight: 500;
  font-size: 1em;
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