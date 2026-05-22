# 🥔 Potato Check-in | 高颜值 New-API 自动签到面板

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

一个轻量、美观、开箱即用的 New-API 公益站自动签到控制台。告别繁琐的定时任务脚本，用最直观的可视化界面管理你的所有签到任务。

## ✨ 核心特性

- 🎨 **极简高颜值 UI**：基于 Tailwind CSS 构建的温暖博客风卡片式界面，支持深度个性化定制（头像、昵称、签名均可自定义）。
- ⏰ **独立定时任务**：抛弃一刀切，为每个站点单独设置每天的触发签到时间。
- 📅 **可视化打卡日历**：以直观的网格日历形式展示每个站点的月度签到记录，成功与失败一目了然。
- 🔔 **多渠道失败提醒**：支持 iOS Bark 极简推送与 SMTP 邮件推送，仅在签到失败时打扰你。
- 🐳 **纯净 Docker 部署**：一键构建，数据持久化隔离，不污染宿主机环境。

---

## 📸 界面预览

> *主界面*<img width="1920" height="919" alt="image" src="https://github.com/user-attachments/assets/ca56727c-0fb7-4bab-87b5-2bb060281fef" />

> *签到日历*<img width="1920" height="919" alt="image" src="https://github.com/user-attachments/assets/13b41d42-0a68-46f1-ad5c-0308f6bfaf27" />
> *通知设置*<img width="1920" height="919" alt="image" src="https://github.com/user-attachments/assets/1846b4e5-c758-497b-b418-2dff7cfca449" />


---

## 🚀 快速部署指南

本项目推荐使用 **Docker Compose** 进行部署，极其简单，全过程只需两分钟。

### 1. 环境准备
请确保你的服务器已经安装了 `git`、`docker` 和 `docker-compose`。

### 2. 拉取仓库
在你的服务器终端执行以下命令，将代码克隆到本地：
```bash
git clone [https://github.com/LRZ9712/newapi-checkin.git](https://github.com/LRZ9712/newapi-checkin.git)
cd newapi-checkin
```

### 3. 配置账号与密码（可选但建议）
项目默认的管理员账号为 `admin`，密码为 `123456`。
为了安全，建议在部署前修改 `docker-compose.yml` 中的环境变量：
```bash
nano docker-compose.yml
```
找到 `environment` 部分，修改为你自己的账号和密码：
```yaml
    environment:
      - TZ=Asia/Shanghai
      - ADMIN_USER=你的专属账号
      - ADMIN_PASS=你的超级密码
      - SECRET_KEY=随意一串随机字符用于加密
```
*(修改完成后按 `Ctrl+O` 保存，`Enter` 确认，`Ctrl+X` 退出)*

### 4. 一键构建并启动
在项目根目录（`docker-compose.yml` 所在的目录）执行：
```bash
docker-compose up -d --build
```

等待终端跑完构建流程并提示 `Started` 后，部署即告完成！🎉

---

## 💻 使用说明

### 1. 访问面板
打开浏览器，访问 `http://你的服务器IP:5000`。
输入你在第三步配置的账号和密码进入系统。

### 2. 获取站点抓包信息
在添加站点时，你需要提供目标公益站的 `New-API User ID` 和 `Session Cookie`：
1. 登录目标公益站，按 `F12` 打开浏览器开发者工具，切换到 **Network (网络)**。
2. 刷新网页，找到任意一个指向该站点的 API 请求（如 `self` 或 `status`）。
3. 在请求标头 (Request Headers) 中找到：
   - `new-api-user`: 一串纯数字（如 `60` 或 `230`）。
   - `Cookie`: 找到 `session=...` 开头的那一长串字符，完整复制。

### 3. 个性化与通知设置
点击页面右上角的 **「⚙️ 系统与通知配置」**：
- **外观设置**：修改网站标题、展示名、头像链接和个性签名，打造完全属于你的私人面板。
- **通知配置**：填入你的 Bark 链接或 SMTP 邮箱配置，点击保存并发送测试，确保能正常收到消息。

---

## 🔄 更新与维护

如果后续仓库有代码更新，你可以按以下步骤无损升级（不会丢失数据库文件）：

```bash
cd newapi-checkin
git pull
docker-compose down
docker-compose up -d --build
```

---

## 📜 许可证

本项目采用 [MIT License](LICENSE) 开源协议。你可以自由使用、修改和分发，但请保留原作者信息。
```
