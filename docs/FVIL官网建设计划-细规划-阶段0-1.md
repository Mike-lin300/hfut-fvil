# FVIL 官网建设 · 细规划（阶段0 + 阶段1）

> 文档版本：v1.1（§5 招新草案按负责人确认更新；§5.4 新增数据库选型评估）
> 适用范围：**阶段0（地基）+ 阶段1（官网门面）**，以及阶段2（招新数据库）核心数据模型草案（提前确认用）
> 执行方式：照本文件逐条执行即可开工，无需再确认；本文件是"动作清单"，不做选择题
> 前置条件：`docs\FVIL官网建设计划.md`（v1.0）决策已确认

---

## 1. 环境基线（2026-09-26 实查）

| 项目 | 实测值 | 说明 |
|---|---|---|
| Python | **3.10.0** @ `D:\Program Files\Python310\python.exe` | Django 5.2 要求 3.10+，满足 |
| Django 5.2 | `D:\ProjectGroup\lDjango\dss01\.venv`（Python 3.10.0） | 已有环境**只作参考**，官网项目新建独立 venv |
| MySQL | **5.7.21**，服务名 `MySQL57`，运行中 | 开发可用；生产用 8.0 |
| 虚拟环境方案 | 基于 Python310 新建 `.venv`（在 `D:\HFUT\fvil` 内） | 与 lDjango 环境隔离 |

## 2. 已确认决策摘要（影响本细规划的关键项）

- 部署：阿里云（暂无域名）→ **配置与代码分离**（.env）从阶段0做起；
- 认证：**不做新生注册**；仅管理组账号；人员以姓名+学号标识；
- 招新：约200人/年、留10人；管理权限学生≤20人；
- 作业：仅 zip 压缩包、人工批改（阶段3才做）；
- 资料库：保留 fvil-ec-guide 原模式（阶段3才涉及，此处不展开）；
- 视觉：实验室蓝 `#1f6feb`，仅中文。

---

## 3. 阶段0：地基（预计 0.5~1 天）

### 3.1 目标项目结构（本阶段建出）

```
D:\HFUT\fvil\
├─ manage.py
├─ config/                  # 项目配置（settings/urls/asgi/wsgi）
├─ core/                    # 主页 app
├─ lab/                     # 实验室介绍 app
├─ templates/               # 全局模板（base.html 等）
├─ static/                  # 静态资源（css/js/img，Bootstrap 放这里）
├─ media/                   # 用户上传文件（gitignore）
├─ .venv/                   # 虚拟环境（gitignore）
├─ .env                     # 环境变量（gitignore）
├─ requirements.txt
├─ .gitignore
└─ docs/                    # 规划文档（已存在）
```

### 3.2 任务清单（逐项执行）

| # | 任务 | 动作（命令） | 产物/结果 | 验证 |
|---|---|---|---|---|
| T0-1 | 创建虚拟环境 | 在 `D:\HFUT\fvil` 下：`& "D:\Program Files\Python310\python.exe" -m venv .venv` | `.venv\` | `.venv\Scripts\python.exe --version` 输出 3.10.0 |
| T0-2 | 安装依赖 | 激活后：`pip install django==5.2 pymysql python-dotenv`；再 `pip freeze > requirements.txt` | `requirements.txt` | `pip show django` 显示 5.2 |
| T0-3 | 创建项目骨架 | `django-admin startproject config .`（在 fvil 根目录）；`python manage.py startapp core`；`python manage.py startapp lab` | `config/ core/ lab/ manage.py` | 目录存在 |
| T0-4 | 创建数据库与专用账号 | 进 MySQL（见 §3.3 SQL） | `fvil` 库 + `fvil` 用户 | `SHOW DATABASES;` 可见 fvil |
| T0-5 | 配置 .env | 在项目根新建 `.env`（模板见 §3.4），`.gitignore` 加入 `.env` | `.env` | 不进入 git |
| T0-6 | 配置 settings.py | 见 §3.5 | `config/settings.py` | — |
| T0-7 | 配置 MySQL 驱动 | `config/__init__.py` 加 PyMySQL 兼容代码（见 §3.5） | — | — |
| T0-8 | 首次迁移 + 建表 | `python manage.py makemigrations`；`python manage.py migrate` | 数据表 | 命令无报错（即 MySQL 连接成功） |
| T0-9 | 创建管理员 | `python manage.py createsuperuser`（用户名建议：fv_admin） | 超级用户 | — |
| T0-10 | 基础模板与静态 | 建 `templates/base.html`（导航+页脚+实验室蓝）、`static/` 放 Bootstrap 5 本地文件（css/js） | 基础页面框架 | 见 §3.6 |
| T0-11 | Admin 汉化与标题 | settings 设中文；admin 站点标题改为"FVIL 飞行器创新实验室" | — | 后台打开可见 |
| T0-12 | git 初始化 | `git init`；写入 `.gitignore`（§3.7）；`git add -A && git commit -m "chore: 项目初始化（阶段0）"` | 首个 commit | `git log` 有记录 |
| T0-13 | 阶段0 验收 | 见 §3.8 | — | 全部通过 |

### 3.3 建库 SQL（在 MySQL 中执行）

```sql
CREATE DATABASE fvil DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'fvil'@'localhost' IDENTIFIED BY 'fv_admin_2026';   -- 密码可自定
GRANT ALL PRIVILEGES ON fvil.* TO 'fvil'@'localhost';
FLUSH PRIVILEGES;
```

> 入口：`"D:\Program Files\MySQL\install\bin\mysql.exe" -uroot -p`（本机 MySQL 5.7）

### 3.4 `.env` 模板

```ini
# 复制为 .env，填入真实值；.env 不入 git
SECRET_KEY=随便生成一串长随机字符（用 python -c "import secrets;print(secrets.token_urlsafe(50))" 生成）
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=fvil
DB_USER=fvil
DB_PASSWORD=fv_admin_2026
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 3.5 settings.py 关键配置

