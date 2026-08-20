# DMS 项目规则 (Project Rules)

> 本规则文件基于 DMS 项目的实际代码、配置文件与环境编写，所有变更须遵循此规则。
> 最后核对日期：2026-08-20

---

## 1. 技术栈与版本（必须严格遵守）

### 1.1 后端 (Backend)
| 组件 | 版本 | 说明 |
| --- | --- | --- |
| Python | **3.7.2** | 虚拟环境位于 `venv/`，解释器源自 `C:\Python372\mecheck\Scripts` |
| Django | **2.1.7** | 主框架，URL 使用 `path()` / `re_path()`（非旧版 `url()`） |
| Django REST Framework | **3.11.0** | REST API 框架 |
| djangorestframework-simplejwt | **5.2.0** | JWT 认证（`ACCESS_TOKEN_LIFETIME` 30 分钟） |
| djangorestframework-jwt | **1.11.0** | 旧版 JWT（部分模块仍在使用） |
| Celery | **4.4.2** | 异步/定时任务，配合 `django-celery==3.3.1` |
| Channels | **2.2.0** | WebSocket（Daphne 2.5.0） |
| django-simpleui | **2022.4.9** | Admin 后台 UI |
| django-import-export | **1.2.0** | Excel 导入导出 |
| django-cors-headers | **3.7.0** | 跨域支持 |
| django-filter | **2.2.0** | 查询过滤 |
| django-crispy-forms | **1.7.2** | 表单渲染 |

### 1.2 数据库与缓存
| 组件 | 版本 | 连接信息 |
| --- | --- | --- |
| MySQL | 主数据库 | `127.0.0.1:3306`，库名 `dms`，引擎 `django.db.backends.mysql`（PyMySQL 0.9.3） |
| MongoDB | 辅助数据库 | `127.0.0.1:27016`，通过 `mongoengine 0.20.0` / `pymongo 3.10.1` 连接 |
| Redis | 消息队列 + 缓存 | `127.0.0.1:6379`，Celery Broker 用 DB 3，Result Backend 用 DB 4 |
| SQLite | `db.sqlite3` | 仅遗留，**不作为主库** |

### 1.3 前端 (Frontend) —— 注意：使用 Vue，非 React
| 组件 | 版本 | 引入方式 |
| --- | --- | --- |
| **Vue.js** | **2.6.10** | 静态文件 `/static/js/vue.min.js`（**非构建工具链，无 webpack/vite**） |
| **Element UI** | **2.12.0** | 静态文件 `/static/js/Element/*.js`（按需引入组件）+ CSS |
| vue-router | 3.1.3 | `/static/js/vue-router.min.js`（部分页面使用） |
| axios | - | `/static/js/axios.min.js`（HTTP 请求） |
| jQuery | - | `/static/js/lib/jquery.min.js` |
| Bootstrap | 3.x | `/static/css/bootstrap.min.css` + `/static/js/lib/bootstrap.min.js` |
| ECharts | - | `/static/js/echart/echart.js` |
| SheetJS (xlsx) | - | `/static/js/xlsx/xlsx.js`（Excel 解析/导出） |
| Babel | - | `/static/js/es6/babel.min.js`（**浏览器端转译**，非预编译） |

> **重要约束**：前端代码写在 Django 模板的 `{% block scripts %}` 中，使用 `<script type="text/babel">` 让浏览器端 babel 转译 ES6。**禁止引入 React / 构建工具链**。

---

## 2. 项目结构

```
DMS/
├── DMS/                    # 项目主包（settings / urls / celery / wsgi）
│   ├── settings.py         # 开发环境配置（默认）
│   ├── settings_server_.py # 生产环境配置
│   ├── celery.py           # Celery 实例
│   └── urls.py             # 根路由
├── app01/                  # 核心应用（登录/首页/用户/任务）
├── Device*/                # 各设备管理应用（DeviceLNV, DeviceABO, DeviceA39, ...）
├── AdapterPowerCode/       # 适配器电源管理
├── ComputerMS/             # 电脑管理
├── ChairCabinetMS/         # 椅柜管理
├── CabinetManage/          # 机柜管理
├── RetainedSample/         # 留样管理
├── WirelessAP/             # 无线 AP 管理
├── TUMHistory/             # TUM 历史
├── extra_apps/xadmin/      # 自定义 xadmin
├── middleware/             # 自定义中间件（RBAC 权限 / 用户 IP 记录）
│   ├── checkper.py         # RbacMiddleware 权限校验
│   └── UserIP.py           # LogMiddle 日志中间件
├── service/                # 业务服务层
│   └── init_permission.py  # 权限初始化
├── static/                 # 前端静态资源（js / css / images / fonts）
├── templates/              # Django 模板
│   ├── base.html           # 基础模板（所有页面继承）
│   ├── login.html / index.html
│   └── <app_name>/         # 各应用专属模板
├── logs/                   # 日志目录（按日期分文件）
├── medias/                 # 上传文件
├── venv/                   # Python 虚拟环境
├── manage.py
└── requirements.txt        # Python 依赖
```

