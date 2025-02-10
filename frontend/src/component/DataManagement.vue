<template>
  <div class="data-management">
    <h2>数据管理</h2>
    
    <!-- 文件上传记录 -->
    <h3>文件上传记录</h3>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>文件名</th>
          <th>上传时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="file in fileRecords" :key="file.id">
          <td>{{ file.id }}</td>
          <td>{{ file.name }}</td>
          <td>{{ file.uploadedAt }}</td>
          <td><button @click="deleteFile(file.id)">删除</button></td>
        </tr>
      </tbody>
    </table>

    <!-- 模型上传记录 -->
    <h3>模型上传记录</h3>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>模型名</th>
          <th>上传时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="model in modelRecords" :key="model.id">
          <td>{{ model.id }}</td>
          <td>{{ model.name }}</td>
          <td>{{ model.uploadedAt }}</td>
          <td><button @click="deleteModel(model.id)">删除</button></td>
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
      fileRecords: [],
      modelRecords: [],
    };
  },
  created() {
    this.fetchDataRecords();
    this.fetchModelRecords();
  },
  methods: {
    // 获取文件上传记录
    async fetchDataRecords() {
      try {
        const response = await axios.get('/data_management');
        this.fileRecords = response.data.dataRecords;
      } catch (error) {
        console.error("Error fetching data records:", error);
      }
    },

    // 获取模型上传记录
    async fetchModelRecords() {
      try {
        const response = await axios.get('/get_models');
        this.modelRecords = response.data.models;  // 根据实际返回数据结构调整
      } catch (error) {
        console.error("Error fetching model records:", error);
      }
    },

    // 删除文件记录
    async deleteFile(fileId) {
      const confirmDelete = confirm("确认删除该文件记录？");
      if (confirmDelete) {
        try {
          // 调用后端删除接口
          await axios.delete(`/delete_file/${fileId}`);
          // 删除成功后从列表中移除
          this.fileRecords = this.fileRecords.filter(file => file.id !== fileId);
        } catch (error) {
          console.error("Error deleting file:", error);
        }
      }
    },

    // 删除模型记录
    async deleteModel(modelId) {
      const confirmDelete = confirm("确认删除该模型记录？");
      if (confirmDelete) {
        try {
          // 调用后端删除接口
          await axios.delete(`/delete_model/${modelId}`);
          // 删除成功后从列表中移除
          this.modelRecords = this.modelRecords.filter(model => model.id !== modelId);
        } catch (error) {
          console.error("Error deleting model:", error);
        }
      }
    }
  }
};
</script>

<style scoped>
.data-management {
  padding: 1rem;
}

h3 {
  margin-top: 2rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
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