```python
# config/settings.py 要点
import os
from dotenv import load_dotenv
load_dotenv()                       # 读取 .env

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth',
    'django.contrib.contenttypes', 'django.contrib.sessions',
    'django.contrib.messages', 'django.contrib.staticfiles',
    'core', 'lab',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

```python
# config/__init__.py（加两行，让 PyMySQL 充当 MySQLdb）
import pymysql
pymysql.install_as_MySQLdb()
```

> **MySQL 5.7 注意事项**：本阶段及后续开发**不使用** `models.CheckConstraint`（MySQL 8.0.16 以下不支持），其余通用写法在 5.7 均可运行；生产环境（阿里云）装 MySQL 8.0。

### 3.6 基础模板要点（T0-10）

- `templates/base.html`：顶部导航（首页 / 实验室介绍 / 指导老师 / 实验室荣誉 / 媒体矩阵 / 招新入口），内容块 `{% block content %}`，页脚（实验室名 + 年份）；
- 主题色：`--accent: #1f6feb`（实验室蓝，与导学站一致）；
- Bootstrap 5：下载 `bootstrap.min.css`、`bootstrap.bundle.min.js` 放入 `static/`，**本地引用**（不用 CDN，保证内网/离线也能加载）；
- 首页占位页 `{% block content %}` 先放"建设中"占位，阶段1填充。

### 3.7 `.gitignore` 内容

```
.venv/
__pycache__/
*.pyc
.env
media/
db.sqlite3
.DS_Store
```

### 3.8 阶段0 验收清单

- [ ] `python manage.py check` 无错误；
- [ ] `python manage.py runserver` 后浏览器打开 `http://127.0.0.1:8000/` 能看到占位首页（无 500）；
- [ ] `http://127.0.0.1:8000/admin/` 能用超级用户登录，后台标题为"FVIL 飞行器创新实验室"；
- [ ] `migrate` 无报错（证明 MySQL 5.7 连接正常）；
- [ ] `.env`、`.venv`、`media/` 未被 git 跟踪（`git status` 干净，且这些不在列表）。

---

## 4. 阶段1：官网门面（预计 1~2 周，含内容填充）

### 4.1 数据模型（lab app）

| 模型 | 字段 | 类型/说明 |
|---|---|---|
| `LabProfile` | 简介文本、成立时间、口号、联系方式 | 单例模型（概况页用），后台可编辑 |
| `Teacher`（指导老师） | 姓名、头衔、研究方向、简介、照片(可空)、排序 | 卡片展示 |
| `Honor`（荣誉） | 名称、级别（国家级/省级/校级/其他）、年份、描述(可空)、排序 | 列表展示 |
| `News`（实验室动态） | 标题、正文、发布时间、置顶(布尔) | 主页动态栏 |
| `MediaAccount`（媒体账号） | 平台（抖音/B站/微信公众号）、账号名、链接、排序 | 跳转卡片 |

模型要点：
- 全部注册到 Django Admin，内容由管理员后台维护，**不需要写内容管理页面**；
- `Teacher` 照片、`News` 正文用 `ImageField`/`TextField`，上传文件落 `media/`；
- 排序字段统一 `order = IntegerField(default=0)`，展示时按 order 升序；
- **本阶段不做**成员模型（阶段4再做），不做任何外键关联到用户。

