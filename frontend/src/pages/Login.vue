<template>
  <div class="auth-page">
    <h2>User Login</h2>
    <form @submit.prevent="onLogin">
      <div class="form-row">
        <label for="login-username">Username</label>
        <input id="login-username" v-model="username" required autocomplete="username" />
      </div>
      <div class="form-row">
        <label for="login-password">Password</label>
        <input id="login-password" v-model="password" type="password" required autocomplete="current-password" />
      </div>
      <button type="submit">Login</button>
    </form>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="success" class="success">{{ success }}</div>
    <div class="switch-link">
      Don't have an account? <a @click.prevent="goRegister" href="/register">Register</a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      error: '',
      success: ''
    };
  },
  methods: {
    async onLogin() {
      this.error = '';
      this.success = '';
      try {
        const res = await fetch('/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          })
        });
        if (!res.ok) {
          const data = await res.json();
          this.error = data.detail || 'Login failed';
        } else {
          const data = await res.json();
          this.success = '登录成功！正在跳转到仪表板...';
          // 保存登录状态到 localStorage
          localStorage.setItem('user', JSON.stringify({
            username: this.username,
            isLoggedIn: true
          }));
          // 跳转到 Dashboard
          setTimeout(() => {
            this.$router.push('/');
          }, 1500);
        }
      } catch (e) {
        this.error = 'Network error';
      }
    },
    goRegister() {
      this.$router.push('/register');
    }
  }
};
</script>

<style scoped>
.auth-page {
  max-width: 340px;
  margin: 48px auto;
  background: #181a1b;
  padding: 32px 28px 24px 28px;
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.12);
  color: #e5e6e7;
  font-family: 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}
h2 {
  text-align: center;
  font-weight: 500;
  margin-bottom: 28px;
  color: #fff;
  letter-spacing: 1px;
}
form {
  margin-bottom: 10px;
}
.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}
label {
  width: 70px;
  color: #b0b3b8;
  font-size: 1em;
  margin-right: 10px;
  letter-spacing: 1px;
}
input {
  flex: 1;
  background: #232526;
  border: 1px solid #232526;
  color: #e5e6e7;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 1em;
  outline: none;
  transition: border 0.2s;
}
input:focus {
  border: 1.5px solid #3b82f6;
  background: #232526;
}
button {
  width: 100%;
  padding: 10px 0;
  background: linear-gradient(90deg, #232526 0%, #3b3b3b 100%);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 1.08em;
  letter-spacing: 1px;
  margin-top: 8px;
  cursor: pointer;
  transition: background 0.2s;
}
button:hover {
  background: linear-gradient(90deg, #232526 0%, #3b82f6 100%);
}
.error {
  color: #ef4444;
  margin-top: 10px;
  text-align: center;
}
.success {
  color: #22c55e;
  margin-top: 10px;
  text-align: center;
}
.switch-link {
  margin-top: 22px;
  text-align: center;
  font-size: 0.98em;
  color: #b0b3b8;
}
.switch-link a {
  color: #3b82f6;
  text-decoration: underline;
  cursor: pointer;
  margin-left: 4px;
}
</style> 