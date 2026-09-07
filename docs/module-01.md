# 模块 1：项目基础、账户认证与用户资料

## 本模块范围

- 创建 Vue 3 + Vite 和 FastAPI 工程骨架
- Supabase Auth 邮箱或手机号 + 密码注册登录；手机号注册根据 Vercel/Cloudflare 从访问 IP 提供的国家代码预选区号，获取不到时默认 `+86`，用户可在下拉菜单中更换或手动输入其他区号
- 完整手机号仍使用 E.164 国际格式（如 `+8613800138000`），并通过内部邮箱别名登录，不启用短信、OTP 或 Supabase 原生 Phone provider
- MVP 关闭邮箱确认，不发送邮件或短信验证码；暂不提供找回密码
- 未登录用户访问 `/` 时先看到 DayFlow 欢迎页。该页为深色主题，围绕产品自身的隐喻设计：
  - **主视觉「时间之河」**：分钟化作发光圆点从时钟流出，沿三条曲线汇入“课程学习 / 项目推进 / 阅读”三个容器，容器随之逐渐充满。圆点是 SVG `<circle>` + `<animateMotion><mpath>`，与曲线共用同一条路径并处在同一 viewBox 内，因此在任何屏幕宽度下都与画面等比缩放、不会脱轨
  - 标题分行上浮入场，“重要的事”上有循环流动的渐变；鼠标移动时主视觉做轻微 3D 视差，跟随光标还有一团柔光；主按钮有磁吸效果
  - 数字（24 小时 / 1 秒 / 100%）在进入视口时缓动累加；能力关键词做无缝横向滚动；产品截图放在深色设备框里交叉淡入，右侧标签页带自动切换进度条；能力卡片滚动进入时错峰上浮，卡片插图各自有绘制、旋转与柱状动效；结尾卡片是循环流动的渐变描边
  - **动效是装饰，不承担可读性**：滚动揭示的隐藏状态只在 JS 就绪后由 `.lp--reveal` 打开，另有 2.5 秒兜底定时器强制显示；截图用常驻叠放 + class 交叉淡入，而不是带 key 的 `<Transition>`（后者在过渡未执行时会把图片永久留在 `opacity: 0`）。`prefers-reduced-motion: reduce` 下关闭全部动画与过渡
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
