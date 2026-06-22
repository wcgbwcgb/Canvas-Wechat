# Canvas-WeChat Clawbot

> 🤖 AI 驱动的微信 Canvas LMS 助教机器人

通过微信官方 **iLink Bot API**（ClawBot 插件），实现：
- 📋 **定时同步** Canvas 课程作业、公告、成绩
- ⚠️ **主动提醒** 作业逾期和即将到期
- 💬 **对话查询** 课程信息（AI Agent + RAG）

---

## 架构

```
Canvas LMS ←→ Sync Worker → PostgreSQL + Redis ←→ iLink Gateway ←→ 微信
                                  ↑                       ↑
                              AI Chat Service      Notification Engine
                              (LangChain Agent)    (Celery Beat)
```

微信通道解耦设计 —— Canvas 业务逻辑完全不依赖微信。切换通道只需改 `ilink/` 层。

---

## 快速开始

### 前置要求

- Python 3.11+
- Docker（用于 PostgreSQL + Redis）
- 微信个人号（建议专用测试号，微信 ≥ 8.0.70）

### 1. 克隆并安装

```bash
git clone <repo-url> canvas-wechat
cd canvas-wechat
pip install -e '.[dev]'
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入：
#   CANVAS_BASE_URL, CANVAS_CLIENT_ID, CANVAS_CLIENT_SECRET
#   DEEPSEEK_API_KEY (AI 对话功能)
#   ILINK_BOT_TOKEN (扫码后自动获取)
```

### 3. 启动基础设施

```bash
docker compose up -d postgres redis
alembic upgrade head
```

### 4. 扫描 iLink 二维码连接微信

```bash
make run
# 访问 http://localhost:8000/ilink/qrcode
# 用微信扫描返回的二维码
# 扫描确认后，将 bot_token 填入 .env 的 ILINK_BOT_TOKEN
# 重启服务
```

### 5. 绑定 Canvas 账号

在微信中给 Bot 发送 `/bind`，点击返回的链接完成 Canvas OAuth2 授权。

### 6. 启动后台任务（可选，用于定时同步和通知）

```bash
make worker   # Celery worker
make beat     # Celery Beat 定时调度
```

### 一键启动全部服务

```bash
docker compose up -d
```

---

## 目录结构

```
canvas-wechat/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置
│   ├── ilink/               # iLink Bot API 网关
│   │   ├── client.py        # HTTP 客户端
│   │   ├── poller.py        # 长轮询主循环
│   │   ├── message_handler.py
│   │   └── context_token.py # Token 持久化 + 补发
│   ├── auth/                # Canvas OAuth2 绑定
│   ├── sync/                # Canvas 数据同步
│   ├── chat/                # AI 对话 (Phase 4)
│   ├── notifications/       # 通知引擎
│   ├── models/              # SQLAlchemy ORM
│   ├── db/                  # 数据库客户端
│   └── middleware/          # FastAPI 中间件
├── alembic/                 # 数据库迁移
├── tests/
├── docker-compose.yml
└── Dockerfile
```

---

## API 端点

| 端点 | 说明 |
|------|------|
| `GET /health` | 健康检查 |
| `GET /status` | 详细状态（Redis/Postgres/iLink/Canvas） |
| `GET /ilink/qrcode` | 获取 iLink Bot 登录二维码 |
| `GET /auth/canvas/callback` | Canvas OAuth2 回调 |

---

## 实施阶段

- [x] Phase 1: 项目脚手架 + iLink 网关 + Canvas 绑定
- [x] Phase 2: Canvas 数据同步（作业/公告/成绩）
- [x] Phase 3: 通知系统（逾期检测 + 补发）
- [ ] Phase 4: AI 对话（LangChain Agent + RAG）
- [ ] Phase 5: 生产加固

---

## 文档参考

- [Canvas LMS REST API](https://developerdocs.instructure.com/)
- [微信 iLink Bot API](https://github.com/Tencent/openclaw-weixin)
- [Canvas Python SDK (canvasapi)](https://github.com/ucfopen/canvasapi)

---

## License

MIT
