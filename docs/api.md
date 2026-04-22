# Alarm Service API 文档

> 基础地址：`http://{host}:{port}`
>
> - QAS 环境：`10.126.1.128:17650`
> - PRD 环境：`10.126.1.237:17651`

## 统一响应格式

所有接口返回以下 JSON 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | string | 状态码。`S10000` 表示成功，`F10001` 表示失败 |
| `msg` | string | 描述信息。失败时会附带指导文档链接 |
| `content` | dict / list | 返回数据，具体结构因接口而异 |

成功响应示例：

```json
{
  "code": "S10000",
  "msg": "OK",
  "content": {}
}
```

失败响应示例：

```json
{
  "code": "F10001",
  "msg": "Error，詳情請參考：http://10.126.1.128:17650/static/files/alarm_server服務指導文檔.pdf",
  "content": {}
}
```

---

## 1. 登录

### `POST /api/login`

通过 LDAP 认证，获取 JWT Token。后续需要认证的接口（目前仅注册服务）需在 Header 中携带此 Token。

**Content-Type：** `application/json`

#### 请求参数

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `work_no` | string | 是 | 工号 | 长度 1~32 |
| `password` | string | 是 | 密码 | 不能为空 |
| `location` | string | 是 | 园区 | 必须为以下之一：`鹏鼎园区`、`礼鼎园区`、`大园园区`、`先丰园区`、`印度园区`（或对应繁体） |

#### 请求示例

```json
{
  "work_no": "A12345",
  "password": "mypassword",
  "location": "鹏鼎园区"
}
```

#### 成功响应

