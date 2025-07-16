<template>
  <div class="dashboard">
    <div class="header">
      <div class="logo">BabelMesh</div>
      <div class="user-info">
        <div v-if="userInfo.isLoggedIn" class="user-dropdown" @click="toggleDropdown">
          <span class="username">Welcome, {{ userInfo.username }}</span>
          <span class="dropdown-arrow">▼</span>
          <div v-if="showDropdown" class="dropdown-menu">
            <div class="dropdown-item" @click="logout">
              <span class="logout-icon">🚪</span>
              Logout
            </div>
          </div>
        </div>
        <a v-else @click.prevent="goLogin" href="/login" class="login-link">
          Not logged in
        </a>
      </div>
    </div>
    <div class="main-content">
      <h2 class="center-title">Please select a proxy node</h2>
      <div class="node-cards">
        <div class="node-card" @click="selectNode('Europe')">
          <div class="node-title">Europe Node</div>
        </div>
        <div class="node-card" @click="selectNode('North America')">
          <div class="node-title">North America Node</div>
        </div>
        <div class="node-card" @click="selectNode('Oceania')">
          <div class="node-title">Oceania Node</div>
        </div>
      </div>
      <div v-if="selectedMessage" class="node-message">
        {{ selectedMessage }}
      </div>
    </div>
    <!-- 左下角半透明logo背景，替换src为你的logo图片路径，如 /logo.png 或 @/assets/logo.png -->
    <div class="background-logo">
      <img src="/BabelMesh_logo.jpg" alt="BabelMesh Logo" />
      <!-- TODO: 将你的logo图片放到 public 目录下，并将 src 替换为实际路径 -->
    </div>
    <div id="particles-js" class="particles-bg"></div>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      userInfo: {
        username: '',
        isLoggedIn: false
      },
      showDropdown: false,
      selectedMessage: '',
    };
  },
  mounted() {
    this.loadUserInfo();
    document.addEventListener('click', this.handleClickOutside);
    if (window.particlesJS) {
      window.particlesJS.load('particles-js', '/particles.json');
    } else {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js';
      script.onload = () => {
        window.particlesJS.load('particles-js', '/particles.json');
      };
      document.body.appendChild(script);
    }
  },
  beforeDestroy() {
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
      localStorage.removeItem('user');
      this.userInfo = {
        username: '',
        isLoggedIn: false
      };
      this.showDropdown = false;
      this.showLogoutMessage();
    },
    handleClickOutside(event) {
      const dropdown = this.$el.querySelector('.user-dropdown');
      if (dropdown && !dropdown.contains(event.target)) {
        this.showDropdown = false;
      }
    },
    showLogoutMessage() {
      const message = document.createElement('div');
      message.textContent = 'Logout successful';
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
      setTimeout(() => {
        if (message.parentNode) {
          message.parentNode.removeChild(message);
        }
        if (style.parentNode) {
          style.parentNode.removeChild(style);
        }
      }, 3000);
    },
    selectNode(node) {
      if (!this.userInfo.isLoggedIn) {
        this.selectedMessage = 'Please login first';
        return;
      }
      if (node === 'Europe') {
        this.selectedMessage = 'Europe node';
      } else if (node === 'North America') {
        this.selectedMessage = 'North America node';
      } else if (node === 'Oceania') {
        this.selectedMessage = 'Oceania node';
      }
    },
  },
};
</script>

