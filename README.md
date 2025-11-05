# 溯言计划 - 农产品溯源后端系统

## 项目简介
基于Flask的农产品溯源管理系统，通过AI技术为农产品图片自动生成溯源故事关键词。

## 功能特性
- ✅ 多文件上传到腾讯云COS
- ✅ 豆包大模型AI图片分析
- ✅ 自动生成农产品关键词
- ✅ 素材时间线管理
- ✅ MySQL云数据库支持

## 技术栈
- **后端**: Python Flask
- **AI服务**: 豆包大模型
- **数据库**: MySQL
- **云存储**: 腾讯云COS
- **部署**: 腾讯云轻量应用服务器

## 项目结构
```
yanshuimitao-backend/
├── app.py # 主应用文件
├── config.py # 配置文件
├── models.py # 数据模型
├── requirements.txt # 依赖列表
├── .env # 环境变量（不上传）
└── utils/ # 工具类
├── cloud_storage.py # 云存储工具
└── doubao_ai_generator.py # AI生成器
```


## 快速开始
1. 安装依赖：`pip install -r requirements.txt`
2. 配置环境变量：复制 `.env.example` 为 `.env`
3. 运行应用：`python app.py`
4. 访问：http://localhost:5000

## API文档
- `GET /api/health` - 健康检查
- `POST /api/upload` - 上传素材
- `GET /api/materials` - 获取素材列表
- `DELETE /api/materials/{id}` - 删除素材

## 许可证

MIT License
