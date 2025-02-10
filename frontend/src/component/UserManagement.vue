<template>
  <div class="user-management">
    <h2>用户管理</h2>
    <table>
      <thead>
        <tr>
          <!--<th>ID</th>-->
          <th>用户名</th>
          <th>邮箱</th>
          <th>角色</th>
          <th>最后登录时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <!--<td>{{ user.id }}</td>-->
          <td>{{ user.username }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.role }}</td>
          <td>{{ formatDate(user.last_login) }}</td>
          <td>
            <button @click="editUser(user)">编辑</button>
            <button @click="deleteUser(user.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      users: [], // 用于存储从后端获取的用户数据
    };
  },
  mounted() {
    this.fetchUsers();
  },
  methods: {
    // 从后端获取用户数据
    async fetchUsers() {
      try {
        const response = await axios.get('https://47.98.188.18:5000/api/users'); // 后端 API 路径
        this.users = response.data; // 将获取到的用户数据赋值给 users 数组
      } catch (error) {
        console.error('获取用户数据失败:', error);
      }
    },

    // 格式化日期，转换为 UTC+8 时区
    formatDate(dateString) {
      const date = new Date(dateString); // 将字符串转换为 Date 对象
      return date.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' }); // 转换为上海时区（UTC+8）
    },

    // 编辑用户
    editUser(user) {
      alert(`编辑用户：${user.username}`);
    },

    // 删除用户
    async deleteUser(userId) {
      if (confirm('确认删除该用户？')) {
        try {
          await axios.delete(`https://47.98.188.18:5000/api/users/${userId}`); // 删除用户的后端 API 路径
          this.users = this.users.filter((user) => user.id !== userId); // 删除本地列表中的用户
          alert('用户已删除');
        } catch (error) {
          console.error('删除用户失败:', error);
          alert('删除用户失败，请稍后再试');
        }
      }
    },
  },
};
</script>

<style scoped>
.user-management {
  padding: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead th {
  background: #3f51b5;
  color: white;
  padding: 0.5rem;
  text-align: left;
}

tbody td {
  border: 1px solid #ddd;
  padding: 0.5rem;
}

button {
  margin: 0 0.5rem;
  padding: 0.3rem 0.6rem;
  border: none;
  background: #3f51b5;
  color: white;
  cursor: pointer;
}

button:hover {
  background: #303f9f;
}
</style>
