<template>
  <div class="background-container">
    <div class="register-container">
      <h2>用户注册</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            type="text"
            v-model="username"
            id="username"
            placeholder="请输入用户名"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            v-model="password"
            id="password"
            placeholder="请输入密码"
            required
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            type="password"
            v-model="confirmPassword"
            id="confirmPassword"
            placeholder="请确认密码"
            required
          />
        </div>

        <div class="form-group">
          <label for="email">电子邮件</label>
          <input
            type="email"
            v-model="email"
            id="email"
            placeholder="请输入电子邮件"
            required
          />
        </div>

        <div class="form-actions">
          <button type="submit">注册</button>
        </div>
      </form>

      <p class="redirect">
        已有账号？ <router-link to="/login">立即登录</router-link>
      </p>
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
      confirmPassword: "",
      email: "",
    };
  },
  methods: {
    // 提交注册表单
    async handleSubmit() {
      if (this.password !== this.confirmPassword) {
        alert("密码和确认密码不匹配！");
        return;
      }

      const data = {
        username: this.username,
        password: this.password,
        email: this.email,
      };

      try {
        const response = await axios.post(
          "https://47.98.188.18:5000/register",
          data
        );
        if (response.status === 200) {
          alert("注册成功！");
          this.$router.push("/login"); // 注册成功后跳转到登录页面
        }
      } catch (error) {
        alert("注册失败：" + (error.response && error.response.data.error));
      }
    },
  },
};
</script>

<style scoped>
.background-container {
  height: 100vh;
  background-image: url("/root/My_Project/frontend/public/image/background.png");
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-container {
  width: 400px;
  padding: 40px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.9); /* 半透明白色背景 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 10px;
  margin-top: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.form-actions {
  text-align: center;
}

.form-actions button {
  padding: 10px 20px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.form-actions button:hover {
  background-color: #45a049;
}

.redirect {
  text-align: center;
  margin-top: 20px;
}
</style>