### 2.1 应用 (App) 标准结构
每个 Django App 必须包含以下文件：
- `models.py` - 数据模型
- `views.py` - 视图（函数视图为主）
- `urls.py` - 路由，**必须定义 `app_name`**
- `admin.py` / `apps.py` - Admin 注册与 AppConfig
- `tests.py` - 测试

---

## 3. 后端编码规范

### 3.1 视图 (Views)
- **优先使用函数视图 (FBV)**，符合项目现有风格；DRF 接口可使用类视图 (CBV)。
- 视图返回 `JsonResponse` 或 `render(request, template, context)`。
- 使用 `@csrf_exempt` 装饰器处理 AJAX 接口（项目惯例）。
- 导入示例（遵循现有风格）：
  ```python
  from django.shortcuts import render, redirect, HttpResponse
  from django.views.decorators.csrf import csrf_exempt
  from django.http import JsonResponse
  from django.db import transaction
  from django.db.models import Max, Min, Sum, Count, Q
  ```

### 3.2 URL 路由
- 根路由 `DMS/urls.py` 使用 `path()` + `re_path()`。
- 每个 App 的 `urls.py` 必须声明 `app_name`，并通过 `include('app.urls', namespace='app')` 挂载。
- URL 名称使用 `name=` 参数显式命名。

### 3.3 模型 (Models)
- 字段必须设置 `verbose_name`（繁体中文，与现有数据一致）。
- 选项 (choices) 使用繁体中文，定义在模型类内部（如 `Customer_list`、`BR_Status_choice`）。
- 文件上传字段使用 `ImageField` / `FileField`，并通过 `pre_delete` signal 清理文件。
- `__unicode__` 方法用于 Python 2 兼容（项目历史遗留，保持一致）。

### 3.4 认证与权限
- **Session 认证**：Web 页面使用 Django Session（`SESSION_ENGINE='django.contrib.sessions.backends.db'`）。
- **JWT 认证**：REST API 使用 `djangorestframework-simplejwt`，通过 `MyTokenObtainPairView` 自定义。
- **RBAC 权限**：`middleware/checkper.py` 的 `RbacMiddleware` 进行 URL 级权限校验。
- **权限白名单**：`settings.SAFE_URL` 中配置免鉴权 URL。
- 自定义用户表 `app01.UserInfo`（不替换默认 `User`，通过外键关联）。

### 3.5 配置 (Settings)
- `LANGUAGE_CODE = 'zh-hans'`，`TIME_ZONE = 'Asia/Shanghai'`，`USE_TZ = False`。
- `DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'`。
- `SESSION_COOKIE_AGE = 21600`（12 小时），`SESSION_SAVE_EVERY_REQUEST = True`。
- 日志：`RotatingFileHandler` 写入 `logs/`，按 `all-`/`error-`/`info-` 分级，文件名带日期。

### 3.6 Celery 任务
- 任务定义在各 App 的 `tasks.py`，由 `app.autodiscover_tasks()` 自动发现。
- Broker：`redis://:DCT2019@127.0.0.1:6379/3`，Backend：DB 4。
- 定时任务配置在 `settings.CELERY_BEAT_SCHEDULE`，使用 `crontab` 或秒数。
- 启动脚本：`DMSceleryworker.bat`（worker）、`DMScelerybeat.bat`（beat）。

---

## 4. 前端编码规范

### 4.1 模板结构
- **所有页面必须继承 `base.html`**：`{% extends 'base.html' %}`。
- 使用 `{% load staticfiles %}` 加载静态资源标签。
- 块定义：`{% block title %}` / `{% block css %}` / `{% block scripts %}`。

