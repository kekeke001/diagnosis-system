const fs = require('fs');

module.exports = {
  devServer: {
    https: {
      key: fs.readFileSync('/root/My_Project/backend/server_decrypted.key'),  // 解密后的私钥路径
      cert: fs.readFileSync('/root/My_Project/backend/server.crt')  // 证书路径
    },
    host: '0.0.0.0',
    port: 8080,
    proxy: {
      '/api': {
        target: 'https://47.98.188.18:5000',
        changeOrigin: true,
        secure: false,
        pathRewrite: {
          '^/api': ''
        }
      }
    }
  }
};
