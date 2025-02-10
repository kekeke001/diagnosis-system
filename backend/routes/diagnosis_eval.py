# diagnosis_eval.py
import sys
import os
import zipfile
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.manifold import TSNE
import numpy as np
from tqdm import tqdm
import math
import json

# 自定义数据集类
class CustomDataset(Dataset):
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]


# 从 zip 文件中恢复 test_dataset
def load_test_dataset_from_zip(file_path):
    """
    从 zip 文件解压并读取 CSV 文件，然后恢复数据集
    :param zip_file_name: zip 文件路径
    :return: CustomDataset 实例
    """
    # 检查temp_data目录是否存在，不存在就创建
    temp_dir = './temp_data'
    os.makedirs(temp_dir, exist_ok=True)  # 确保临时目录存在

    # 解压文件
    with zipfile.ZipFile(file_path, 'r') as zipf:
        zipf.extractall(temp_dir)

    # 打印解压后的文件列表，帮助调试
    extracted_files = os.listdir(temp_dir)
    print(f"解压后的文件列表：{extracted_files}")

    # 假设 CSV 文件名为 test_data1.csv，如果文件名不同，请修改
    csv_file = os.path.join(temp_dir, 'test_dataset.csv')
    
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"未找到 CSV 文件：{csv_file}")
        
    df = pd.read_csv(csv_file)

    # 确保数据没有非数值列，强制转换为数值类型
    df = df.apply(pd.to_numeric, errors='coerce')  # 将无法转换为数字的值设置为 NaN

    # 处理缺失值：可以选择填充或删除
    df = df.fillna(0)  # 选择填充 NaN 值为 0，也可以选择删除 df.dropna()

    # 提取数据和标签
    data = df.iloc[:, :-1].values  # 除了最后一列，作为特征数据
    labels = df.iloc[:, -1].values  # 最后一列作为标签

    # 清理临时解压文件
    os.remove(csv_file)

    # 将数据转换为 torch tensor
    data = torch.tensor(data, dtype=torch.float32)
    labels = torch.tensor(labels, dtype=torch.long)

    # 将数据重塑为 (963, 1024, 13) 的形状
    data = data.reshape(-1, 1024, 13)  # 恢复数据的形状
    print("恢复后的数据形状:", data.shape)
    print("恢复后的标签形状:", labels.shape)

    return CustomDataset(data, labels)


# 生成 test_loader 数据加载器
def get_test_loader(file_path, batch_size):
    """
    生成测试数据加载器
    :param zip_file_name: zip 文件路径
    :param batch_size: 批量大小
    :return: DataLoader 对象
    """
    test_dataset = load_test_dataset_from_zip(file_path)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    return test_loader


class LinearAttention(nn.Module):
    def __init__(self, d_model):
        super(LinearAttention, self).__init__()
        self.query_proj = nn.Linear(d_model, d_model)
        self.key_proj = nn.Linear(d_model, d_model)
        self.value_proj = nn.Linear(d_model, d_model)
        self.output_proj = nn.Linear(d_model, d_model)
    
    def forward(self, x):
        Q = self.query_proj(x)  # (sequence_length, batch_size, d_model)
        K = self.key_proj(x)    # (sequence_length, batch_size, d_model)
        V = self.value_proj(x)  # (sequence_length, batch_size, d_model)
        
        Q = F.elu(Q) + 1
        K = F.elu(K) + 1
        
        K = K.permute(1, 2, 0)  # (batch_size, d_model, sequence_length)
        V = V.permute(1, 0, 2)  # (batch_size, sequence_length, d_model)
        
        KV = torch.bmm(K, V)    # (batch_size, d_model, d_model)
        Q = Q.permute(1, 0, 2)  # (batch_size, sequence_length, d_model)
        
        output = torch.bmm(Q, KV)  # (batch_size, sequence_length, d_model)
        output = output.permute(1, 0, 2)  # (sequence_length, batch_size, d_model)
        
        output = self.output_proj(output)
        return output

