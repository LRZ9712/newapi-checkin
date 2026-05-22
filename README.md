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

> **💡 提示：** 建议你在这里上传两张截图（一张主面板，一张日历弹窗），展示它的美观度。
> 
> *在这里插入主界面截图*
> *在这里插入日历界面截图*

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