### 4.2 Vue + Element UI 使用模式（必须遵循）
```html
{% extends 'base.html' %}
{% load staticfiles %}
{% block title %}页面标题{% endblock %}

{% block css %}
<!-- 页面专属样式 -->
{% endblock %}

{% block content %}
<div id="app">
  <!-- Element UI 组件，使用 ${ } 插值（避免与 Django {{ }} 冲突） -->
  <el-table :data="tableData">
    <el-table-column prop="name" label="名称"></el-table-column>
  </el-table>
</div>
{% endblock %}

{% block scripts %}
<script src="/static/js/es6/polyfill.min.js"></script>
<script src="/static/js/es6/babel.min.js"></script>
<script src="/static/js/axios.min.js"></script>
<script src="/static/js/vue.min.js"></script>
<script src="/static/js/qs.js"></script>
<script src="/static/js/Element/index.js"></script>
<!-- 按需引入 Element 组件 -->
<script src="/static/js/Element/table.js"></script>
<script src="/static/js/Element/main.js"></script>

<script type="text/babel">
new Vue({
    el: '#app',
    delimiters: ['${', '}'],   // 关键：自定义分隔符避免与 Django 模板冲突
    data: function () {
        return { tableData: [] };
    },
    methods: { /* ... */ }
});
</script>
{% endblock %}
```

### 4.3 关键前端约束
1. **Vue 分隔符必须使用 `${` `}`**，不可使用默认 `{{ }}`（会与 Django 模板冲突）。
2. **脚本类型为 `text/babel`**，依赖浏览器端 `babel.min.js` 转译，**不使用 webpack/vite 预编译**。
3. **静态资源通过绝对路径 `/static/js/...` 引入**，不使用 npm import。
4. **Element UI 组件按需引入**（`/static/js/Element/*.js`），勿整包引入。
5. AJAX 请求使用 `axios`，复杂参数序列化使用 `qs`。
6. **样式修改隔离**：全局样式仅改 `base.html`；页面样式写在 `{% block css %}` 内，不影响其他子页面。

---

## 5. 通用约定

### 5.1 语言与字符编码
- 代码文件使用 UTF-8 编码。
- 注释、verbose_name、choices 使用**繁体中文**（与现有业务数据保持一致）。
- 交流与文档使用中文。

### 5.2 静态文件
- 前端资源统一放 `static/` 下，按类别分子目录（`js/`、`css/`、`images/`、`fonts/`）。
- 第三方库放 `static/js/lib/` 或 `static/download_UPK/`。
- 上传文件存放于 `MEDIA_ROOT = 'c:\DMSmedia'`。

### 5.3 依赖管理
- Python 依赖通过 `pip install` 安装并记录到 `requirements.txt`。
- 前端**不使用 npm/package.json 管理组件**（`static/package.json` 仅为历史遗留，无实际作用）。
- 新增第三方 JS 库时，下载到 `static/js/lib/` 后用 `<script>` 引入。

### 5.4 错误处理
- 数据库查询须考虑记录不存在、外键约束冲突等异常。
- 外部 HTTP 请求（如调用 DDIS Server）须 `try/except` 包裹并打印错误日志。
- 使用 `logging`（`logger = logging.getLogger('Django')`）记录关键操作。

### 5.5 运行与部署
- 开发启动：`python manage.py runserver`。
- Celery：`DMSceleryworker.bat` + `DMScelerybeat.bat`。
- 生产配置切换：修改 `manage.py` 的 `DJANGO_SETTINGS_MODULE` 为 `DMS.settings_server_`。
- `ALLOWED_HOSTS = ['*']`，`DEBUG = True`（开发环境）。

---

## 6. 禁止事项
1. 禁止引入 React、Angular 或任何前端构建工具链（webpack/vite/rollup）。
2. 禁止升级 Django / Python / Vue / Element UI 主版本（会破坏现有兼容性）。
3. 禁止修改 `requirements.txt` 中已锁版本的依赖（除非明确需要并测试通过）。
4. 禁止在子页面模板中修改全局样式（影响其他页面）。
5. 禁止使用 Django 模板默认 `{{ }}` 作为 Vue 插值（必须用 `${ }`）。
6. 禁止删除 `middleware/` 中的 RBAC 权限中间件（会破坏权限体系）。
