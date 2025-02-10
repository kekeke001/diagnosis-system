<template>
  <div class="login-page">
    <div class="background-overlay">
      <h1 class="system-title">故障诊断系统</h1>
    </div>

    <div class="login-form-wrapper">
      <h2>欢迎登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">用户名</label>
          <input
            type="text"
            id="username"
            v-model="username"
            required
            placeholder="请输入用户名"
          />
        </div>
        <div class="input-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            placeholder="请输入密码"
          />
        </div>
        <button type="submit" class="login-button">登录</button>
        <p class="register-link">
          还没有账户？
          <router-link to="/register">注册</router-link>
        </p>
      </form>
      <div v-if="errorMessage" class="error">
        <p>{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      username: "",
      password: "",
      errorMessage: "",
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axios.post("https://47.98.188.18:5000/login", {
          username: this.username,
          password: this.password,
        });
        if (response.status === 200) {
          // 保存令牌和用户名到 localStorage
          localStorage.setItem('user_token', response.data.token); // 保存 token
          localStorage.setItem('username', this.username); // 保存用户名
          // 跳转到 dashboard 页面
          this.$router.push("/dashboard");
        }
      } catch (error) {
        this.errorMessage =
          (error.response && error.response.data.error) ||
          "登录失败，请稍后再试";
      }
    },
  },
};
</script>

<style scoped>
.login-page {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-image: url("/root/My_Project/frontend/public/image/background.png");
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
}

.system-title {
  position: absolute;
  top: 3%;
  left: 30%;
  font-size: 6em;
  font-weight: bold;
  color: white;
  text-shadow: 3px 3px 10px rgba(0, 0, 0, 0.7);
  text-align: center;
}

.login-form-wrapper {
  background-color: rgba(255, 255, 255, 0.85);
  top: 6%;
  padding: 20px 30px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 100%;
  text-align: center;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.input-group {
  margin-bottom: 15px;
  text-align: left;
}

.input-group label {
  font-size: 0.9em;
  color: #555;
  margin-bottom: 5px;
  display: block;
}

.input-group input {
  width: 100%;
  padding: 10px;
  font-size: 1em;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.login-button {
  width: 100%;
  padding: 12px;
  background-color: #3f51b5;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1.2em;
  cursor: pointer;
}

.login-button:hover {
  background-color: #303f9f;
}

.register-link {
  margin-top: 10px;
  font-size: 0.9em;
}

.error {
  margin-top: 15px;
  color: red;
}
</style>
