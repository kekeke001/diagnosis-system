import axios from 'axios';
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';  // 导入 router 配置文件
// 引入 socket.io-client
import io from 'socket.io-client';

// 设置 axios 的 baseURL 使用 HTTPS
axios.defaults.baseURL = 'https://47.98.188.18:5000';  // 确保使用 HTTPS 协议
axios.defaults.headers.common['Content-Type'] = 'application/json';  // 设置请求头为 JSON
axios.defaults.timeout = 300000;  // 设置超时为 10秒


createApp(App).use(router).mount('#app');  // 挂载到 #app


// 创建 WebSocket 连接（使用 wss 协议）
const socket = io('wss://47.98.188.18:5000', {
  transports: ['websocket'],
  secure: true,                // 开启安全连接
  rejectUnauthorized: false    // 跳过自签名证书验证（如果使用的是自签名证书）
});

// 连接成功时的回调
socket.on('connect', () => {
  console.log('Connected to WebSocket server');
});

// 监听服务器响应的消息
socket.on('response', (data) => {
  console.log('Received from server:', data);
});


socket.on('connect_error', (error) => {
  console.error('WebSocket connection failed:', error);
});

socket.on('response', (data) => {
  console.log('Received from server:', data);
});

// 向服务器发送消息
function sendMessage() {
  socket.emit('send_message', { message: 'Hello from client!' });
}

// 可以在 Vue 组件中调用该函数
export default {
  name: 'App',
  mounted() {
    sendMessage(); // 组件加载时发送消息
  }
};
