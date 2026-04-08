# HiAgent 心理疗愈智能体项目准则

本项目是一个基于 FastAPI (后端) 和 Vue 3 + Vite (前端) 开发的心理社交/疗愈平台，集成了 HITSZ HiAgent 2.0 智能体服务。

请忽略.claudeignore中的文件。

## 🚀 常用指令

### 后端 (Python/FastAPI)
- **启动开发服务器**: `cd backend && uvicorn main:app --reload`
- **安装依赖**: `pip install -r requirements.txt`

### 前端 (Vue 3/Vite)
- **进入开发模式**: `cd frontend && npm run dev`
- **安装依赖**: `npm install`
- **构建生产版本**: `npm run build`

## 🛠 项目架构与关键逻辑

### 1. 智能体集成 (HiAgentClient)
- **API 通道**: 必须使用 `/api/proxy/api/v1/` 路径以绕过 CSRF 限制。
- **身份验证**: 
    - `UserID`: 严格限制在 1-20 字符以内（例如：`ikrokx_001`）。
    - `Header`: 必须包含 `Apikey`。
- **流数据处理**: 
    - 响应行前缀为 `data:data: `。
    - 需区分 `event: think_message` (思考过程) 和 `event: message` (正式回答)。

### 2. 代码风格规范
- **后端**: 遵循 PEP8，使用 `HiAgentClient` 类进行模块化封装。接口返回格式统一为 `{"thought": "...", "reply": "..."}`。
- **前端**: Vue 3 组合式 API (Script Setup)。使用 `markdown-it` 解析 AI 回复。

## 🧪 核心开发重点
- **会话持久化**: 优先从 `localStorage` 获取 `AppConversationID` 以维持对话上下文。
