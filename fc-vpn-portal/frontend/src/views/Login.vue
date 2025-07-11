<template>
  <div class="login">
    <b-container>
      <b-row align-h="center">
        <b-col cols="12" md="6">
          <b-card title="用户登录" class="mt-4">
            <b-alert v-if="error" show variant="danger">{{ error }}</b-alert>
            <b-form @submit.prevent="onSubmit">
              <b-form-group label="用户名" label-for="username">
                <b-form-input
                  id="username"
                  v-model="form.username"
                  type="text"
                  placeholder="请输入用户名"
                  required
                ></b-form-input>
              </b-form-group>

              <b-form-group label="密码" label-for="password">
                <b-form-input
                  id="password"
                  v-model="form.password"
                  type="password"
                  placeholder="请输入密码"
                  required
                ></b-form-input>
              </b-form-group>

              <b-button type="submit" variant="primary" :disabled="loading">
                {{ loading ? '登录中...' : '登录' }}
              </b-button>
            </b-form>
            <div class="mt-3">
              <p>还没有账号？<router-link to="/register">立即注册</router-link></p>
            </div>
          </b-card>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      error: null,
      loading: false
    }
  },
  methods: {
    onSubmit() {
      this.loading = true
      this.error = null
      
      this.$store.dispatch('login', this.form)
        .then(() => {
          this.$router.push('/dashboard')
        })        .catch(err => {
          this.error = (err.response && err.response.data && err.response.data.message) || '登录失败，请检查用户名和密码'
        })
        .finally(() => {
          this.loading = false
        })
    }
  }
}
</script>
