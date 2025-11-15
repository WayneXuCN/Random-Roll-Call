# 随机点名软件

适用于课堂教学场景的随机点名软件，具备Excel导入、随机抽取、历史记录等功能。

## 功能特性

- **Excel导入功能**：支持.xlsx和.xls格式文件导入学生姓名列表
- **随机点名功能**：基于高质量随机数算法的公平随机抽取
- **多学生点名**：支持1-20人同时点名
- **防重复机制**：可配置是否允许同一轮次中重复抽取同一学生
- **动画效果**：平滑的随机滚动动画效果
- **简洁UI**：蓝色系专业界面设计，适合教学场景
- **数据存储**：本地存储学生名单和点名历史
- **历史记录**：完整的点名记录和统计功能

## 环境要求

- Python 3.9+
- uv 包管理器

## 安装与运行

### 使用uv管理虚拟环境

1. 克隆或下载项目
2. 安装依赖：
```bash
uv sync
```

3. 运行软件：
```bash
uv run python -m src.main
```

### 手动安装依赖

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行软件：
```bash
python -m src.main
```

## 使用方法

1. 准备Excel模板文件，确保第一列包含学生姓名
2. 启动软件并点击"导入名单"按钮
3. 设置点名人数（1-20人）并选择是否启用防重复
4. 点击"开始点名"按钮，稍后点击"停止点名"获取结果
5. 查看历史记录和统计信息

## 项目结构

```
random_roll_call/
├── src/
│   ├── main.py          # 主程序入口
│   ├── excel_importer.py # Excel导入功能
├── data/                # 数据存储目录
├── docs/                # 文档目录
├── tests/               # 测试文件目录
├── template.xlsx        # Excel模板文件
├── pyproject.toml       # 项目配置文件
└── README.md            # 项目说明文件
```

## 技术栈

- GUI框架：PyQt6
- 数据处理：pandas, numpy
- Excel处理：openpyxl
- 构建工具：setuptools

## 开发与测试

运行测试：
```bash
uv run pytest
```

格式化代码：
```bash
uv run black src/
```

## 打包为可执行文件

使用PyInstaller打包：
```bash
uv run pip install pyinstaller
uv run pyinstaller --onefile --windowed --name "随机点名系统" --icon=icon.ico src/main.py
```

## 许可证

MIT License