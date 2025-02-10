import { createRouter, createWebHashHistory } from 'vue-router';  // 只导入 createWebHashHistory
import LoginPage from '../component/LoginPage.vue';
import WelcomePage from '../component/WelcomePage.vue';
import FileManagement from '../component/FileManagement.vue';
import ModelManagement from '../component/ModelManagement.vue';
import DiagnosisPage from '../component/DiagnosisPage.vue';
import ReportGenerative from '../component/ReportGenerative.vue';
import DashboardPage from '../component/DashboardPage.vue';
import RegisterPage from '../component/RegisterPage.vue';

const routes = [
  {
    path: '/login',
    name: 'LoginPage',
    component: LoginPage,
    beforeEnter: (to, from, next) => {
      console.log("LoginPage route matched!");
      next();
    }
  },
  {
    path: '/register',
    name: 'RegisterPage',
    component: RegisterPage
  },
  {
    path: '/welcome',
    name: 'WelcomePage',
    component: WelcomePage
  },
  {
    path: '/file-management',
    name: 'FileManagement',
    component: FileManagement
  },
  {
    path: '/model-management',
    name: 'ModelManagement',
    component: ModelManagement
  },
  {
    path: '/diagnosis',
    name: 'DiagnosisPage',
    component: DiagnosisPage
  },
  {
    path: '/report-generative',
    name: 'ReportGenerative',
    component: ReportGenerative
  },
  {
    path: '/dashboard',
    name: 'DashboardPage',
    component: DashboardPage,
    beforeEnter: (to, from, next) => {
      const userToken = localStorage.getItem('user_token');
      const username = localStorage.getItem('username');
      if (!userToken || !username) {  // 如果没有令牌或用户名，跳转到登录页面
        next('/login');
      } else {
        next();  // 已登录，允许访问
      }
    },
  },
];

// 创建 router 实例
const router = createRouter({
  history: createWebHashHistory(),  // 使用 createWebHashHistory 创建哈希历史记录模式
  routes
});

// 全局路由守卫，打印路由变化
router.beforeEach((to, from, next) => {
  console.log('Route is changing to:', to.name);  // 打印当前路由名称
  next();  // 必须调用 next()，否则路由不会继续
});

export default router;
