<template>
  <div class="register">
    <b-container>
      <b-row align-h="center">
        <b-col cols="12" md="6">
          <b-card title="用户注册" class="mt-4">
            <b-alert v-if="error" show variant="danger">{{ error }}</b-alert>
            <b-alert v-if="success" show variant="success">{{ success }}</b-alert>
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

              <b-form-group label="电子邮箱 (可选)" label-for="email">
                <b-form-input
                  id="email"
                  v-model="form.email"
                  type="email"
                  placeholder="请输入电子邮箱"
                ></b-form-input>
              </b-form-group>

              <b-button type="submit" variant="primary" :disabled="loading">
                {{ loading ? '注册中...' : '注册' }}
              </b-button>
            </b-form>
            <div class="mt-3">
              <p>已有账号？<router-link to="/login">立即登录</router-link></p>
            </div>
          </b-card>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    return {
      form: {
        username: '',
        password: '',
        email: ''
      },
      error: null,
      success: null,
      loading: false
    }
  },
  methods: {
    onSubmit() {
      this.loading = true
      this.error = null
      this.success = null
      
      this.$store.dispatch('register', this.form)
        .then(() => {
          this.success = '注册成功！请前往登录页面进行登录。'
          this.form = {
            username: '',
            password: '',
            email: ''
          }
          setTimeout(() => {
            this.$router.push('/login')
          }, 2000)
        })        .catch(err => {
          this.error = (err.response && err.response.data && err.response.data.message) || '注册失败，请稍后重试'
        })
        .finally(() => {
          this.loading = false
        })
    }
  }
}
</script>