```json
{
  "code": "S10000",
  "msg": "OK",
  "content": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

---

## 2. 服务注册

### `POST /api/registrate`

注册一个服务，获取用于调用告警接口的 `service_name` + `service_type` + `token` 三元组。

**Content-Type：** `application/json`

**认证：** 需要在 Header 中携带 JWT Token：`Authorization: Bearer <token>`

#### 请求参数

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `service_name` | string | 是 | 服务名称，用于标识调用方 | 不能为空，最大 30 字符，不能包含特殊字符（如 `@/*&%$#` 等） |
| `service_type` | string | 是 | 服务类型 | 必须为 `RPA` 或 `Web` |

#### 请求示例

```json
{
  "service_name": "MES告警服务",
  "service_type": "Web"
}
```

#### 成功响应

```json
{
  "code": "S10000",
  "msg": "OK",
  "content": {
    "service_name": "MES告警服务",
    "service_type": "Web",
    "work_no": "A12345",
    "token": "a1b2c3d4e5f6...",
    "service_host": "10.126.1.100"
  }
}
```

#### 失败响应（服务已注册）

```json
{
  "code": "F10001",
  "msg": "該服務名已經註冊...",
  "content": {
    "token": "a1b2c3d4e5f6..."
  }
}
```

---

### `GET /api/registrate`

查询当前用户已注册的所有服务。

**认证：** 需要 JWT Token

#### 成功响应

```json
{
  "code": "S10000",
  "msg": "OK",
  "content": [
    {
      "service_name": "MES告警服务",
      "service_type": "Web",
      "service_host": "10.126.1.100",
      "token": "a1b2c3d4e5f6...",
      "created_at": "2024-01-15 10:30:00"
    }
  ]
}
```

---

## 3. 发送钉钉群消息

### `POST /api/sendGroupAlarmMsg`

通过 Webhook 向钉钉群发送消息，支持 text、link、markdown 三种类型。

**Content-Type：** `application/json`

#### 公共参数

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `webhook` | string | 是 | 钉钉群机器人 Webhook 地址 | 必须以 `http://10.182.179.113:8081/` 开头 |
| `type` | string | 是 | 消息类型 | `text`、`link`、`markdown` 三选一 |
| `same_alarm_inter` | integer | 是 | 去重间隔（分钟），在该时间内相同内容不重复发送 | 正整数 |
| `service_name` | string | 是 | 注册时获取的服务名称 | — |
| `service_type` | string | 是 | 注册时获取的服务类型 | `RPA` 或 `Web` |
| `token` | string | 是 | 注册时获取的 token | — |

#### 3.1 type = "text"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `text.content` | string | 是 | 消息正文 | 不能为空，最大 1300 字符，最多 30 行 |
| `text.isatall` | boolean | 否 | 是否 @所有人 | 默认 `false` |
| `text.atuserids` | string[] | 否 | 需要 @的用户工号列表 | 用户必须存在于系统中 |

```json
{
  "webhook": "http://10.182.179.113:8081/robot/send?access_token=xxx",
  "type": "text",
  "same_alarm_inter": 5,
  "service_name": "MES告警服务",
  "service_type": "Web",
  "token": "a1b2c3d4e5f6...",
  "text": {
    "content": "【告警】MES 服务异常，请及时处理",
    "isatall": false,
    "atuserids": ["A12345", "B67890"]
  }
}
```

#### 3.2 type = "link"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `link.message_url` | string | 是 | 点击消息后跳转的链接 | 必须以 `http` 开头 |
| `link.title` | string | 是 | 消息标题 | 不能为空 |
| `link.text` | string | 是 | 消息摘要 | 不能为空 |

```json
{
  "webhook": "http://10.182.179.113:8081/robot/send?access_token=xxx",
  "type": "link",
  "same_alarm_inter": 5,
  "service_name": "MES告警服务",
  "service_type": "Web",
  "token": "a1b2c3d4e5f6...",
  "link": {
    "message_url": "http://example.com/detail/123",
    "title": "MES 生产异常通知",
    "text": "A1 产线温度超标，当前温度 85°C，阈值 80°C"
  }
}
```

#### 3.3 type = "markdown"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `markdown.title` | string | 是 | 消息标题（仅在通知栏显示） | 不能为空 |
| `markdown.text` | string | 是 | Markdown 格式正文 | 不能为空 |
| `markdown.atuserids` | object | 否 | @用户配置，不传则不 @任何人 | — |
| `markdown.atuserids.at` | string[] | 否 | 需要 @的用户工号列表 | 用户必须存在于系统中 |
| `markdown.atuserids.cc` | string[] | 否 | 抄送用户工号列表 | 用户必须存在于系统中 |
| `markdown.atuserids.after_at_msg` | string | 否 | 跟在 @用户后面的附加文本 | — |

```json
{
  "webhook": "http://10.182.179.113:8081/robot/send?access_token=xxx",
  "type": "markdown",
  "same_alarm_inter": 10,
  "service_name": "MES告警服务",
  "service_type": "Web",
  "token": "a1b2c3d4e5f6...",
  "markdown": {
    "title": "生产异常告警",
    "text": "### 生产异常告警\n- **产线：** A1\n- **温度：** 85°C\n- **阈值：** 80°C",
    "atuserids": {
      "at": ["A12345"],
      "cc": ["B67890"],
      "after_at_msg": "请尽快处理"
    }
  }
}
```

#### 成功响应

```json
{
  "code": "S10000",
  "msg": "OK",
  "content": {}
}
```

#### 去重拦截响应

```json
{
  "code": "F10001",
  "msg": "Error...",
  "content": {
    "errmsg": {
      "err_msg": "5分鐘內禁止發送相同數據"
    }
  }
}
```

---

## 4. 发送钉钉群文件/消息（openConversationId）

### `POST /api/sendGroupAlarmFile`

通过 openConversationId 向钉钉群发送文件、图片或消息。与 `/api/sendGroupAlarmMsg` 的区别是使用 `groupid`（openConversationId）而非 Webhook。

**Content-Type：** `multipart/form-data`

#### 公共参数

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `groupid` | string | 是 | 钉钉群的 openConversationId | 不能为空 |
| `type` | string | 是 | 消息类型 | `text`、`link`、`markdown`、`image`、`file` 五选一 |
| `same_alarm_inter` | integer | 是 | 去重间隔（分钟） | 正整数 |
| `service_name` | string | 是 | 注册时获取的服务名称 | — |
| `service_type` | string | 是 | 注册时获取的服务类型 | `RPA` 或 `Web` |
| `token` | string | 是 | 注册时获取的 token | — |

#### 4.1 type = "text"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `text` | string | 是 | JSON 字符串，包含 `content` 字段 | `content` 不能为空，最大 1300 字符，最多 30 行 |

```
POST /api/sendGroupAlarmFile
Content-Type: multipart/form-data

groupid: cidXXXXXXXXXXXXXXX
type: text
same_alarm_inter: 5
service_name: MES告警服务
service_type: Web
token: a1b2c3d4e5f6...
text: {"content": "【告警】MES 服务异常，请及时处理"}
```

#### 4.2 type = "markdown"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `markdown` | string | 是 | JSON 字符串，需包含 `title` 和 `text` 字段 | 两个字段均不能为空 |

```
markdown: {"title": "生产告警", "text": "### 温度超标\n- 产线 A1\n- 温度 85°C"}
```

#### 4.3 type = "link"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `link` | string | 是 | JSON 字符串，需包含 `title`、`text`、`url` 字段 | 三个字段均不能为空 |

```
link: {"title": "异常详情", "text": "A1 产线温度超标", "url": "http://example.com/detail/123"}
```

#### 4.4 type = "image"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `image` | file | 是 | 图片文件（通过 form-data 上传） | 不能为空 |

#### 4.5 type = "file"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `file` | file | 是 | 文件（通过 form-data 上传） | 不能为空 |

#### 成功响应

```json
{
  "code": "S10000",
  "msg": "OK",
  "content": {
    "status": "ok",
    "processQueryKey": "abc123def456"
  }
}
```

---

## 5. 发送钉钉个人消息

### `POST /api/sendSingleAlarm`

向指定用户发送钉钉个人消息，支持 text、markdown、link、image、file 五种类型。

**Content-Type：** `multipart/form-data`

#### 公共参数

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `userids` | string[] | 是 | 接收消息的用户工号列表 | 用户必须存在于系统中 |
| `type` | string | 是 | 消息类型 | `text`、`markdown`、`link`、`image`、`file` 五选一 |
| `same_alarm_inter` | integer | 是 | 去重间隔（分钟） | 正整数 |
| `service_name` | string | 是 | 注册时获取的服务名称 | — |
| `service_type` | string | 是 | 注册时获取的服务类型 | `RPA` 或 `Web` |
| `token` | string | 是 | 注册时获取的 token | — |

#### 5.1 type = "text"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `text` | string | 是 | JSON 字符串，包含 `content` 字段 | `content` 不能为空，最大 1300 字符，最多 30 行 |

```
POST /api/sendSingleAlarm
Content-Type: multipart/form-data

userids: ["A12345", "B67890"]
type: text
same_alarm_inter: 5
service_name: MES告警服务
service_type: Web
token: a1b2c3d4e5f6...
text: {"content": "您好，MES 服务出现异常，请及时查看"}
```

#### 5.2 type = "markdown"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `markdown` | string | 是 | JSON 字符串，需包含 `title` 和 `text` 字段 | 两个字段均不能为空 |

```
markdown: {"title": "告警通知", "text": "### 温度超标\n当前温度 85°C"}
```

#### 5.3 type = "link"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `link` | string | 是 | JSON 字符串，需包含 `title`、`text`、`url` 字段 | 三个字段均不能为空 |

```
link: {"title": "异常详情", "text": "A1 产线温度超标", "url": "http://example.com/detail/123"}
```

#### 5.4 type = "image"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `image` | file | 是 | 图片文件（通过 form-data 上传） | 不能为空 |

#### 5.5 type = "file"

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `file` | file | 是 | 文件（通过 form-data 上传） | 不能为空 |

#### 成功响应

```json
{
  "code": "S10000",
  "msg": "OK",
  "content": {
    "status": "ok",
    "processQueryKey": "abc123def456"
  }
}
```

#### 部分用户不存在的响应

```json
{
  "code": "S10000",
  "msg": "OK",
  "content": {
    "status": "ok, but ['C99999'] nonexistent.",
    "processQueryKey": "abc123def456"
  }
}
```

---

## 6. 发送邮件告警

### `POST /api/sendAlarmMail`

通过 SOAP 邮件服务发送告警邮件。

**Content-Type：** `application/json`

#### 请求参数

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `mail_type` | string | 是 | 邮件服务类型，决定使用哪个邮件网关 | `zheng`（正鼎/eip109）或 `peng`（鹏鼎/eip03） |
| `send_to` | string[] | 是 | 收件人邮箱列表 | 每个邮箱必须包含 `.` 字符 |
| `title` | string | 是 | 邮件主题 | 不能为空 |
| `content` | string | 是 | 邮件正文（支持 HTML） | 不能为空 |
| `same_alarm_inter` | integer | 是 | 去重间隔（分钟） | 正整数 |
| `service_name` | string | 是 | 注册时获取的服务名称 | — |
| `service_type` | string | 是 | 注册时获取的服务类型 | `RPA` 或 `Web` |
| `token` | string | 是 | 注册时获取的 token | — |

#### 请求示例

```json
{
  "mail_type": "zheng",
  "send_to": ["zhangsan@example.com", "lisi@example.com"],
  "title": "【告警】MES 服务异常通知",
  "content": "<h3>告警详情</h3><p>A1 产线温度超标，当前 85°C，阈值 80°C</p>",
  "same_alarm_inter": 30,
  "service_name": "MES告警服务",
  "service_type": "Web",
  "token": "a1b2c3d4e5f6..."
}
```

#### 成功响应

```json
{
  "code": "S10000",
  "msg": "OK",
  "content": {}
}
```

---

## 7. 查询消息送达状态

### `GET /api/ReadStatus`

查询已发送的钉钉消息的送达状态（通过 `processQueryKey` 查询）。

**Content-Type：** `application/json`

#### 请求参数

| 字段 | 类型 | 必填 | 说明 | 约束 |
|------|------|------|------|------|
| `type` | string | 是 | 查询类型 | `single`（个人消息）或 `group`（群消息） |
| `single` | object | 条件必填 | 当 `type` = `single` 时必须提供 | — |
| `single.processQueryKey` | string | 是 | 发送消息时返回的查询 key | 不能为空 |
| `group` | object | 条件必填 | 当 `type` = `group` 时必须提供 | — |
| `group.groupid` | string | 是 | 钉钉群的 openConversationId | — |
| `group.processQueryKey` | string | 是 | 发送消息时返回的查询 key | 不能为空 |

#### 查询个人消息状态示例

```json
{
  "type": "single",
  "single": {
    "processQueryKey": "abc123def456"
  }
}
```

#### 查询群消息状态示例

```json
{
  "type": "group",
  "group": {
    "groupid": "cidXXXXXXXXXXXXXXX",
    "processQueryKey": "abc123def456"
  }
}
```

#### 成功响应

```json
{
  "code": "S10000",
  "msg": "OK",
  "content": {
    "errmsg": {
      "sendStatus": "RECALLED",
      "readUserIds": ["A12345"]
    }
  }
}
```

---

## 8. 健康检查

### `GET /monitor_verification_api`

服务健康检查接口，供内部监控系统使用。

#### 成功响应

```json
{
  "code": 200
}
```

---

## 附录

### A. 服务认证说明

除登录（`/api/login`）、注册（`/api/registrate`）和健康检查（`/monitor_verification_api`）外，所有告警发送接口都需要携带以下三个认证字段：

| 字段 | 说明 |
|------|------|
| `service_name` | 通过 `/api/registrate` 注册时填写的服务名称 |
| `service_type` | 通过 `/api/registrate` 注册时选择的服务类型（`RPA` 或 `Web`） |
| `token` | 注册成功后返回的 SHA256 token |

如果认证失败，返回：

```json
{
  "code": "F10001",
  "msg": "服務還沒有進行註冊，無法發送消息...",
  "content": {}
}
```

### B. 去重机制说明

所有告警发送接口都支持 `same_alarm_inter`（去重间隔）参数：

- 系统会根据 **调用方 IP + 通知方式 + 消息内容 + @用户 + webhook/groupid + 消息类型** 进行去重
- 在 `same_alarm_inter` 分钟内，完全相同的消息不会重复发送
- 文件/图片类型通过 SHA256 哈希值进行内容去重
- 设置为 `0` 可禁用去重（每次都发送）

### C. 接口调用流程

```
1. POST /api/login          → 获取 JWT Token
2. POST /api/registrate     → 注册服务，获取 service_name + service_type + token
3. POST /api/sendGroupAlarmMsg   ┐
   POST /api/sendGroupAlarmFile  │
   POST /api/sendSingleAlarm    ├→ 使用 token 三元组发送告警
   POST /api/sendAlarmMail      ┘
4. GET  /api/ReadStatus      → 查询消息送达状态（可选）
```
