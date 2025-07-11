import Vue from 'vue';
import Router from 'vue-router';
import Dashboard from './pages/Dashboard.vue';
import Login from './pages/Login.vue';
import Monitor from './pages/Monitor.vue';
import Profile from './pages/Profile.vue';

Vue.use(Router);

export default new Router({
  routes: [
    { path: '/', component: Dashboard },
    { path: '/login', component: Login },
    { path: '/monitor', component: Monitor },
    { path: '/profile', component: Profile },
  ],
}); 