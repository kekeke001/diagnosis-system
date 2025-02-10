<template>
  <div id="dashboard">
    <!-- 顶部导航栏 -->
    <header class="header">
      <h1>故障诊断系统管理平台</h1>
      <div class="user-info">
        <span>欢迎 {{ username || '未知用户' }}</span>
        <button class="logout-btn" @click="logout">登出</button>
      </div>
    </header>

    <!-- 主体部分 -->
    <div class="main-container">
      <!-- 侧边栏导航 -->
      <aside class="sidebar">
        <button
          v-for="tab in tabs"
          :key="tab.name"
          :class="{ active: currentTab === tab.name }"
          @click="currentTab = tab.name"
        >
          {{ tab.label }}
        </button>
      </aside>

      <!-- 内容区域 -->
      <div class="content">
        <component :is="currentTabComponent" />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import WelcomePage from './WelcomePage.vue';
import FileManagement from './FileManagement.vue';
import ModelManagement from './ModelManagement.vue';
import DiagnosisPage from './DiagnosisPage.vue';
import ReportGeneration from './ReportGenerative.vue';
import UserManagement from './UserManagement.vue';
// import DataManagement from './DataManagement.vue';

export default {
  data() {
    return {
      currentTab: 'WelcomePage',
      username: '', // 用于保存当前登录的用户名
      tabs: [
        { name: 'WelcomePage', label: '欢迎使用', component: WelcomePage },
        { name: 'FileManagement', label: '文件管理', component: FileManagement },
        { name: 'ModelManagement', label: '模型管理', component: ModelManagement },
        { name: 'DiagnosisPage', label: '故障诊断', component: DiagnosisPage },
        { name: 'ReportGeneration', label: '报表生成', component: ReportGeneration },
        // { name: 'DataManagement', label: '数据管理', component: DataManagement },
        { name: 'UserManagement', label: '用户管理', component: UserManagement },
      ],
    };
  },
  mounted() {
    this.checkLoginStatus();  // 页面加载时检查是否已登录
    this.fetchCurrentUser();   // 获取当前用户信息
  },
  methods: {
    // 检查是否已登录
    checkLoginStatus() {
      const token = localStorage.getItem('user_token');
      if (!token) {
        this.$router.push('/login');  // 如果没有 token，跳转到登录页面
      }
    },

    // 获取当前用户信息
    async fetchCurrentUser() {
      try {
        const token = localStorage.getItem('user_token');
        const response = await axios.get('https://47.98.188.18:5000/api/current_user', {
          headers: {
            Authorization: `Bearer ${token}`, // 使用 token 验证
          },
        });

        if (response.data && response.data.username) {
          this.username = response.data.username;
        } else {
          this.username = '未知用户';
        }
      } catch (error) {
        console.error('获取当前用户信息失败:', error);
        this.username = '未知用户'; // 处理错误情况时提供默认用户名
        this.$router.push('/login');
      }
    },

    // 登出方法
    logout() {
      // 清除本地存储中的用户信息
      localStorage.removeItem('user_token');
      localStorage.removeItem('username');

      // 重定向到登录页面
      this.$router.push('/login');
    }
  },
  computed: {
    // 动态加载当前选中的组件
    currentTabComponent() {
      const tab = this.tabs.find((t) => t.name === this.currentTab);
      return tab ? tab.component : null;
    },
  },
};
</script>

<style scoped>
#dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
/* 头部标题和用户信息 */
.header {
  background: #3f51b5;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: flex-start;  /* 设置为 flex-start，标题靠左 */
  align-items: center;
  width: 100%;
}

.header h1 {
  margin: 0;
  font-size: 38px;
  text-align: left;  /* 确保标题文字靠左 */
  flex-grow: 1;  /* 让 h1 伸展以占据空白空间 */
}

.user-info {
  font-size: 1rem;
  color: white;
  display: flex;
  align-items: center;
  justify-content: flex-end;  /* 用户信息靠右对齐 */
}

.logout-btn {
  margin-left: 20px;
  padding: 5px 10px;
  cursor: pointer;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 5px;
}

.logout-btn:hover {
  background-color: #d32f2f;
}

.main-container {
  display: flex;
  flex: 1;
}

.sidebar {
  width: 200px;
  background: #f4f4f4;
  border-right: 1px solid #ddd;
  display: flex;
  flex-direction: column;
  padding: 1rem 0;
}

.sidebar button {
  background: none;
  border: none;
  text-align: left;
  padding: 1rem;
  width: 100%;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s, color 0.3s;
}

.sidebar button:hover {
  background: #ddd;
}

.sidebar button.active {
  background: #3f51b5;
  color: white;
  font-weight: bold;
}

.content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}
</style>
