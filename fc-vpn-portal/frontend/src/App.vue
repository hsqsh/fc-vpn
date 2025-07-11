<template>
  <div id="app">
    <b-navbar toggleable="lg" type="dark" variant="dark">
      <b-navbar-brand to="/">FC-VPN</b-navbar-brand>

      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

      <b-collapse id="nav-collapse" is-nav>        <b-navbar-nav class="ml-auto">
          <b-nav-item v-if="!isLoggedIn" to="/login">登录</b-nav-item>
          <b-nav-item v-if="!isLoggedIn" to="/register">注册</b-nav-item>
          <b-nav-item v-if="isLoggedIn" to="/dashboard">控制台</b-nav-item>
          <b-nav-item v-if="isLoggedIn" to="/monitor">流量监控</b-nav-item>
          <b-nav-item v-if="isLoggedIn" to="/profile">个人资料</b-nav-item>
          <b-nav-item v-if="isLoggedIn" @click="logout">登出</b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>

    <main class="mt-4">
      <router-view/>
    </main>

    <footer class="mt-5 py-3 text-center">
      <p>FC-VPN &copy; 2025 - 云原生弹性VPN解决方案</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    isLoggedIn() {
      return this.$store.getters.isLoggedIn;
    }
  },
  methods: {
    logout() {
      this.$store.dispatch('logout');
      this.$router.push('/login');
    }
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
main {
  flex: 1;
}
footer {
  background-color: #f8f9fa;
}
.container {
  max-width: 960px;
}
</style>
