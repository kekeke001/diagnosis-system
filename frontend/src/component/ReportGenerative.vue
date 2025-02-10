<template>
  <div>
    <h2>诊断报表</h2>

    <!-- 诊断记录表单 -->
    <table border="1" cellpadding="10" cellspacing="0" style="width: 100%; border-collapse: collapse;">
      <thead>
        <tr>
          <th>报告名</th> <!-- 新增报告名列 -->
          <th>文件名</th>
          <th>模型名</th>
          <th>诊断时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="record in diagnosisRecords" :key="record.record_id">
          <td>{{ record.report_name }}</td> <!-- 显示报告名 -->
          <td>{{ record.file_name }}</td>
          <td>{{ record.model_name }}</td>
          <td>{{ formatDate(record.created_at) }}</td>
          <td>
            <!-- 删除按钮 -->
            <button @click="deleteRecord(record.record_id)" class="btn-delete">删除</button>
            <!-- 下载按钮 -->
            <button @click="downloadReport(record.report_path)" class="btn-download">下载报告</button>
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- 错误信息 -->
    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      diagnosisRecords: [],  // 存储诊断记录
      errorMessage: null,    // 错误信息
    };
  },
  methods: {
    // 获取诊断记录
    async fetchDiagnosisRecords() {
      try {
        const response = await axios.get('https://47.98.188.18:5000/get_diagnosis_records');
        this.diagnosisRecords = response.data.records;
      } catch (error) {
        console.error("获取诊断记录失败：", error);
        this.errorMessage = "获取诊断记录失败，请稍后重试。";
      }
    },

    // 格式化日期
    formatDate(dateStr) {
      const date = new Date(dateStr);
    
      // 获取年、月、日、时、分、秒
      const year = date.getFullYear();
      const month = (date.getMonth() + 1).toString().padStart(2, '0');  // 月份从 0 开始，因此需要加 1
      const day = date.getDate().toString().padStart(2, '0');
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      const seconds = date.getSeconds().toString().padStart(2, '0');
    
      // 返回完整的日期时间格式
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    },

    // 删除诊断记录
    async deleteRecord(recordId) {
      if (confirm('您确定要删除此诊断记录及其报告吗？')) {
        try {
          const response = await axios.delete(`https://47.98.188.18:5000/delete_diagnosis_record/${recordId}`);
          if (response.status === 200) {
            alert('删除成功');
            this.fetchDiagnosisRecords();  // 刷新诊断记录列表
          } else {
            this.errorMessage = "删除失败，请稍后重试。";
          }
        } catch (error) {
          console.error("删除诊断记录失败：", error);
          this.errorMessage = "删除诊断记录失败，请稍后重试。";
        }
      }
    },

    // 下载报告
    downloadReport(reportPath) {
      // 处理路径，确保正确拼接
      if (reportPath.startsWith('/root/My_Project/backend')) {
        reportPath = reportPath.replace('/root/My_Project/backend', '');
      }

      // 拼接成完整的 URL
      const reportUrl = `https://47.98.188.18:5000${reportPath}`;
      
      // 跳转到报告页面
      window.location.href = reportUrl;
    },
  },
  mounted() {
    this.fetchDiagnosisRecords();  // 页面加载时获取诊断记录
  },
};
</script>

<style scoped>
/* 按钮样式 */
.btn-delete {
  background-color: #ff4444;
  color: white;
  padding: 5px 10px;
  margin: 5px;
  cursor: pointer;
  border: none;
  border-radius: 5px;
}

.btn-download {
  background-color: #4CAF50;
  color: white;
  padding: 5px 10px;
  margin: 5px;
  cursor: pointer;
  border: none;
  border-radius: 5px;
}

.error {
  color: red;
  margin-top: 20px;
}
</style>