class CustomTransformerEncoderLayer(nn.Module):
    def __init__(self, d_model, dim_feedforward, dropout):
        super(CustomTransformerEncoderLayer, self).__init__()
        self.linear_attention = LinearAttention(d_model)
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(dim_feedforward, d_model)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, src):
        src2 = self.linear_attention(src)
        src = src + self.dropout1(src2)
        src = self.norm1(src)

        src2 = self.linear2(self.dropout(F.relu(self.linear1(src))))
        src = src + self.dropout2(src2)
        src = self.norm2(src)
        return src

# 计算位置编码
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)
    
class TransformerEncoderModule(nn.Module):
    def __init__(self, d_model, nhead, num_encoder_layers, dim_feedforward, dropout):
        super(TransformerEncoderModule, self).__init__()
        self.pos_encoder = PositionalEncoding(d_model)
        self.encoder_layers = nn.ModuleList(
            [CustomTransformerEncoderLayer(d_model, dim_feedforward, dropout) for _ in range(num_encoder_layers)]
        )

    def forward(self, x):
        x = self.pos_encoder(x)
        for layer in self.encoder_layers:
            x = layer(x)
        return x

class ConvLF_Net(nn.Module):
    def __init__(self, channel_in=13, num_filters=16, d_model=256, nhead=8, num_encoder_layers=2, dim_feedforward=1024, dropout=0.2, num_classes=6):
        super(ConvLF_Net, self).__init__()
        self.cnn1 = nn.Sequential(
            nn.Conv1d(channel_in, 64, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=10, stride=2),
            nn.Conv1d(64, 64, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=10, stride=2),
        )
        self.cnn2 = nn.Sequential(
                nn.Conv1d(channel_in, 64, kernel_size=25, padding=12),
                nn.ReLU(),
                nn.MaxPool1d(kernel_size=10, stride=2),
                nn.Conv1d(64, 64, kernel_size=25, padding=12),
                nn.ReLU(),
                nn.MaxPool1d(kernel_size=10, stride=2),
        )
        self.cnn3 =nn.Sequential(
                nn.Conv1d(channel_in, 64, kernel_size=50, padding=25),
                nn.ReLU(),
                nn.MaxPool1d(kernel_size=10, stride=2),
                nn.Conv1d(64, 64, kernel_size=50, padding=25),
                nn.ReLU(),
                nn.MaxPool1d(kernel_size=10, stride=2),
        )
        self.cnn4 =nn.Sequential(
                nn.Conv1d(channel_in, 64, kernel_size=100, padding=50),
                nn.ReLU(),
                nn.MaxPool1d(kernel_size=10, stride=2),
                nn.Conv1d(64, 64, kernel_size=100, padding=50),
                nn.ReLU(),
                nn.MaxPool1d(kernel_size=10, stride=2),
        )
        self.flatten_and_project = nn.Linear(64, d_model)
        self.linear_transformer_encoder = TransformerEncoderModule(d_model, nhead, num_encoder_layers, dim_feedforward, dropout)
        self.classifier = nn.Linear(d_model, num_classes)

    def forward(self, x):
        x0 = x.permute(0, 2, 1)
        x1 = self.cnn1(x0)  # torch.Size([batch_size, 16, sequence_length])
        x2 = self.cnn2(x0)  # torch.Size([batch_size, 16, sequence_length])
        x3 = self.cnn3(x0)  # torch.Size([batch_size, 16, sequence_length])
        x4 = self.cnn4(x0)  # torch.Size([batch_size, 16, sequence_length])
        x = x1 + x2 + x3 + x4 
        x = x.permute(2, 0, 1)  # torch.Size([sequence_length, batch_size, 16])
        x = self.flatten_and_project(x)  # torch.Size([sequence_length, batch_size, d_model])
        x = self.linear_transformer_encoder(x)  # torch.Size([sequence_length, batch_size, d_model])
        x = x.mean(dim=0)  # torch.Size([batch_size, d_model
        x = self.classifier(x)  # torch.Size([batch_size, num_classes])
        return x


