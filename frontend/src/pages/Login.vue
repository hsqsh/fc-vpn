<template>
  <div class="dashboard-bg">
    <div class="auth-card">
      <div class="logo">BabelMesh</div>
      <h2 class="auth-title">User Login</h2>
      <form @submit.prevent="onLogin">
        <div class="form-row">
          <label for="login-username">Username</label>
          <input id="login-username" v-model="username" required autocomplete="username" />
        </div>
        <div class="form-row">
          <label for="login-password">Password</label>
          <input id="login-password" v-model="password" type="password" required autocomplete="current-password" />
        </div>
        <button type="submit" class="auth-btn">Login</button>
      </form>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="success" class="success">{{ success }}</div>
      <div class="switch-link">
        Don't have an account? <a @click.prevent="goRegister" href="/register">Register</a>
      </div>
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
          this.error = data.detail || 'Login failed. Please check your username and password.';
        } else {
          const data = await res.json();
          this.success = 'Login successful! Redirecting to dashboard...';
          localStorage.setItem('user', JSON.stringify({
            username: this.username,
            isLoggedIn: true
          }));
          setTimeout(() => {
            this.$router.push('/');
          }, 1500);
        }
      } catch (e) {
        this.error = 'Network error. Please try again later.';
      }
    },
    goRegister() {
      this.$router.push('/register');
    }
  }
};
</script>

<style scoped>
.dashboard-bg {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #0a2342 0%, #1e3c72 35%, #7b2ff2 70%, #2575fc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.auth-card {
  background: rgba(20, 40, 80, 0.85);
  border-radius: 18px;
  box-shadow: 0 4px 32px rgba(64,158,255,0.18), 0 0 24px 2px #1e3c72 inset;
  padding: 40px 36px 32px 36px;
  min-width: 340px;
  max-width: 380px;
  color: #fff;
  font-family: 'Orbitron', 'Segoe UI', 'Arial', sans-serif;
  text-align: center;
  position: relative;
}
.logo {
  font-size: 2em;
  font-weight: bold;
  color: #fff;
  letter-spacing: 2px;
  text-align: left;
  text-shadow: 0 4px 24px #1e90ff, 0 1px 0 #222;
  font-family: 'Orbitron', 'Segoe UI', 'Arial', sans-serif;
  margin-bottom: 8px;
}
.auth-title {
  font-size: 1.7em;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1.5px;
  text-shadow: 0 2px 16px #1e90ff, 0 1px 0 #222;
  margin-bottom: 28px;
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
  width: 80px;
  color: #b0b3b8;
  font-size: 1em;
  margin-right: 10px;
  letter-spacing: 1px;
  text-align: left;
}
input {
  flex: 1;
  background: #232526;
  border: 1.5px solid #232526;
  color: #fff;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 1em;
  outline: none;
  transition: border 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px #1e90ff22;
}
input:focus {
  border: 1.5px solid #3b82f6;
  background: #232526;
  box-shadow: 0 0 12px #3b82f6;
}
.auth-btn {
  width: 100%;
  padding: 12px 0;
  background: linear-gradient(90deg, #1e90ff 0%, #3b82f6 100%);
  color: #fff !important;
  border: none;
  border-radius: 8px;
  font-size: 1.08em;
  font-weight: 600;
  letter-spacing: 1px;
  box-shadow: 0 2px 12px #1e90ff, 0 0 8px 2px #fff8;
  text-shadow: 0 0 8px #fff, 0 0 16px #3b82f6;
  margin-top: 8px;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s, color 0.2s;
}
.auth-btn:hover {
  background: linear-gradient(90deg, #ff9800 0%, #ffb347 100%);
  color: #fff !important;
  box-shadow: 0 4px 24px #ff9800, 0 0 12px 2px #fff8;
  text-shadow: 0 0 12px #fff, 0 0 24px #ff9800;
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