### 4.2 页面与路由表

| 路由 | 视图（core/lab） | 页面内容 |
|---|---|---|
| `/` | core.home | hero 横幅（实验室名+口号）+ 简介摘要 + 最新动态3条 + 荣誉一览 + 媒体入口 + 招新入口按钮 |
| `/about/` | lab.profile | 实验室概况（LabProfile 全文 + 成立时间） |
| `/about/teachers/` | lab.teachers | 指导老师卡片列表 |
| `/about/honors/` | lab.honors | 荣誉列表（按级别/年份） |
| `/about/media/` | lab.media | 媒体矩阵（平台卡片 + 跳转链接） |
| `/recruit/` | core.recruit | 招新占位页（"招新即将开始，敬请关注"，阶段2接入真实报名） |

### 4.3 主页板块设计

1. **Hero**：实验室全名 + 英文缩写 FVIL + 口号（待提供）+ 主视觉背景（可用实验室照片/渐变蓝）；
2. **简介摘要**：LabProfile 截断文本 + "了解更多 →"（跳 /about/）；
3. **最新动态**：News 最新3条（标题+日期）；
4. **荣誉一览**：Honor 前6条（级别徽章）；
5. **媒体矩阵**：抖音/B站卡片（图标 + 账号名 + 跳转链接）；
6. **招新入口**：醒目按钮 → `/recruit/`；
7. **页脚**：实验室名、年份、联系方式。

### 4.4 任务顺序（阶段1 内）

| # | 任务 | 产物 | 验证 |
|---|---|---|---|
| T1-1 | lab app 建模型 → makemigrations → migrate | 5 张表 | migrate 成功 |
| T1-2 | 模型注册 Admin（含列表显示、排序、搜索） | admin 可管理 | 后台增删改查正常 |
| T1-3 | core/lab 视图 + URL 配置 | 6 个路由可访问 | 逐个访问无 404/500 |
| T1-4 | 页面模板（base 已有时只写内容块） | 各页面 | 渲染正常 |
| T1-5 | 样式打磨（实验室蓝、卡片、响应式） | 官网观感 | 手机尺寸浏览正常 |
| T1-6 | **内容填充**（需素材，见 §4.5） | 页面有真实内容 | 见 §4.6 |
| T1-7 | git commit（`feat: 官网主页与实验室介绍（阶段1）`） | 提交 | git log |
| T1-8 | 阶段1 验收 | — | 见 §4.6 |

### 4.5 需要负责人提供的素材清单

| 素材 | 用途 | 状态 |
|---|---|---|
| 实验室简介文案（200字左右概况） | 概况页 + 主页摘要 | 待提供 |
| 主页口号/标语（一句话） | hero 横幅 | 待提供 |
| 指导老师信息（姓名、头衔、研究方向、照片可选） | 指导老师页 | 待提供 |
| 荣誉清单（名称、级别、年份，可先给近三年） | 荣誉页 | 待提供 |
| 抖音/B站账号名 + 主页链接 | 媒体矩阵 | 待提供 |
| 实验室 Logo / 主视觉图（如有） | 主页 hero | 待提供 |
| 常用联系方式（QQ群/邮箱等） | 页脚/概况页 | 待提供 |

> 素材未齐不影响开发：先用占位内容，素材到位后在后台直接改（Admin 已支持）。

### 4.6 阶段1 验收清单

- [ ] 6 个路由全部可访问，无 404/500；
- [ ] 主页在手机宽度（375px）与桌面宽度均排版正常；
- [ ] 管理员在后台新增/修改老师、荣誉、动态后，前台立即生效；
- [ ] 媒体卡片点击能跳转（素材到位后验证真实链接）；
- [ ] 页面无英文残留（按钮、提示均中文）；
- [ ] 配色整体为实验室蓝 #1f6feb 风格。

---

## 5. 阶段2 招新数据库 · 核心数据模型草案（已按负责人确认）

> 草案已确认（2026-09-26），阶段2 开工时直接按此实施，细规划届时再展开实施细节。

### 5.1 模型草案