<style scoped>
.dashboard {
  padding: 40px;
  text-align: center;
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  /* 更明显的蓝紫渐变背景 */
  background: linear-gradient(135deg, #0a2342 0%, #1e3c72 35%, #7b2ff2 70%, #2575fc 100%);
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
  position: relative;
}
.logo {
  font-size: 2em;
  font-weight: bold;
  color: #fff;
  letter-spacing: 2px;
  flex: 1;
  text-align: left;
  text-shadow: 0 4px 24px #1e90ff, 0 1px 0 #222;
  font-family: 'Orbitron', 'Segoe UI', 'Arial', sans-serif;
}
.user-info {
  display: flex;
  align-items: center;
  flex: 1;
  justify-content: flex-end;
}
.main-content {
  margin-top: 56px;
}
.center-title {
  text-align: center;
  margin: 0 0 32px 0;
  font-size: 2em;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1.5px;
  text-shadow: 0 2px 16px #1e90ff, 0 1px 0 #222;
  font-family: 'Orbitron', 'Segoe UI', 'Arial', sans-serif;
}
.node-cards {
  margin: 32px 0;
  display: flex;
  justify-content: center;
  gap: 40px;
}
.node-card {
  background: rgba(20, 40, 80, 0.85);
  border: 2px solid #3b82f6;
  border-radius: 18px;
  box-shadow: 0 4px 32px rgba(64,158,255,0.18), 0 0 24px 2px #1e3c72 inset;
  padding: 40px 32px 32px 32px;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s, transform 0.2s;
  position: relative;
}
.node-card:hover {
  box-shadow: 0 8px 40px 0 #ff9800, 0 0 32px 4px #3b82f6 inset;
  border-color: #ff9800;
  transform: translateY(-6px) scale(1.04);
}
.node-title {
  font-size: 1.3em;
  font-weight: 700;
  margin-bottom: 22px;
  color: #fff;
  letter-spacing: 1px;
  text-shadow: 0 2px 12px #3b82f6, 0 1px 0 #222;
}
.el-button {
  background: linear-gradient(90deg, #1e90ff 0%, #3b82f6 100%);
  color: #fff !important;
  border: none;
  border-radius: 8px;
  font-size: 1.08em;
  font-weight: 600;
  letter-spacing: 1px;
  box-shadow: 0 2px 12px #1e90ff, 0 0 8px 2px #fff8;
  text-shadow: 0 0 8px #fff, 0 0 16px #3b82f6;
  transition: background 0.2s, box-shadow 0.2s, color 0.2s;
}
.el-button:hover {
  background: linear-gradient(90deg, #ff9800 0%, #ffb347 100%);
  color: #fff !important;
  box-shadow: 0 4px 24px #ff9800, 0 0 12px 2px #fff8;
  text-shadow: 0 0 12px #fff, 0 0 24px #ff9800;
}
.node-message {
  margin-top: 32px;
  font-size: 1.5em;
  color: #ff9800;
  text-shadow: 0 2px 12px #3b82f6, 0 1px 0 #222;
}
/* 用户名、下拉等细节白色/浅蓝 */
.username {
  color: #fff;
  font-weight: 500;
  text-shadow: 0 1px 8px #3b82f6;
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
  background: rgba(30,60,114,0.18);
}
.user-dropdown:hover {
  background-color: rgba(59, 130, 246, 0.18);
}
.dropdown-arrow {
  font-size: 12px;
  color: #fff;
  transition: transform 0.2s;
}
.user-dropdown:hover .dropdown-arrow {
  transform: rotate(180deg);
}
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: rgba(24, 26, 27, 0.98);
  border: 1px solid #3b82f6;
  border-radius: 8px;
  box-shadow: 0 4px 12px #1e90ff44;
  min-width: 140px;
  z-index: 1000;
  margin-top: 4px;
}
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: #fff;
  font-size: 14px;
  transition: background-color 0.2s;
  border-radius: 4px;
  margin: 4px;
}
.dropdown-item:hover {
  background-color: rgba(255, 152, 0, 0.18);
  color: #ff9800;
}
.logout-icon {
  font-size: 16px;
}
.login-link {
  color: #ff9800;
  text-decoration: underline;
  cursor: pointer;
  font-size: 1.08em;
  font-weight: 500;
  margin-left: 8px;
}
.login-link:hover {
  color: #fff;
}
.background-logo {
  position: fixed;
  right: 0;
  bottom: 0;
  z-index: 0;
  pointer-events: none;
  width: 40vw;
  min-width: 320px;
  max-width: 600px;
  opacity: 0.18;
}
.background-logo img {
  width: 100%;
  height: auto;
  display: block;
  filter: drop-shadow(0 8px 32px #1e90ff88);
}
.particles-bg {
  position: fixed;
  left: 0;
  top: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  pointer-events: none;
}
</style> 