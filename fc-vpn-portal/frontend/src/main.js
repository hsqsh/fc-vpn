import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import VueApexCharts from 'vue-apexcharts'

// 导入 Bootstrap 和 BootstrapVue CSS 文件
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

// 配置 Vue 使用 BootstrapVue 和 ApexCharts
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)
Vue.use(VueApexCharts)

Vue.component('apexchart', VueApexCharts)

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
