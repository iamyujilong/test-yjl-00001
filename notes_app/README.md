# 个人笔记管理系统

一个基于 Flask + SQLite + HTML/CSS/JavaScript 构建的个人笔记管理系统，支持笔记管理、分类管理、标签管理、收藏、归档、搜索筛选、评论点赞等功能。

## 技术栈

- **后端**: Python Flask 2.3.3
- **数据库**: SQLite（零配置，单文件存储）
- **前端**: HTML5 + CSS3 + JavaScript (ES6+)
- **图标**: Font Awesome 6.4.0

## 功能特性

### 笔记管理
- 创建、编辑、删除笔记
- 支持富文本内容输入
- 自动保存更新时间

### 分类管理
- 自定义分类名称
- 支持颜色标识（可视化区分）
- 默认分类：默认、工作、生活、学习、灵感

### 标签管理
- 为笔记添加多个标签
- 支持按标签筛选笔记
- 自动创建新标签
- 标签管理弹窗：添加、删除自定义标签
- 笔记默认关联"全部"标签

### 收藏功能
- 标记重要笔记为收藏
- 黄色高亮标识收藏笔记
- 支持仅查看收藏笔记

### 归档功能
- 归档不常用的笔记
- 归档笔记显示为灰色
- 默认隐藏归档笔记，可切换显示

### 搜索功能
- 按标题搜索笔记
- 按内容搜索笔记
- 实时搜索结果更新

### 筛选功能
- 按分类筛选笔记
- 按标签筛选笔记
- 组合筛选条件

### 响应式设计
- 适配桌面端和移动端
- 网格视图/列表视图切换

### 评论系统
- 匿名评论功能
- 显示评论时间、IP属地
- 支持回复评论
- 评论列表按热度/时间排序
- 每日评论上限：2条/用户

### 点赞系统
- 笔记点赞/取消点赞
- 评论点赞/取消点赞
- 同一用户对同一笔记/评论只能点赞1次
- 实时显示点赞数

## 项目结构

```
notes_app/
├── backend/
│   └── app.py              # Flask 后端应用
├── database/
│   ├── init_db.py          # 数据库初始化脚本
│   └── notes.db            # SQLite 数据库文件（自动生成）
├── frontend/
│   ├── index.html          # 主页面
│   ├── styles.css          # 样式文件
│   └── app.js              # 前端逻辑
├── requirements.txt        # Python 依赖
└── README.md               # 项目说明
```

## 安装与运行

### 环境要求

- Python 3.7+

### 安装步骤

1. 进入项目目录：

```bash
cd notes_app
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 运行应用：

```bash
python backend/app.py
```

4. 访问应用：

打开浏览器访问 http://localhost:5000

## API 接口

### 笔记接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/notes` | 获取笔记列表（支持搜索、筛选） |
| GET | `/api/notes/:id` | 获取单个笔记详情 |
| POST | `/api/notes` | 创建新笔记 |
| PUT | `/api/notes/:id` | 更新笔记 |
| DELETE | `/api/notes/:id` | 删除笔记 |
| POST | `/api/notes/:id/like` | 点赞/取消点赞笔记 |
| GET | `/api/notes/:id/like/status` | 获取笔记点赞状态 |
| POST | `/api/notes/:id/comments` | 发表评论 |
| GET | `/api/notes/:id/comments` | 获取评论列表 |

### 分类接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/categories` | 获取所有分类 |
| POST | `/api/categories` | 创建新分类 |
| PUT | `/api/categories/:id` | 更新分类 |
| DELETE | `/api/categories/:id` | 删除分类 |

### 标签接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tags` | 获取所有标签 |
| POST | `/api/tags` | 创建新标签 |
| DELETE | `/api/tags/:id` | 删除标签 |

### 评论接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/comments/:id/like` | 点赞/取消点赞评论 |

## 使用说明

### 创建笔记

1. 点击右上角「新建笔记」按钮
2. 填写标题、内容
3. 选择分类（可选）
4. 输入标签，用逗号分隔（可选）
5. 勾选「设为收藏」（可选）
6. 点击「保存」

### 编辑笔记

1. 点击笔记卡片进入编辑页面
2. 修改内容后点击「保存」

