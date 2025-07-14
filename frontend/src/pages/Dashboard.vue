<template>
  <div class="dashboard">
    <div class="header">
      <h2>Please select a proxy node</h2>
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
    <div class="node-cards">
      <div class="node-card" @click="selectNode('Europe')">
        <div class="node-title">Europe Node</div>
        <el-button type="primary" size="medium">Connect</el-button>
      </div>
      <div class="node-card" @click="selectNode('North America')">
        <div class="node-title">North America Node</div>
        <el-button type="primary" size="medium">Connect</el-button>
      </div>
      <div class="node-card" @click="selectNode('Oceania')">
        <div class="node-title">Oceania Node</div>
        <el-button type="primary" size="medium">Connect</el-button>
      </div>
    </div>
    <div v-if="selectedMessage" class="node-message">
      {{ selectedMessage }}
    </div>
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
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
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
.node-cards {
  margin: 32px 0;
  display: flex;
  justify-content: center;
  gap: 32px;
}
.node-card {
  background: #fff;
  border: 1.5px solid #e0e0e0;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  padding: 32px 28px 24px 28px;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.node-card:hover {
  box-shadow: 0 4px 16px rgba(64,158,255,0.15);
  border-color: #409EFF;
}
.node-title {
  font-size: 1.2em;
  font-weight: 600;
  margin-bottom: 18px;
  color: #222;
}
.node-message {
  margin-top: 32px;
  font-size: 1.5em;
  color: #409EFF;
}
</style> 