<template>
  <div class="model-management-container">
    <h2>模型管理</h2>

    <!-- 上传文件按钮和输入框 -->
    <div class="upload-container">
      <input type="file" ref="fileInput" @change="handleModelUpload" />
      <!-- 如果没有正在上传，则显示上传文件按钮 -->
      <button v-if="!uploading" @click="triggerFileInput" class="upload-button">上传模型</button>
      <!-- 如果正在上传，则显示上传中...按钮 -->
      <button v-if="uploading" disabled>上传中...</button>
    </div>

    <!-- 模型列表 -->
    <div v-if="models.length">
      <table>
        <thead>
          <tr>
            <th>模型名称</th>
            <th>文件大小</th>
            <th>上传时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="model in models" :key="model.model_id">
            <td>{{ model.model_name }}</td>
            <td>{{ formatFileSize(model.model_size) }}</td>
            <td>{{ formatDate(model.upload_time) }}</td>
            <td>
              <button @click="deleteModel(model.model_id)" class="delete-button">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="pagination">
        <button :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">上一页</button>
        <span>第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
        <button :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">下一页</button>
      </div>
    </div>

    <!-- 没有模型时的提示信息 -->
    <div v-else class="no-models">
      <p>没有上传的模型。</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      models: [], // 存储模型列表
      uploading: false, // 上传状态标识
      currentPage: 1, // 当前页码
      totalPages: 1, // 总页数
      pageSize: 5, // 每页展示的模型数量
      fileName: "", // 存储上传文件的文件名
    };
  },
  methods: {
    // 获取模型列表
    async fetchModels() {
      try {
        const response = await axios.get("https://47.98.188.18:5000/get_models", {
          params: {
            page: this.currentPage,
            page_size: this.pageSize,
          }
        });
        if (response.status === 200) {
          this.models = response.data.models; // 更新模型列表
          this.totalPages = Math.ceil(response.data.total / this.pageSize); // 更新总页数
        }
      } catch (error) {
        console.error("获取模型列表失败", error);
      }
    },

    // 检查文件是否已存在
    async checkFileExists(fileName) {
      try {
        const response = await axios.get("https://47.98.188.18:5000/check_model_exists", {
          params: { model_name: fileName }
        });
        return response.data.exists; // 返回是否存在该文件
      } catch (error) {
        console.error("检查文件是否存在失败", error);
        return false;
      }
    },

    // 处理模型上传
    async handleModelUpload(event) {
      const file = event.target.files[0];

      if (!file) {
        alert("请选择一个模型文件上传！");
        return;
      }

      const fileName = file.name;

      // 检查文件是否已存在
      const fileExists = await this.checkFileExists(fileName);
      if (fileExists) {
        alert("已存在相同文件，请勿重复上传！");
        return;
      }

      const formData = new FormData();
      formData.append("model", file);

      this.uploading = true; // 设置上传状态

      try {
        const response = await axios.post("https://47.98.188.18:5000/upload_model", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        if (response.status === 200) {
          this.fetchModels(); // 上传成功后重新获取模型列表
        }
      } catch (error) {
        console.error("上传模型失败", error);
        // 错误处理，判断是否有返回的 error 信息
        if (error.response && error.response.data && error.response.data.error) {
          const errorMessage = error.response.data.error;

          // 根据后端返回的错误信息做出不同的提示
          if (errorMessage === "Model already exists") {
            alert("该模型文件已存在，请勿重复上传！");
          } else {
            alert("上传模型失败，请重试。");
          }
        } else {
          alert("上传模型失败，请重试。");
        }
      } finally {
        this.uploading = false; // 上传完成，恢复状态
      }
    },

    // 触发文件选择框
    triggerFileInput() {
      this.$refs.fileInput.click();
    },

    // 删除模型
    async deleteModel(modelId) {
      try {
        console.log('正在删除模型：' + modelId); // 输出模型ID进行调试
        const response = await axios.delete(`https://47.98.188.18:5000/delete_model/${modelId}`);
        if (response.status === 200) {
          this.fetchModels(); // 删除成功后重新获取模型列表
        }
      } catch (error) {
        console.error("删除模型失败", error);
        alert("删除模型失败，请重试。");
      }
    } ,

    // 格式化文件大小
    formatFileSize(size) {
      if (size < 1024) return `${size} B`;
      else if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`;
      else if (size < 1024 * 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(2)} MB`;
      else return `${(size / (1024 * 1024 * 1024)).toFixed(2)} GB`;
    },

    // 格式化日期
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString(); // 例如：2025/01/01
    },

    // 跳转到指定页
    goToPage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.currentPage = page;
      this.fetchModels(); // 切换页码时重新获取模型列表
    }
  },
  mounted() {
    this.fetchModels(); // 页面加载时获取模型列表
  }
};
</script>

<style scoped>
/* 容器样式 */
.model-management-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

/* 上传模型区域样式 */
.upload-container {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end; /* 上传按钮在右侧 */
  align-items: center;
}

.upload-container input[type="file"] {
  padding: 8px;
  margin-right: 10px;
  display: none; /* 隐藏文件输入框 */
}

.upload-container button {
  background-color: #4CAF50;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.upload-container button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 表格样式 */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  padding: 12px;
  text-align: left;
  border: 1px solid #ddd;
}

th {
  background-color: #f2f2f2;
  font-weight: bold;
}

tr:hover {
  background-color: #f9f9f9;
}

/* 删除按钮样式 */
.delete-button {
  background-color: #f44336;
  color: white;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.delete-button:hover {
  background-color: darkred;
}

/* 分页样式 */
.pagination {
  margin-top: 20px;
  text-align: center;
}

.pagination button {
  background-color: #007bff;
  color: white;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin: 0 5px;
}

.pagination button:hover {
  background-color: #0056b3;
}

.pagination button:disabled {
  background-color: #d6d6d6;
  cursor: not-allowed;
}

/* 没有模型时的样式 */
.no-models {
  text-align: center;
  font-size: 18px;
  color: #888;
}
</style>
