# Instructure Developer Documentation Portal — 技术文档

> **URL:** [https://developerdocs.instructure.com/](https://developerdocs.instructure.com/)
> **平台:** GitBook
> **目标受众:** 希望在 Instructure 生态系统内构建集成的开发者、教育科技工程师
> **最后更新:** 2026 年 6 月

---

## 目录

1. [概述](#1-概述)
2. [文档架构](#2-文档架构)
3. [快速入门指南](#3-快速入门指南)
4. [服务目录](#4-服务目录)
5. [Canvas LMS REST API](#5-canvas-lms-rest-api)
6. [认证与授权](#6-认证与授权)
7. [LTI (学习工具互操作性)](#7-lti-学习工具互操作性)
8. [Data Access Platform (DAP)](#8-data-access-platform-dap)
9. [其他服务](#9-其他服务)
10. [LLM 集成](#10-llm-集成)
11. [开发者工具与最佳实践](#11-开发者工具与最佳实践)

---

## 1. 概述

Instructure Developer Documentation Portal 是 Instructure 公司所有产品的 API 文档统一入口。该门户使用 GitBook 构建，提供以下核心能力：

- **Canvas LMS REST API** — 核心学习管理系统的完整 API 参考
- **多种认证方式** — OAuth2、Developer Keys、InstAccess Tokens
- **LTI 标准支持** — LTI 1.3、Deep Linking、Names and Roles Provisioning Service、Assignment and Grades Service
- **数据平台** — Data Access Platform (DAP)、Live Events、Data Sync
- **多产品线** — Catalog、Commons、Studio、New Quizzes、Parchment Digital Badges 等

> **注意：** 该文档直接从 [Canvas LMS 源代码](https://github.com/instructure/canvas-lms) 自动生成。

---

## 2. 文档架构

### 2.1 顶层导航结构

```
Introduction (首页 — https://developerdocs.instructure.com/)
├── Get Started (快速入门 — /get_started)
└── Services (服务目录 — /services)
    ├── Elevate Standards Alignment - AB Connect
    ├── Canvas LMS
    ├── Catalog
    ├── Commons
    ├── Data Access Platform (DAP)
    ├── Data Sync
    ├── Data Hub
    ├── Instructure UI
    ├── New Quizzes
    ├── Parchment Digital Badges
    └── Studio
```

### 2.2 机器可读入口

| 格式 | URL | 用途 |
|------|-----|------|
| llms.txt | `https://developerdocs.instructure.com/llms.txt` | 完整站点地图（Markdown 格式） |
| llms-full.txt | `https://developerdocs.instructure.com/llms-full.txt` | 完整文档内容（LLM 适配） |
| Markdown | `https://developerdocs.instructure.com/readme.md` | 各页面 Markdown 源文件 |
| 动态查询 | `GET /readme.md?ask=<问题>` | AI 驱动的文档问答 |

### 2.3 外部资源链接

- **社区论坛:** [https://community.canvaslms.com/](https://community.canvaslms.com/)
- **Canvas LMS GitHub:** [https://github.com/instructure/canvas-lms](https://github.com/instructure/canvas-lms)
- **IMS Global LTI 规范:** [https://www.imsglobal.org/](https://www.imsglobal.org/)

---

## 3. 快速入门指南

> 来源：[https://developerdocs.instructure.com/get_started](https://developerdocs.instructure.com/get_started)

### 3.1 核心使用场景

| 场景 | 所用 API | 示例 |
|------|---------|------|
| **集成 Canvas LMS** | Canvas REST API | 自动化课程创建、同步学生数据、获取成绩 |
| **获取教育数据分析** | Data Access Platform (DAP) | 学生表现分析、机构报表、BI 工具集成 |
| **改进评估流程** | Quizzes API | 创建/分享测验、获取测验结果、管理测验排期 |
| **增强课堂体验** | Canvas REST API | 个性化课程信息、通知学生、即时作业反馈 |

### 3.2 开发工作流

#### 第一步：获取访问密钥

每个服务的认证方式不同，需要查阅对应服务的子页面：

| 服务 | 认证文档位置 |
|------|------------|
| **Canvas LMS** | [OAuth2 概述](https://developerdocs.instructure.com/services/canvas/oauth2/file.oauth) / [Developer Keys](https://developerdocs.instructure.com/services/canvas/oauth2/file.developer_keys) |
| **Data Access Platform** | [DAP 认证](https://developerdocs.instructure.com/services/dap/query-api/oauth_login) |
| **Elevate Standards Alignment** | [AB Connect 认证](https://developerdocs.instructure.com/services/ab-connect/introduction/authentication) |

#### 第二步：发送第一个请求

- 使用获取的认证密钥/密钥对
- 选择要测试的 API
- 若文档中有 **"Test it"** 按钮，可直接在页面上测试
- 或使用 Postman / curl 进行测试

#### 第三步：理解响应格式

**✅ 成功响应 (200/201):**

```json
{
  "id": 123,
  "name": "Introduction to Biology",
  "course_code": "BIO101"
}
```

**⚠️ 错误响应 (4xx):**

```json
{
  "errors": [
    {
      "message": "Invalid access token."
    }
  ]
}
```

**📑 分页处理：**

Canvas 等服务对大量数据使用分页机制，Response Header 中会包含 `Link` 字段：

```
Link: <https://canvas.instructure.com/api/v1/courses?page=2>; rel="next"
```

#### 推荐工具

- [Postman](https://www.postman.com/) — API 测试与可视化
- JSONView（浏览器扩展） — JSON 响应美化

---

## 4. 服务目录

### 4.1 完整服务列表

| 服务名称 | 描述 | 文档入口 |
|---------|------|----------|
| **Canvas LMS** | 核心学习管理系统 REST API、LTI 集成、数据服务、权限管理 | [/services/canvas](https://developerdocs.instructure.com/services/canvas) |
| **Catalog** | 课程目录与注册管理 API | [/services/catalog](https://developerdocs.instructure.com/services/catalog) |
| **Commons** | 学习资源共享平台 API | [/services/commons](https://developerdocs.instructure.com/services/commons) |
| **Data Access Platform (DAP)** | 集中式数据仓库，提供分析查询 | [/services/dap](https://developerdocs.instructure.com/services/dap) |
| **Data Hub** | 教育数据标准互操作 (Ed-Fi) | [api.ed-fi.org](https://api.ed-fi.org/) |
| **Data Sync** | OneRoster、Grades Exchange、Interop 数据同步 | [/services/datasync](https://developerdocs.instructure.com/services/datasync) |
| **Elevate Standards Alignment (AB Connect)** | 课程标准对齐服务 | [/services/ab-connect](https://developerdocs.instructure.com/services/ab-connect) |
| **Instructure UI** | Instructure 设计系统/组件库 | [/services/instui](https://developerdocs.instructure.com/services/instui) |
| **New Quizzes** | 新一代测验引擎 API | [/services/new-quizzes](https://developerdocs.instructure.com/services/new-quizzes) |
| **Parchment Digital Badges** | 数字徽章颁发与管理 | [/services/parchment-digital-badges](https://developerdocs.instructure.com/services/parchment-digital-badges) |
| **Studio** | 视频学习平台 API | [/services/studio](https://developerdocs.instructure.com/services/studio) |

---

## 5. Canvas LMS REST API

> 来源：[https://developerdocs.instructure.com/services/canvas](https://developerdocs.instructure.com/services/canvas)

### 5.1 基本规范

| 规范项 | 说明 |
|--------|------|
| **传输协议** | HTTPS（HTTP 请求会被重定向到 HTTPS） |
| **响应格式** | JSON |
| **整数 ID** | 64 位整数；可通过 Header `Accept: application/json+canvas-string-ids` 强制转为字符串 |
| **布尔参数** | `true/false`, `t/f`, `yes/no`, `y/n`, `on/off`, `1/0` |
| **POST/PUT 编码** | 默认 `application/x-www-form-urlencoded`；可选 `application/json` |
| **时间戳** | ISO 8601 格式，UTC 时区：`YYYY-MM-DDTHH:MM:SSZ` |

#### 请求示例

**Form 编码请求：**
```
name=test+name&file_ids[]=1&file_ids[]=2&sub[name]=foo&sub[message]=bar&flag=y
```

**对应的 JSON 编码请求：**
```json
{
  "name": "test name",
  "file_ids": [1, 2],
  "sub": { "name": "foo", "message": "bar" },
  "flag": true
}
```

### 5.2 API 基础地址

```
https://<your-canvas-instance>/api/v1/
```

### 5.3 Canvas LMS 文档子模块

| 模块 | 描述 |
|------|------|
| **Basics** | GraphQL、API 变更日志、SIS IDs、分页、限流、文件上传、复合文档 |
| **OAuth2** | OAuth2 概述、OAuth2 端点、Developer Keys |
| **Resources** | 190+ API 资源（见下方列表） |
| **Outcomes** | 学习成果 CSV 格式 |
| **Group Categories** | 分组类别 CSV、Differentiation Tags CSV |
| **SIS** | 学生信息系统 CSV 格式 |
| **External Tools** | LTI、xAPI、Canvas Roles、Plagiarism Detection |
| **Data Services** | Live Events（Canvas / Caliper IMS 1.1） |
| **Permissions** | 完整权限列表与详细说明（100+ 权限） |

### 5.4 主要 API 资源分类

#### 账户与管理
`Accounts`, `Admins`, `Account Reports`, `Account Notifications`, `Authentication Providers`, `Brand Configs`, `Feature Flags`, `Sandboxes`

#### 课程与内容
`Courses`, `Modules`, `Pages`, `Files`, `Content Exports`, `Content Migrations`, `Content Shares`, `Blueprint Courses`

#### 用户与注册
`Users`, `Enrollments`, `Sections`, `Enrollment Terms`, `Logins`, `Communication Channels`, `User Observees`

#### 作业与评估
`Assignments`, `Assignment Groups`, `Submissions`, `Peer Reviews`, `Assignment Extensions`, `Moderated Grading`

#### 成绩
`Grading Standards`, `Grading Periods`, `Grading Period Sets`, `Custom Gradebook Columns`, `Grade Change Log`, `Gradebook History`, `Late Policy`, `What If Grades`

#### 测验 (Classic)
`Quizzes`, `Quiz Questions`, `Quiz Question Groups`, `Quiz Submissions`, `Quiz Reports`, `Quiz Statistics`, `Quiz Extensions`

#### 新测验 (New Quizzes)
`New Quizzes`, `New Quiz Items`, `New Quizzes Accommodations`, `New Quizzes Reports`

#### 讨论与通知
`Discussion Topics`, `Announcements`, `Conversations`, `CommMessages`, `Notification Preferences`

#### 其他
`Calendar Events`, `Appointment Groups`, `Collaborations`, `Conferences`, `ePortfolios`, `Bookmarks`, `Favorites`, `Groups`, `Outcomes`, `Rubrics`, `Search`, `Smart Search`, `Media Objects`

#### AI 相关
`AI Conversations`, `AI Experiences`, `Study Assist`, `Smart Search`

#### SIS 集成
`SIS Imports`, `SIS Import Errors`, `SIS Integration`

#### 开发者工具
`Access Tokens`, `Developer Keys`, `JWTs`, `Public JWK`, `InstAccess Tokens`, `API Token Scopes`, `LTI Registrations`

#### Live Events 数据类型
`Account`, `Asset`, `Assignment`, `Attachment`, `Content`, `Conversation`, `Course`, `Discussion`, `Enrollment`, `External Tool`, `Grade`, `Group`, `Learning`, `Logged`, `Module`, `Outcome`, `Plagiarism`, `Quiz`, `Rubric`, `SIS`, `Submission`, `Syllabus`, `User`, `Wiki`

### 5.5 OpenAPI 3.0 支持

Canvas LMS 支持从源代码生成 OpenAPI 3.0 规范文件：

```bash
bundle exec rake doc:openapi
```

生成文件位置：`public/doc/openapi/canvas.openapi.yaml`

**支持的集成工具：**
- Swagger Editor（导入 YAML）
- Swagger UI（交互式 API 文档）
- Postman（导入为 Collection）
- OpenAPI Generator（代码生成器）

### 5.6 GraphQL 支持

Canvas LMS 同时提供 GraphQL 接口，文档位于：
- [https://developerdocs.instructure.com/services/canvas/basics/file.graphql](https://developerdocs.instructure.com/services/canvas/basics/file.graphql)

---

## 6. 认证与授权

> 来源：[https://developerdocs.instructure.com/services/canvas/oauth2/file.oauth](https://developerdocs.instructure.com/services/canvas/oauth2/file.oauth)

### 6.1 Canvas API 认证

Canvas 使用 **OAuth2 (RFC-6749)** 进行 API 认证和授权，同时用于 LTI Advantage 服务认证。

#### 关键特征

| 特性 | 说明 |
|------|------|
| **Token 有效期** | 1 小时（2015 年 10 月之后签发的 Developer Key） |
| **Token 刷新** | 使用 Refresh Token 获取新 Access Token，无需用户重新授权 |
| **推荐方式** | HTTP `Authorization: Bearer <token>` Header |
| **备选方式** | Query String 参数 `?access_token=<token>`（不推荐） |

#### 认证 Header 方式（推荐）：

```bash
curl -H "Authorization: Bearer <ACCESS-TOKEN>" "https://canvas.instructure.com/api/v1/courses"
```

#### Query String 方式（不推荐）：

```bash
curl "https://canvas.instructure.com/api/v1/courses?access_token=<ACCESS-TOKEN>"
```

### 6.2 OAuth2 完整授权流程

#### 步骤 1：获取 Client ID/Secret

- **Canvas Cloud（Instructure 托管）：** 由机构管理员签发 Developer Keys
- **开源 Canvas：** 在 Site Admin 账户中生成
- **LTI 供应商注意：** Developer Keys 是机构范围的，多机构工具需要根据 LTI 启动参数（如 `custom_canvas_api_domain`）查找正确的 Key

#### 步骤 2：重定向用户请求授权

```
GET https://<canvas-install-url>/login/oauth2/auth?client_id=XXX&response_type=code&state=YYY&redirect_uri=https://example.com/oauth2response
```

可选 `scope` 参数（身份认证）：`scope=/auth/userinfo`

#### 步骤 3：回调处理

**成功回调：**
```
http://www.example.com/oauth2response?code=XXX&state=YYY
```

**错误回调：**
```
http://www.example.com/oauth2response?error=access_denied&error_description=a_description&state=YYY
```

**原生应用：** Canvas 重定向到 `/login/oauth2/auth?code=<code>`，应用从 WebView URL 中提取 code。

#### 步骤 4：交换 Access Token

```http
POST /login/oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&client_id=<your_client_id>
&client_secret=<your_client_secret>
&redirect_uri=<same_redirect_uri>
&code=<code_from_step_2>
&replace_tokens=1          # 可选：销毁旧 Token
```

#### 步骤 5：刷新 Access Token

```http
POST /login/oauth2/token

grant_type=refresh_token
&client_id=<your_client_id>
&client_secret=<your_client_secret>
&refresh_token=<refresh_token>
```

> **注意：** 刷新操作不会返回新的 Refresh Token，同一 Refresh Token 可重复使用。

#### 登出

```http
DELETE /login/oauth2/token
```

### 6.3 Token 存储安全要求

- 不要在网页中嵌入 Token
- 不要在 URL 中传递 Token 或 Session ID
- 安全地保护数据库或 Token 存储
- Web 应用应防止 XSS、CSRF、重放攻击
- 原生应用应使用系统 Keychain 安全存储

### 6.4 手动生成 Token（仅限测试）

路径：用户头像 → Profile → Approved Integrations → 生成新 Access Token

> ⚠️ **警告：** 要求其他用户手动生成 Token 并输入应用是违反 API 政策的行为。多用户应用必须使用 OAuth 流程。

### 6.5 LTI Advantage 服务认证 (Client Credentials Grant)

用于 Names and Roles Provisioning Service、Assignment and Grades Service 等 LTI 服务。

#### 步骤 1：配置 Developer Key

- 创建 LTI Developer Key
- 配置 Public JWK（静态或动态 URL）
- JWK 必须包含 `alg` 和 `use` 字段

**示例 JWK：**

```json
{
  "public_jwk": {
    "kty": "RSA",
    "alg": "RS256",
    "e": "AQAB",
    "kid": "8f796179-7ac4-48a3-a202-fc4f3d814fcd",
    "n": "nZA7QWcIwj-3N_RZ1q...",
    "use": "sig"
  }
}
```

#### 步骤 2：请求 Access Token

使用 RSA256 私钥签名的 `client_credentials` grant 请求。

#### 步骤 3：调用 LTI 服务

```bash
curl -H "Authorization: Bearer <ACCESS-TOKEN>" \
  "https://<canvas_domain>/api/lti/courses/:course_id/names_and_roles"
```

#### 支持的 LTI 端点

| 服务 | 端点 |
|------|------|
| Names and Role Provisioning | 用户名单与角色 API |
| Line Items | 成绩条目管理 |
| Score | 成绩发布 |
| Result | 成绩结果查询 |

### 6.6 各服务认证方式汇总

| 服务 | 认证方式 | 文档链接 |
|------|---------|----------|
| Canvas LMS API | OAuth2 / Developer Keys | `/services/canvas/oauth2/` |
| Canvas LTI Advantage | OAuth2 Client Credentials + JWT | `/services/canvas/oauth2/file.oauth` |
| Data Access Platform | JWT Access Token | `/services/dap/query-api/oauth_login` |
| Elevate Standards Alignment | API Key | `/services/ab-connect/introduction/authentication` |
| Parchment Digital Badges | Password-based / Authorization Code | `/services/parchment-digital-badges/authentication` |

---

## 7. LTI (学习工具互操作性)

> 来源：[https://developerdocs.instructure.com/services/canvas/external-tools/lti](https://developerdocs.instructure.com/services/canvas/external-tools/lti)

### 7.1 LTI 文档结构

```
External Tools
├── LTI
│   ├── Introduction (工具介绍)
│   ├── Registration (注册流程)
│   ├── Launch Overview (启动概览)
│   ├── Configuring (开发者密钥配置)
│   ├── Variable Substitutions (变量替换)
│   ├── Deep Linking (深度链接)
│   ├── Grading (评分集成)
│   ├── Provisioning (用户配置)
│   ├── PostMessage (窗口通信)
│   ├── Platform Notification Service (平台通知)
│   ├── Legacy 1.1 Configuration (遗留 1.1 配置)
│   └── Placements (布局位置)
│       ├── Navigation (导航)
│       ├── Homework Submission (作业提交)
│       ├── Editor Button (编辑器按钮)
│       ├── Migration Selection (迁移选择)
│       ├── Link Selection / Modules (模块链接)
│       ├── Assignment Selection (作业选择)
│       └── Collaborations (协作)
├── xAPI
├── Canvas Roles
└── Plagiarism Detection Platform (抄袭检测)
    ├── Assignments / Users / Submissions
    ├── Webhooks Subscriptions
    └── JWT Access Tokens
```

### 7.2 关键外部 LTI 规范链接

| 规范 | 链接 |
|------|------|
| LTI v1.3 Specification | [https://www.imsglobal.org/spec/lti/v1p3/](https://www.imsglobal.org/spec/lti/v1p3/) |
| 1EdTech Security Framework | [https://www.imsglobal.org/spec/security/v1p0/](https://www.imsglobal.org/spec/security/v1p0/) |
| Deep Linking | [https://www.imsglobal.org/spec/lti-dl/v2p0](https://www.imsglobal.org/spec/lti-dl/v2p0) |
| Names and Roles Provisioning | [https://www.imsglobal.org/spec/lti-nrps/v2p0](https://www.imsglobal.org/spec/lti-nrps/v2p0) |
| Assignment and Grades Service | [https://www.imsglobal.org/spec/lti-ags/v2p0/](https://www.imsglobal.org/spec/lti-ags/v2p0/) |
| LTI Advantage Implementation Guide | [https://www.imsglobal.org/spec/lti/v1p3/impl/](https://www.imsglobal.org/spec/lti/v1p3/impl/) |
| LTI Migration Guide | [https://www.imsglobal.org/spec/lti/v1p3/migr](https://www.imsglobal.org/spec/lti/v1p3/migr) |
| LTI Boot Camp Resources | [https://github.com/imsglobal/ltibootcamp](https://github.com/imsglobal/ltibootcamp) |

---

## 8. Data Access Platform (DAP)

> 来源：[https://developerdocs.instructure.com/services/dap](https://developerdocs.instructure.com/services/dap)

### 8.1 概述

DAP 是 Instructure 的集中式数据仓库，提供跨产品的分析数据访问。支持三种访问方式：

| 访问方式 | 描述 |
|---------|------|
| **Query API** | REST API，支持 JWT Token 认证 |
| **DAP CLI** | 命令行工具，支持 Snapshot、Incremental、Schema 等操作 |
| **Client Library** | 代码内直接访问 (SDK) |

### 8.2 数据命名空间 (Namespaces)

| Namespace | 描述 |
|-----------|------|
| `canvas` | Canvas LMS 核心数据表 |
| `canvas_logs` | Canvas 日志数据 |
| `catalog` | Catalog 产品数据 |
| `new_quizzes` | 新版测验数据（含 Classic Quizzes Schema Crosswalk） |

### 8.3 DAP CLI 命令参考

| 命令 | 功能 |
|------|------|
| `dap snapshot` | 下载表的完整快照 |
| `dap incremental` | 下载指定时间范围内的表变更 |
| `dap list` | 列出命名空间中所有可用表 |
| `dap schema` | 下载表结构定义 |
| `dap initdb` | 将表快照导入数据库 |
| `dap syncdb` | 同步表数据变更到数据库 |
| `dap dropdb` | 删除数据库中已同步的表 |
| `dap listdb` | 列出本地数据库中的表信息 |
| `dap env vars` | 配置 DAP CLI 认证环境变量 |

---

## 9. 其他服务

### 9.1 Catalog API

课程目录与注册管理，包含 API：`Account Admins`, `Analytics`, `Bulk Enrollments`, `Catalogs`, `Certificates`, `Courses`, `Enrollments`, `Orders`, `Programs`, `Progresses`, `Tags`, `Users`, `Waitlist Applicants`

### 9.2 Commons API

学习资源共享平台，包含 API：`Account`, `Consortiums`, `Courses`, `Groups`, `Licenses`, `Media`, `Outcomes`, `Resources`, `Reviews`, `Session`, `Users`

### 9.3 Studio API

视频学习平台，包含 API：`Captions`, `Collection`, `Courses`, `Group`, `Insights`, `Media`, `Media Upload`, `Professional Captioning`, `Tags`, `Transfer Media`, `User`

### 9.4 New Quizzes API

新一代测验引擎 LTI 公共端点：`Dsr Requests`, `Impact`, `Mobile Verify`, `Quiz Accommodations`, `Quiz Items`, `Quiz Reports`, `Sftp Users`, `Sis Post Grades`, `Unified Tool Id`

### 9.5 Parchment Digital Badges API

数字徽章管理：`Assertions`, `Backpack`, `Badgeclasses`, `Badgeconnect`, `Issuers`, `Organizations`, `Pathways`, `Recipientgroups`, `Users`

### 9.6 Elevate Standards Alignment (AB Connect)

课程标准对齐 API，支持：ODATA 过滤、排序、Facets、分页、调用限流、关联对象查询、嵌入式 Widgets

### 9.7 Data Sync API

教育数据互操作标准，包含：`Interop API`, `Interop Data API`, `Grades Exchange API`, `OneRoster API`, `Platform API`

---

## 10. LLM 集成

门户为 AI/LLM 提供了便捷的文档访问入口：

| 资源 | URL | 用途 |
|------|-----|------|
| **llms.txt** | `https://developerdocs.instructure.com/llms.txt` | 完整文档索引（Markdown 格式），含所有页面链接 |
| **llms-full.txt** | `https://developerdocs.instructure.com/llms-full.txt` | 全量文档内容，适合 LLM 上下文注入 |
| **AI 动态查询** | `GET /readme.md?ask=<问题>` | 自然语言提问，返回答案和相关文档片段 |

### 使用示例

```bash
# 通过 AI 查询接口检索文档
curl "https://developerdocs.instructure.com/readme.md?ask=How+do+I+authenticate+Canvas+API+calls%3F"
```

---

## 11. 开发者工具与最佳实践

### 11.1 推荐的开发工具

| 工具 | 用途 |
|------|------|
| **Postman** | API 测试与调用 |
| **Swagger Editor / UI** | OpenAPI 3.0 规范可视化与交互 |
| **OpenAPI Generator** | 从 OpenAPI 规范自动生成客户端代码 |
| **JSONView (浏览器扩展)** | JSON 响应格式化查看 |
| **DAP CLI** | 命令行数据访问与同步 |

### 11.2 API 最佳实践

1. **始终使用 HTTPS** — HTTP 请求会被重定向，但凭据已在明文中暴露
2. **使用 Authorization Header** — 优先使用 `Authorization: Bearer <token>` 而非 Query String 传 Token
3. **处理 401 Unauthorized** — 检查 `WWW-Authenticate` Header 区分 Token 过期和权限不足
4. **安全存储 Token** — Token 等同于密码，必须安全存储
5. **处理分页** — 检查 Response 的 `Link` Header 获取下一页 URL
6. **大整数处理** — JavaScript 中使用 `Accept: application/json+canvas-string-ids` Header 将 ID 转为字符串
7. **限流处理** — Canvas API 有调用频率限制，详见 [Throttling 文档](https://developerdocs.instructure.com/services/canvas/basics/file.throttling)
8. **关注 API 变更日志** — 定期查看 [API Change Log](https://developerdocs.instructure.com/services/canvas/basics/file.changelog) 了解新增、变更、弃用和移除

### 11.3 本地文档生成

如果你搭建了本地 Canvas 环境：

```bash
# 生成 REST API 文档
bundle exec rake doc:api

# 生成 OpenAPI 3.0 规范
bundle exec rake doc:openapi
```

---

## 附录 A: 重要链接汇总

| 资源 | URL |
|------|-----|
| 开发者文档门户 | https://developerdocs.instructure.com/ |
| Canvas 社区 | https://community.canvaslms.com/ |
| Canvas LMS GitHub | https://github.com/instructure/canvas-lms |
| API 变更日志 | https://developerdocs.instructure.com/services/canvas/basics/file.changelog |
| OAuth2 概述 | https://developerdocs.instructure.com/services/canvas/oauth2/file.oauth |
| Developer Keys | https://developerdocs.instructure.com/services/canvas/oauth2/file.developer_keys |
| LTI 文档 | https://developerdocs.instructure.com/services/canvas/external-tools/lti/file.tools_intro |
| DAP 文档 | https://developerdocs.instructure.com/services/dap |
| 权限参考 | https://developerdocs.instructure.com/services/canvas/permissions/file.permissions |
| 分页文档 | https://developerdocs.instructure.com/services/canvas/basics/file.pagination |
| 限流文档 | https://developerdocs.instructure.com/services/canvas/basics/file.throttling |
| SIS CSV 格式 | https://developerdocs.instructure.com/services/canvas/sis/file.sis_csv |
| Instructure UI | https://developerdocs.instructure.com/services/instui |

## 附录 B: 截图

- 首页截图: `instructure_homepage.png`
- Get Started 页面截图: `instructure_get_started.png`
- Services 页面截图: `instructure_services.png`

---

> **文档生成日期:** 2026-06-22
> **文档版本:** 1.0
> **基于:** Instructure Developer Documentation Portal (`developerdocs.instructure.com`)