# 模型评估函数
def eval_model(test_loader, model_path):
    """
    评估模型并生成评估指标和可视化结果
    :param test_loader: DataLoader 对象
    :param model_path: 模型文件路径
    :return: 混淆矩阵、准确率、精确率、召回率、F1 分数、特异性
    """
      # 根据设备的可用性选择 CUDA 或 CPU
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # 创建模型
    model = ConvLF_Net().to(device)
    # 加载模型权重，并指定加载到当前设备
    model.load_state_dict(torch.load(model_path, map_location=device))
    print("[Info]: Finish loading model!", flush=True)

    label_total = []
    preds = []
    test_acc = 0.0
    final_outputs = []

    model.eval()
    test_pbar = tqdm(test_loader, position=0, leave=True)
    with torch.no_grad():
        for data, labels in test_pbar:
            data = data.float().to(device)
            outputs = model(data)
            _, test_pred = torch.max(outputs, 1)
            preds.append(test_pred.cpu().detach())

            labels = labels.to(device)
            label_total.append(labels.cpu().detach())

            final_outputs.append(outputs.cpu().detach())

            test_acc += (test_pred == labels).float().mean().item()

        print("Test Accuracy:", test_acc / len(test_loader))

    # 计算混淆矩阵
    conf_matrix = confusion_matrix(torch.cat(label_total).numpy(), torch.cat(preds).numpy())

    # 计算每个类的TP、FN、FP、TN
    num_classes = conf_matrix.shape[0]
    tp = np.diag(conf_matrix)  # True Positives for each class
    fn = np.sum(conf_matrix, axis=1) - tp  # False Negatives for each class
    fp = np.sum(conf_matrix, axis=0) - tp  # False Positives for each class
    tn = np.sum(conf_matrix) - (fp + fn + tp)  # True Negatives for each class

    # 计算准确率、精确率、召回率、F1 分数和特异性
    accuracy = np.sum(tp) / np.sum(conf_matrix)
    precision = np.mean(tp / (tp + fp))  # Precision
    recall = np.mean(tp / (tp + fn))  # Recall
    f1 = 2 * (precision * recall) / (precision + recall)  # F1 Score
    specificity = np.mean(tn / (tn + fp))  # Specificity

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"Specificity: {specificity:.4f}")

    # t-SNE 可视化
    final_outputs = torch.cat(final_outputs)
    X_embedded = TSNE(n_components=2, random_state=42).fit_transform(final_outputs.numpy())

    unique_labels = np.unique(torch.cat(label_total).numpy())
    palette = sns.color_palette("Set1", n_colors=len(unique_labels))

    plt.figure(figsize=(15, 6))

    # 绘制 t-SNE 映射结果
    plt.subplot(1, 2, 1)
    plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False,
                    labelleft=False)
    sns.scatterplot(x=X_embedded[:, 0], y=X_embedded[:, 1], hue=torch.cat(label_total).numpy(), palette=palette,
                    legend='full')
    plt.title("t-SNE Visualization")
    plt.savefig("/root/My_Project/backend/reports/t-SNE_Visualization.png")

    # 绘制混淆矩阵
    plt.subplot(1, 2, 2)
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", cbar=True)
    plt.xlabel('Predicted labels')
    plt.ylabel('True labels')
    plt.savefig("/root/My_Project/backend/reports/Confusion_Matrix.png")

    plt.show()

    return accuracy, precision, recall, f1, specificity


# 主函数入口
# 其他导入和方法定义...
if __name__ == "__main__":
    try:
        file_path = sys.argv[1]
        model_path = sys.argv[2]

        # 执行诊断并生成结果
        print("Starting model evaluation...")

        # 加载测试数据和模型
        test_loader = get_test_loader(file_path, batch_size=32)

        # 执行模型评估
        accuracy, precision, recall, f1, specificity = eval_model(test_loader, model_path)

        # 设置诊断结果
        diagnosis_result = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "specificity": specificity
        }

        # 输出诊断结果为 JSON 格式
        print("diagnosis_result-eval",json.dumps(diagnosis_result))

    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e.stderr}", file=sys.stderr)
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        # 输出错误到标准错误流
        print(f"Error: {str(e)}", file=sys.stderr)
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


