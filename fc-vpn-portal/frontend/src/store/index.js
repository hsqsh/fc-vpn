import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

// 设置axios默认基础URL
axios.defaults.baseURL = 'http://localhost:5000'

// 如果localStorage中有token，则设置默认的Authorization header
if (localStorage.getItem('token')) {
  axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('token')
}

export default new Vuex.Store({
  state: {
    status: '',
    token: localStorage.getItem('token') || '',
    user: {}
  },
  mutations: {
    auth_request(state) {
      state.status = 'loading'
    },
    auth_success(state, token) {
      state.status = 'success'
      state.token = token
    },
    auth_error(state) {
      state.status = 'error'
    },
    logout(state) {
      state.status = ''
      state.token = ''
      state.user = {}
    },
    set_user(state, user) {
      state.user = user
    }
  },
  actions: {    login({ commit }, user) {
      return new Promise((resolve, reject) => {
        commit('auth_request')
        axios.post('/api/auth/login', user)
          .then(resp => {
            const token = resp.data.access_token
            localStorage.setItem('token', token)
            axios.defaults.headers.common['Authorization'] = 'Bearer ' + token
            commit('auth_success', token)
            resolve(resp)
          })
          .catch(err => {
            commit('auth_error')
            localStorage.removeItem('token')
            reject(err)
          })
      })
    },
    register({ commit }, user) {
      return new Promise((resolve, reject) => {
        commit('auth_request')
        axios.post('/api/auth/register', user)
          .then(resp => {
            resolve(resp)
          })
          .catch(err => {
            commit('auth_error')
            reject(err)
          })
      })
    },
    logout({ commit }) {
      return new Promise((resolve) => {
        commit('logout')
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
        resolve()
      })
    },
    fetchUserProfile({ commit }) {
      return new Promise((resolve, reject) => {
        axios.get('/api/user/profile')
          .then(resp => {
            commit('set_user', resp.data)
            resolve(resp)
          })
          .catch(err => {
            reject(err)
          })
      })    },    requestService(context, targetUrl) {
      return new Promise((resolve, reject) => {
        axios.post('/api/service/request', { target_url: targetUrl })
          .then(resp => {
            resolve(resp)
          })
          .catch(err => {
            reject(err)
          })
      })
    },    disconnectService(context, serviceId) {
      return new Promise((resolve, reject) => {
        axios.post('/api/service/disconnect', { service_id: serviceId })
          .then(resp => {
            resolve(resp)
          })
          .catch(err => {
            reject(err)
          })
      })
    },
    fetchMonitoringData(context) {
      return new Promise((resolve, reject) => {
        axios.get('/api/service/monitor')
          .then(resp => {
            resolve(resp)
          })
          .catch(err => {
            reject(err)
          })
      })
    }
  },
  getters: {
    isLoggedIn: state => !!state.token,
    authStatus: state => state.status,
    user: state => state.user
  }
})