| 模型 | 字段 | 说明 |
|---|---|---|
| `Batch`（招新批次） | 名称（如"2026秋招"）、报名开始/截止时间、状态（未开始/报名中/培训中/考核中/已结束） | 每年一届，数据按批次隔离；状态自动拦截报名 |
| `Applicant`（报名者） | 姓名、**学号**（唯一）、年级、专业、联系方式、批次(外键)、报名时间、状态（已报名/培训中/通过/淘汰/候补）、备注 | 报名仅填表（**不收集意向方向**），**不注册账号** |
| `Round`（考核轮次） | 批次(外键)、名称（如"第一轮培训"）、类型（培训/考核/作业）、日期、说明 | 一届可多轮 |
| `Score`（成绩） | 报名者(外键)、轮次(外键)、**等级**（A+/A/A-/B+/B/B-，choices）、评价(TextField，可空，验收人员文本)、录入人、录入时间 | **唯一约束**：同一人同一轮仅一条成绩 |

### 5.2 权限与行为设计

- 管理组（Group：`招新管理员`，成员≤20人，由超级管理员分配）→ 可增删改批次、报名者、轮次，**录入成绩（等级+可选评价）**；
- 报名者 → 无账号，不登录；查看自己的方式：**匿名查询页（已确认要做）**——输入学号+姓名即可查询本人各轮次的**等级**与可选的**验收评价**；
- 数据导出：Admin 或自定义"导出Excel"按钮（openpyxl 或 django-import-export），供负责人下载全量名单/成绩表；
- 规模适配：200人报名 → 表单只含必填基本信息；列表页带筛选（批次/状态/专业）；成绩录入支持按轮次批量勾选录入。

### 5.3 已确认决策（负责人 2026-09-26）

1. **匿名查询页：做**——学号+姓名查询，无需登录；
2. **报名时间控制：做**——Batch 状态（未开始/报名中/培训中/考核中/已结束）自动拦截报名；
3. **成绩制：等级制**——A+ / A / A- / B+ / B / B- 六级，查询显示等级，可附带一条验收人员文本评价；
4. **意向方向：不收集**——报名表单只含姓名、学号、年级、专业、联系方式。

### 5.4 数据库选型评估：SQLite vs MySQL（结论：维持 MySQL）

负责人提问：本场景（招新200人/年、等级制成绩、匿名查询）能否直接用 Django 自带 SQLite？

**结论：技术上 SQLite 完全够用，但仍建议维持 MySQL——本场景用 SQLite 没有收益，用 MySQL 没有额外成本。**

| 维度 | SQLite | MySQL（本项目选择） |
|---|---|---|
| 数据量 | 每年约200人 × 几轮 ≈ 千条级，毫无压力 | 同样无压力 |
| 并发 | 写锁为全库级；本场景写入极少（新生报名 + 管理员录分），实际够用 | 成熟并发模型，无此顾虑 |
| 部署运维 | 单文件，备份=复制文件，最省事；但 web 进程需可写该文件（权限易踩坑） | 独立服务，需安装维护；本机已有 5.7，云上装 8.0 成本为零 |
| 扩展性 | 不适合多实例/远程访问；实验室后续的项目、财务、文档库等模块一旦接入，并发与数据量上升会受限 | 支持后续全部扩展 |
| 环境一致性 | 开发用 SQLite + 部署用 MySQL = **双环境差异**（类型、行为），有"本地能跑、上线炸"的迁移坑 | 本机 5.7 开发 + 云上 8.0，差异已规避（不用 CheckConstraint） |
| 运维/备份工具 | 少 | 成熟（mysqldump、binlog、权限体系） |

**决定**：维持 MySQL 为主数据库（开发 5.7 / 部署 8.0）。SQLite 仅作为本地快速演示时的备选，不作为正式选型。

---

## 6. 验证与交付方式（全局约定）

- 每个任务完成后，按该任务"验证"列的**最小验证**执行（命令或浏览器操作）；
- 阶段验收按验收清单逐项打勾；未过的项不得标记完成；
- 代码提交：每完成一个任务或一组任务即 commit，提交信息带 `[fvil]` 或 `feat:` 前缀；
- 本机运行入口：`.venv\Scripts\activate` 后 `python manage.py runserver`；
- 若执行中遇到本机环境问题（如 MySQL 密码、端口占用），先按报错信息处理；处理不了记录问题继续下一个任务，最后集中报告。

---

## 7. 协作方式约定（2026-09-26）

- 负责人自行学习开发技术，学习中的提问**不进入本会话**（避免干扰执行）；
- 负责人按学习节奏**细化任务放行**：例如阶段0可能拆成多段逐段放行；
- 助手只按当前放行的小段执行并自测，**不越段提前开工**；
- 每个放行段完成后给出结果与验证情况，等待下一段放行。

---

*合肥工业大学 飞行器创新实验室（FVIL）· 官网建设项目*
