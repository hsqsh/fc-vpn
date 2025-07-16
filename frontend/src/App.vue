<template>
  <router-view />
</template>

<script>
export default {
  name: 'App',
};
</script>

<style>
/* 全局样式可在此添加 */
/* 在 App.vue 的 <style> 标签里（不要加 scoped） */
.el-button,
.el-button--primary,
.el-button--primary span,
.el-button span {
  color: #fff !important;
  text-shadow: 0 0 8px #fff, 0 0 16px #3b82f6;
  font-weight: 600;
}
.el-button--primary {
  background: linear-gradient(90deg, #1e90ff 0%, #3b82f6 100%);
  border: none;
  box-shadow: 0 2px 12px #1e90ff, 0 0 8px 2px #fff8;
}
.el-button--primary:hover {
  background: linear-gradient(90deg, #ff9800 0%, #ffb347 100%);
  color: #fff !important;
  box-shadow: 0 4px 24px #ff9800, 0 0 12px 2px #fff8;
  text-shadow: 0 0 12px #fff, 0 0 24px #ff9800;
}
</style> 