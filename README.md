# RAG-PDF-System

基于 FastAPI + LangChain + Milvus + Qwen 的多格式文档 RAG（检索增强生成）系统，支持多跳推理、知识库管理、评估体系和 AI 助手编排。

## 技术栈

| 组件 | 技术 |
|---|---|
| 后端框架 | FastAPI (Python 3.10+) |
| 前端 | Vue 3 + Element Plus + Pinia + Vite |
| ORM | SQLAlchemy 2.x (SQLite 本地开发) |
| 向量数据库 | Milvus 2.3.4 |
| 嵌入模型 | DashScope text-embedding-v1 |
| 大语言模型 | 通义千问 Qwen-Max |
| 重排序 | DashScope gte-rerank |
| 消息队列 | RabbitMQ 3 + Celery 5.x |
| 缓存 / 记忆 | Redis 7 |
| 对象存储 | MinIO |

## 前置依赖

- **Python 3.10+**
- **Node.js 18+**
- **Docker & Docker Compose**（用于启动基础服务）
- **DashScope API Key** — 从 [阿里云 DashScope](https://dashscope.aliyun.com/) 获取

## 快速启动

### 1. 克隆项目

```bash
git clone https://github.com/xiebrown/RAGsystem.git
cd RAGsystem
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入必要配置：

```env
# ===== 必填 =====
SECRET_KEY=<随机字符串，可用 openssl rand -hex 32 生成>
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ===== 基础服务（Docker 默认值，无需修改） =====
MILVUS_HOST=localhost
MILVUS_PORT=19530
REDIS_URL=redis://localhost:6379/0
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=rag-documents
```

### 3. 启动基础服务

```bash
docker compose -f docker/docker-compose.yml up -d
```

启动后确认各服务状态：

| 服务 | 端口 | 管理界面 |
|---|---|---|
| Milvus | 19530 | — |
| MinIO | 9000 | http://localhost:9001 |
| RabbitMQ | 5672 | http://localhost:15672 |
| Redis | 6379 | — |
| Flower (Celery 监控) | 5555 | http://localhost:5555 |

### 4. 安装 Python 依赖

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 5. 启动后端

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

后端启动后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/v1/health

### 6. 启动 Celery Worker（可选，文档处理需要）

```bash
celery -A src.worker.celery_app worker --loglevel=info -P solo
```

### 7. 启动前端（可选）

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器运行在 http://localhost:5173 ，API 请求自动代理到后端 8000 端口。

---

## Docker 一键启动

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

这将同时启动所有 7 个服务：app (后端)、worker (Celery)、flower、rabbitmq、redis、etcd、minio、milvus-standalone。

## 项目结构

```
RAGsystem/
├── config/                   # 配置文件
│   ├── settings.py           # 应用配置（Pydantic Settings）
│   ├── database.py           # 数据库连接配置
│   ├── embedding.py          # 嵌入模型配置
│   └── logging.yaml          # 日志配置
├── src/
│   ├── main.py               # FastAPI 应用入口
│   ├── settings.py           # 全局设置（.env 驱动）
│   ├── api/
│   │   ├── dependencies.py   # JWT 鉴权依赖
│   │   └── routers/          # 路由模块
│   │       ├── auth.py       # 注册 / 登录
│   │       ├── chat.py       # RAG 对话接口
│   │       ├── agent.py      # AI Agent 管理
│   │       ├── assistant.py  # 助手编排
│   │       ├── knowledge_base.py  # 知识库管理
│   │       ├── evaluation.py # 评估体系
│   │       ├── storage.py    # MinIO 文件管理
│   │       ├── monitor.py    # 文档状态监控
│   │       └── health.py     # 健康检查
│   ├── database/
│   │   ├── models.py         # SQLAlchemy 数据模型
│   │   ├── sql_session.py    # 数据库会话管理
│   │   └── vector_db.py      # Milvus 向量库客户端
│   ├── embedding/            # 嵌入服务
│   ├── llm/                  # 大模型客户端
│   ├── processors/           # 文档解析器（PDF/DOCX/XLSX/PPTX/MD/HTML）
│   ├── retrieval/            # 检索 & 重排序
│   ├── services/             # 核心业务服务
│   │   ├── rag_service.py    # RAG 主流程（单跳 / 多跳）
│   │   ├── memory_service.py # 短期 + 长期记忆
│   │   └── evaluator.py      # RAG 评估（忠实性 / 相关性 / 准确性）
│   ├── utils/                # 工具函数（JWT / 日志 / 预览）
│   └── worker/               # Celery 任务
│       ├── celery_app.py     # Celery 配置
│       └── tasks.py          # 文档处理异步任务
├── frontend/                 # Vue 3 前端
│   └── src/views/            # 页面组件
├── docker/                   # Docker 部署配置
├── scripts/                  # 评估 & 工具脚本
├── docs/                     # 文档
├── .env.example              # 环境变量模板
├── .env                      # 本地环境变量（不入库）
├── .gitignore
└── requirements.txt
```

## API 概览

所有 API 前缀：`/api/v1`

| 路由 | 说明 | 鉴权 |
|---|---|---|
| `POST /auth/register` | 用户注册 | 否 |
| `POST /auth/login/access-token` | 登录获取 JWT | 否 |
| `GET /health` | 健康检查 + Celery 状态 | 否 |
| `POST /chat/` | 核心 RAG 对话 | 是 |
| `GET /chat/sessions` | 获取会话列表 | 是 |
| `CRUD /knowledge-bases` | 知识库增删改查 | 是 |
| `POST /knowledge-bases/{id}/documents/upload` | 上传文档 | 是 |
| `CRUD /assistants` | 助手编排管理 | 是 |
| `CRUD /agents` | AI Agent 管理 | 是 |
| `CRUD /evaluations` | 评估任务管理 | 是 |
| `GET /storage/files` | MinIO 文件浏览 | 是 |
| `GET /monitor/stats` | 文档处理状态统计 | 是 |

完整文档访问 http://localhost:8000/docs

## 核心功能

### RAG 对话
- 单跳检索：向量检索 + 重排序 + LLM 生成
- 多跳推理：自动分解子问题，逐跳检索，融合证据后作答
- 会话管理：Redis 短期记忆 + Milvus 长期记忆

### 知识库管理
- 支持格式：PDF、DOCX、XLSX、PPTX、Markdown、HTML、TXT
- 文档上传 → 异步解析 → 分块 → 向量化 → 入库全流程
- 自定义分块策略（块大小、重叠量）
- 批量操作、状态监控、文档预览

### 评估体系
- 自动生成 QA 数据集（单跳 / 多跳 / 错误类型）
- LLM-as-Judge 评估（忠实性、相关性、上下文精度、准确性）
- 延迟分位数统计
- Markdown 评估报告导出

### AI 助手编排
- 可配置系统提示词、温度、Top-K、重排序策略
- 绑定知识库组合
- 支持 Function Call / ReAct / Plan-Execute 三种 Agent 类型

## 许可证

MIT
