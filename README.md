# Image Generate Demo

这是一个使用 端脑云 DeepSeek R1 蒸馏模型和 Flux 模型生成图片的 Web 应用演示项目。

粉丝福利：现在用我的邀请链接 https://cephalon.cloud/share/register-landing?invite_id=X46Dzv 或者邀请码 X46Dzv，还有我专属的注册奖励，还可以额外免费送5000端脑值

## 功能特点

- 基于文本提示生成图片
- 可自定义图片尺寸

## 技术栈

- Python Flask 作为后端框架
- HTML/CSS 用于前端界面
- ComfyUI 用于图片生成

## 安装和运行

1. 克隆项目仓库
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行应用：
   ```bash
   python app.py
   ```
4. 在浏览器中访问 `http://localhost:5000`

## 使用说明

1. 在文本框中输入你想要生成的图片描述
2. 根据需要调整参数
3. 点击生成按钮
4. 等待图片生成完成

## 目录结构

```
.
├── app.py              # Flask 应用主文件
├── requirements.txt    # 项目依赖
├── static/            # 静态资源目录
│   ├── css/          # CSS 样式文件
│   └── images/       # 生成的图片存储目录
└── templates/         # HTML 模板目录
```