<template>
  <div class="welcome-container">
    <h1>欢迎使用故障诊断系统</h1>
    <p>本系统提供以下功能：</p>
    <ul>
      <li>文件管理：上传文件的管理和记录（支持增加和删除）</li>
      <li>模型管理：已经训练好的模型管理（支持增加和删除）</li>
      <li>故障诊断：选择文件和已经训练好的模型进行诊断，生成诊断结果并保存</li>
      <li>报表生成：生成诊断结果报表</li>
      <li>用户管理：查看和管理用户记录</li>
      <li>数据管理：管理文件和模型上传记录</li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "WelcomePage",
};
</script>

<style scoped>
.welcome-container {
  text-align: center; /* 整个容器内容居中 */
  padding: 20px;
}

h1 {
  font-size: 3.5rem; /* 调整标题字体大小 */
  margin-top: 10px;  /* 设置标题与顶部的间距 */
  margin-bottom: 10px; /* 标题与下面内容的间距 */
}

p {
  font-size: 1.75rem; /* 调整段落字体大小 */
  margin-bottom: 10px; /* 段落与列表项的间距 */
}

ul {
  list-style-type: none; /* 去除默认列表符号 */
  padding-left: 0;
  display: inline-block; /* 使整个列表居中显示 */
  text-align: left; /* 保持列表项的左对齐 */
}

li {
  font-size: 1.25rem;
  margin: 0.5rem 0; /* 调整每个项目的间距 */
  padding-left: 100px; /* 增加左侧内边距，调整文字与左边的距离 */
}
</style>
