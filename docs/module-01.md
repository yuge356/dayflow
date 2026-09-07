# 模块 1：项目基础、账户认证与用户资料

## 本模块范围

- 创建 Vue 3 + Vite 和 FastAPI 工程骨架
- Supabase Auth 邮箱或手机号 + 密码注册登录；手机号注册根据 Vercel/Cloudflare 从访问 IP 提供的国家代码预选区号，获取不到时默认 `+86`，用户可在下拉菜单中更换或手动输入其他区号
- 完整手机号仍使用 E.164 国际格式（如 `+8613800138000`），并通过内部邮箱别名登录，不启用短信、OTP 或 Supabase 原生 Phone provider
- MVP 关闭邮箱确认，不发送邮件或短信验证码；暂不提供找回密码
- 未登录用户访问 `/` 时先看到 DayFlow 欢迎页。该页为**浅色液态玻璃**风格：柔和的冷蓝—紫—粉渐变底色上漂浮着大颗半透明彩虹气泡，内容全部承载在扁平的高透玻璃卡片里（细白描边、柔和投影、`backdrop-filter` 毛玻璃），不使用厚重阴影或拟物质感
  - **主视觉：任务树完成动效**。一个玻璃窗口里横向排布“项目 → 模块 → 任务”的任务树，动画按 `子任务 → 所属模块 → 项目` 的顺序推进：叶子任务先被暖橙→粉→紫→蓝的渐变从左向右填满、白色对号沿路径画出、时长切换为 `100%` 且状态徽标变成“已完成”；随后这条连接线被同一渐变点亮并汇入上级；两个子任务都完成后模块被填满；最后整个项目节点被填满打勾。完成后停留片刻再从头循环，下方的说明文字随阶段切换
  - 动画整体在一个 `viewBox` 内（节点、文字、连接线、对号都是 SVG），因此在任何屏幕宽度下等比缩放、不会错位；节奏由一个步进计数器驱动（每步 900ms），CSS 只负责各元素的过渡
  - 其余动效：标题分行上浮、“重要的事”上循环流动的渐变、气泡缓慢漂移、主按钮磁吸、数字进入视口时缓动累加、截图交叉淡入并带自动切换进度条、能力卡片滚动错峰上浮、结尾卡片渐变描边流动
  - **动效是装饰，不承担可读性**：滚动揭示的隐藏状态只在 JS 就绪后由 `.lp--reveal` 打开，另有 2.5 秒兜底定时器强制显示；截图用常驻叠放 + class 交叉淡入，而不是带 key 的 `<Transition>`（后者在过渡未执行时会把图片永久留在 `opacity: 0`）。`prefers-reduced-motion: reduce` 下关闭全部动画与过渡，任务树直接显示为全部完成的终态
- 登录页采用居中的紫白左右分栏圆角卡片，欢迎语、表单、按钮和错误提示全部使用中文；登录与注册在当前页面内切换，登录和注册密码框右侧均使用左侧眼睛图标切换密码显隐、最右侧锁图标标识密码字段，并隐藏浏览器重复生成的显隐按钮；原 `/register` 地址兼容地打开注册状态，窄屏自动切换为上下布局
- 新注册账号在 Supabase `user_metadata` 中写入 `onboarding_completed=false`，首次登录进入 `/onboarding`；指引包含今日任务、项目/任务与时间统计三个步骤，可上一步、下一步、跳过或完成。完成状态通过 `updateUser` 写回元数据，不新增业务数据库字段
- 为兼容上线前已经存在的账号，缺少 `onboarding_completed` 元数据时默认视为已经完成，老用户登录后直接进入 `/today`
- 产品品牌统一为 DayFlow；Logo 为品牌紫（#7456f5）大圆角方块底上的白色 "D" 字，内 D 区域透出底色并包含白色指针时钟（竖针向上、横针向右、中心圆点）。它以内联 SVG 呈现于侧栏、登录页、欢迎页与引导页，同一图形亦作为站点 favicon（`public/dayflow-logo.svg`），不显示中文副标题
- 全局界面在不改变原有配色、布局和组件结构的前提下使用轻度玻璃视觉增强：大面积业务卡片使用接近实色的半透明表面、淡描边和柔和阴影，但不执行实时背景模糊；模糊只保留在侧栏、登录卡片和小型浮层，减少页面切换时的 GPU 合成开销
- Supabase 自动持久化和刷新会话；FastAPI 校验 Supabase Bearer Token
- 查看和修改个人资料
- Supabase 托管 PostgreSQL 初始迁移与账号资料镜像触发器
- `users`、`profiles` 的数据库级行权限策略
- 健康检查、错误状态和基础测试

本模块没有提前实现任务、计时、每日计划、伙伴或通知功能。

详细的后台开关、连接字符串和环境变量步骤见 [Supabase MVP 配置](supabase-setup.md)。

## 本地运行

### 1. 启动 PostgreSQL

```bash
docker compose up -d postgres
```

### 2. 启动后端

```bash
cd backend
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

API 文档地址：`http://localhost:8000/docs`

### 3. 启动前端

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

前端地址：`http://localhost:5174`

## 验证命令

后端：

```bash
cd backend
pytest
ruff check .
```

前端：

```bash
cd frontend
npm run type-check
npm run build
```

## 认证与首次使用验收

1. 退出登录后访问 `/`，显示欢迎页而不是应用壳层；登录和注册按钮都打开中文认证页面。
2. 新注册账号进入 `/onboarding`，刷新后仍停留在指引；完成或跳过后进入 `/today`。
3. 再次登录同一账号不重复显示指引；升级前创建、没有 onboarding 元数据的老账号也直接进入 `/today`。
4. 登录态由 Supabase JS 持久化并自动刷新，业务 API 继续使用相同的 Supabase Access Token。
5. 打开手机号注册时默认显示中国大陆 `+86`；生产环境存在可用的 IP 国家信息时自动切换，用户仍可手动修改。