### 收藏笔记

- 点击笔记卡片右上角的星形图标

### 归档笔记

- 点击笔记卡片右上角的归档图标

### 删除笔记

- 点击笔记卡片右上角的垃圾桶图标
- 确认后删除

### 搜索笔记

- 在左侧搜索框输入关键词
- 实时显示匹配结果

### 筛选笔记

- 选择左侧分类或标签进行筛选
- 使用「显示归档」和「仅收藏」复选框

### 管理分类

1. 点击「分类管理」按钮
2. 添加新分类（输入名称和颜色）
3. 编辑或删除现有分类

### 管理标签

1. 点击「标签管理」按钮
2. 添加新标签（输入名称）
3. 删除现有标签

### 查看笔记详情

1. 点击笔记卡片的评论图标或直接点击卡片
2. 在详情页查看完整内容
3. 查看点赞数和评论数

### 发表评论

1. 打开笔记详情
2. 在评论输入框输入内容
3. 点击「发表」按钮
4. 每日限制2条评论

### 回复评论

1. 在评论列表中点击「回复」按钮
2. 输入回复内容
3. 点击「发表」按钮

### 点赞笔记

1. 在笔记卡片或详情页点击心形图标
2. 再次点击可取消点赞

### 点赞评论

1. 在评论下方点击点赞图标
2. 再次点击可取消点赞

### 评论排序

- 在笔记详情页切换「最新」或「最热」排序

## 数据库表结构

### categories 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| name | TEXT | 分类名称（唯一） |
| color | TEXT | 颜色标识 |
| created_at | TIMESTAMP | 创建时间 |

### tags 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| name | TEXT | 标签名称（唯一） |
| created_at | TIMESTAMP | 创建时间 |

### notes 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| title | TEXT | 笔记标题 |
| content | TEXT | 笔记内容 |
| category_id | INTEGER | 分类ID（外键） |
| is_favorite | INTEGER | 是否收藏（0/1） |
| is_archived | INTEGER | 是否归档（0/1） |
| like_count | INTEGER | 点赞数 |
| comment_count | INTEGER | 评论数 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### note_tags 表

| 字段 | 类型 | 说明 |
|------|------|------|
| note_id | INTEGER | 笔记ID（外键） |
| tag_id | INTEGER | 标签ID（外键） |

### anonymous_users 表

| 字段 | 类型 | 说明 |
|------|------|------|
| token | TEXT | 主键，匿名用户标识 |
| ip_address | TEXT | IP地址 |
| ip_location | TEXT | IP属地 |
| created_at | TIMESTAMP | 创建时间 |

### comments 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| note_id | INTEGER | 笔记ID（外键） |
| parent_id | INTEGER | 父评论ID（外键） |
| token | TEXT | 匿名用户标识（外键） |
| ip_location | TEXT | IP属地 |
| content | TEXT | 评论内容 |
| like_count | INTEGER | 点赞数 |
| created_at | TIMESTAMP | 创建时间 |

### note_likes 表

| 字段 | 类型 | 说明 |
|------|------|------|
| note_id | INTEGER | 笔记ID（外键） |
| token | TEXT | 匿名用户标识（外键） |
| created_at | TIMESTAMP | 创建时间 |

### comment_likes 表

| 字段 | 类型 | 说明 |
|------|------|------|
| comment_id | INTEGER | 评论ID（外键） |
| token | TEXT | 匿名用户标识（外键） |
| created_at | TIMESTAMP | 创建时间 |

## 开发说明

### 数据库初始化

首次运行时，应用会自动创建数据库文件并初始化默认分类和"全部"标签。

### 数据备份

SQLite 数据库文件位于 `database/notes.db`，定期备份此文件即可备份所有数据。

### 安全注意事项

- 本系统为本地单机应用，不包含用户认证功能
- 请勿在公共网络环境中直接部署
- 建议定期备份数据库文件

### 匿名用户机制

- 系统通过匿名token（UUID）识别用户
- token存储在浏览器cookie中，有效期30天
- IP地址用于计算IP属地（本地地址显示"本地"，其他显示"未知"）
- 每日评论限制基于token和日期判断

## 许可证

MIT License