<template>
  <div class="home">
    <b-container>
      <b-row align-h="center" class="mt-5">
        <b-col cols="12" md="8">
          <b-card class="text-center">
            <h2>欢迎使用 FC-VPN</h2>
            <h4 class="text-muted">云原生弹性VPN解决方案</h4>
            <p class="mt-4">
              FC-VPN是一款基于云原生技术构建的现代化VPN服务，提供弹性扩展、按需付费、智能管理的VPN解决方案。
            </p>
            <div class="mt-4">
              <b-button to="/register" variant="primary" class="mr-3">立即注册</b-button>
              <b-button to="/login" variant="outline-primary">登录</b-button>
            </div>
          </b-card>
        </b-col>
      </b-row>

      <b-row class="mt-5">
        <b-col cols="12" md="4" class="mb-4">
          <b-card title="弹性扩展" class="h-100">
            <b-card-text>
              根据实际需求自动扩展资源，无论是10个用户还是10000个用户，都能够保持稳定的性能。
            </b-card-text>
          </b-card>
        </b-col>
        <b-col cols="12" md="4" class="mb-4">
          <b-card title="按需付费" class="h-100">
            <b-card-text>
              只为您实际使用的服务付费，不再需要预先购买固定容量的VPN硬件或服务。
            </b-card-text>
          </b-card>
        </b-col>
        <b-col cols="12" md="4" class="mb-4">
          <b-card title="智能管理" class="h-100">
            <b-card-text>
              基于Kubernetes的自动化管理，确保服务高可用性和自动恢复能力。
            </b-card-text>
          </b-card>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>
