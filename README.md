# FVIL 飞行器创新实验室业务平台

合肥工业大学飞行器创新实验室（FVIL）的自建**业务平台**（非官方授权的"官网"，用于实验室内部业务运转）。

当前进度：**阶段0~3 已完成并验收**（地基 / 站点门面 / 招新系统 / 作业系统与材料库），阶段4（成员管理）规划中。

## 功能模块

| 模块 | 说明 | 状态 |
|---|---|---|
| 站点门面 | 首页、实验室介绍、指导老师 | ✅ 阶段1 |
| 招新系统 | 报名（学号自动推导年级）、批次管理、成绩录入（等级制）、匿名查询、Excel 导出 | ✅ 阶段2 |
| 作业系统 | 发布作业（PDF）、学生双文件提交（报告 PDF + 源码 ZIP，命名校验、截止拦截、覆盖写入）、人工批改录分、批量打包下载 | ✅ 阶段3 |
| 材料库 | 四分类资料（导学/作业/附录/其他），Admin 上传、公开下载 | ✅ 阶段3 |
| 导学站 | C 语言导学资料静态站（独立仓库 `fvil-ec-guide`，构建产物挂载于 `/guide/`） | ✅ T2-1 |
| 成员管理 | 成员简介、状态管理 | 阶段4（规划中） |

## 技术栈

- Python 3.10 + Django 5.2（MTV，Django Templates + Bootstrap 5，静态资源本地化）
- MySQL 8.0（`utf8mb4`；Django 5.2 要求 MySQL ≥ 8.0.11）
- 文件存储：本地 `media/`（附件量小，无需对象存储）
- 配置与代码分离（`.env`），git 版本控制

## 目录结构

```
fvil/
├─ config/          # 项目配置（settings / 全局 urls）
├─ core/            # 主页、导学站服务
├─ lab/             # 实验室介绍（概况 / 指导老师）
├─ recruitment/     # 招新（报名 / 批次 / 成绩 / 查询 / 导出）
├─ doclib/          # 作业系统 + 材料库
├─ media/           # 上传文件实体（git 忽略，与数据库共同构成数据）
├─ static/          # 前端静态资源（Bootstrap / 自定义 CSS / 素材图）
├─ templates/       # 全站基础模板（base.html 导航 7 项）
├─ docs/            # 计划书、阶段报告（见下文文档索引）
└─ fvil-ec-guide/   # C 语言导学站（独立嵌套 git 仓库，web/ 为构建产物）
```

## 快速开始

```bash
# 1. 创建并激活虚拟环境（Windows）
python -m venv .venv
.venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 .env（复制 .env.example 或参照 config/settings.py 的 os.getenv）
#    SECRET_KEY / DEBUG / ALLOWED_HOSTS / DB_NAME / DB_USER / DB_PASSWORD / DB_HOST / DB_PORT

# 4. 建库并迁移
#    在 MySQL 中创建数据库（utf8mb4 / utf8mb4_unicode_ci）及业务账号，授权 fvil.*
python manage.py migrate

# 5. 创建后台管理员
python manage.py createsuperuser

# 6. 启动
python manage.py runserver
```

## 数据与文件

- **数据 = MySQL 库 `fvil` + `media/` 目录**，两者部署迁移时都要处理；
- 数据库账号、后台账号密码均不写入本文件（见 `.env` 与后台）；
- `media/` 已被 `.gitignore` 忽略；导学站 `fvil-ec-guide` 为独立仓库，部署时需单独同步。

## 权限组

后台管理权限按组划分（数据迁移自动创建）：

| 组 | 权限范围 | 用途 |
|---|---|---|
| 招新管理员 | recruitment 4 模型 16 项 | 录分、导出 |
| 资料管理员 | doclib 3 模型 12 项 | 发布作业、管理材料与提交 |

超级管理员不自动属于上述组，需在后台手动将账号加入对应组。

## 文档索引

- `docs/FVIL官网建设计划.md`（粗规划）
- `docs/FVIL官网建设计划-细规划-阶段0-1.md` / `-阶段2.md` / `-阶段3.md`
- `docs/阶段0完成报告.md` / `docs/阶段3报告-部署前.md`

## License

**未选择**（项目为实验室内部业务平台，暂无对外发布计划）。若后续开源，建议从 MIT / Apache-2.0 中二选一（详见项目讨论记录）。
