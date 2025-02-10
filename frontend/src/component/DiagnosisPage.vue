<template>
  <div>
    <h2>故障诊断</h2>

    <!-- 选择文件 -->
    <label for="file">选择文件：</label>
    <select v-model="selectedFile">
      <option v-for="file in files" :key="file.file_id" :value="file.file_id">
        {{ file.file_name }}
      </option>
    </select>

    <!-- 选择模型 -->
    <label for="model">选择模型：</label>
    <select v-model="selectedModel">
      <option v-for="model in models" :key="model.model_id" :value="model.model_id">
        {{ model.model_name }}
      </option>
    </select>

    <!-- 开始诊断按钮 -->
    <button @click="diagnose" :disabled="!selectedFile || !selectedModel">开始诊断</button>

    <!-- 显示加载提示 -->
    <div v-if="isLoading">诊断中，请稍候...</div>

    <!-- 显示诊断结果 -->
    <div v-if="diagnosisResult">
      <h3>诊断结果：</h3>
      <ul>
        <li>准确率（Accuracy）：{{ diagnosisResult.accuracy }}</li>
        <li>精确率（Precision）：{{ diagnosisResult.precision }}</li>
        <li>召回率（Recall）：{{ diagnosisResult.recall }}</li>
        <li>F1 分数：{{ diagnosisResult.f1 }}</li>
        <li>特异性（Specificity）：{{ diagnosisResult.specificity }}</li>
      </ul>

      <!-- 显示混淆矩阵图像 -->
      <div v-if="confusionMatrixImagePath">
        <h4>混淆矩阵 & t-SNE可视化</h4>
        <img :src="confusionMatrixImagePath" alt="Confusion Matrix" class="diagnosis-image" />
      </div>
    </div>

    <!-- 显示错误信息 -->
    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      files: [], // 文件列表
      models: [], // 模型列表
      selectedFile: null, // 选中的文件ID
      selectedModel: null, // 选中的模型ID
      diagnosisResult: null, // 诊断结果
      confusionMatrixImagePath: null, // 混淆矩阵图像路径
      isLoading: false, // 加载状态
      errorMessage: null, // 错误信息
    };
  },
  methods: {
    // 获取文件列表
    async fetchFiles() {
      try {
        const response = await axios.get("https://47.98.188.18:5000/get_files");
        this.files = response.data.files;
      } catch (error) {
        console.error("获取文件失败：", error);
        this.errorMessage = "获取文件列表失败，请稍后重试。";
      }
    },

    // 获取模型列表
    async fetchModels() {
      try {
        const response = await axios.get("https://47.98.188.18:5000/get_models");
        this.models = response.data.models;
      } catch (error) {
        console.error("获取模型失败：", error);
        this.errorMessage = "获取模型列表失败，请稍后重试。";
      }
    },

    // 执行诊断
    async diagnose() {
      if (!this.selectedFile || !this.selectedModel) {
        alert("请先选择文件和模型！");
        return;
      }

      this.isLoading = true; // 开始加载
      this.errorMessage = null;

      try {
        const response = await axios.post("https://47.98.188.18:5000/diagnose", {
          file_id: this.selectedFile,
          model_id: this.selectedModel,
        });

        // 确保后端返回数据正确
        const data = response.data;
        if (data.diagnosis_result) {
          this.diagnosisResult = data.diagnosis_result;

          // 构造完整的图像路径
          this.confusionMatrixImagePath = `https://47.98.188.18:5000${data.confusion_matrix_image_path}`;  // 使用完整路径
        } else {
          throw new Error("返回数据不完整");
        }
      } catch (error) {
        console.error("诊断失败：", error);
        this.errorMessage = error.response?.data?.message || "诊断失败，请稍后重试。";
      } finally {
        this.isLoading = false; // 加载结束
      }
    },
  },
  mounted() {
    this.fetchFiles();
    this.fetchModels();
  },
};
</script>

<style scoped>
button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px;
  cursor: pointer;
  font-size: 16px;
}

button:disabled {
  background-color: #d6d6d6;
  cursor: not-allowed;
}

select {
  margin: 10px;
  padding: 8px;
  font-size: 14px;
}

h2 {
  margin-bottom: 20px;
}

h3 {
  margin-top: 20px;
}

.diagnosis-image {
  max-width: 70%;
  margin: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.error {
  color: red;
  margin-top: 20px;
}
</style>
