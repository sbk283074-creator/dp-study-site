# CODE 平台改造计划 — 把 Python Mastery 升级为多语言编程平台

> 状态：**已开工**。决策已拍板（1A / 2B / 3A / 4A / 5A），**P0 地基 + P1 迁移已完成**。
> 调研日期：2026-09-19。所有数字为本机实测，非估算（估算已单独标注）。

### 0. 进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| **P0** | `code/` 骨架 + 泛化构建器（`_build/`，位置参数 + `languages.json` 注册表）+ 平台首页 | ✅ 完成 |
| **P1** | Python 迁入 `code/python`（`git mv`，历史保留）+ Hub 接线 + `PYTHON/` 跳转页 + 搜索索引重建 | ✅ 完成 |
| **P2** | C/C++ 赛道 | 🟡 进行中：**35 / 67 章**（ch00–16、17–30、34–37），全部机器验证 —— 整条赛道 **553 个代码块全绿**（3 个因 macOS 无泄漏检测按设计跳过）。权威清单见 `code/cpp/OUTLINE.md` |
| **P3** | Java (+Kotlin) 赛道 | 🟡 进行中：赛道已建（STYLE + 校验器 + ch00–ch02，40 个代码块全绿） |
| **P4** | TypeScript / C# / Go / Rust 赛道 + 迷你赛道 | ⬜ 未开始 |
| **P5** | 终极项目 Nebula Arena（全栈多语言） | ⬜ 未开始 |

> **⚠️ "完成" 指本机工作树，不等于线上。** P0/P1 的提交（`d524957`）**尚未推送** ——
> 线上 `/code/` 与 `/code/python/` 仍是 **404**，`/PYTHON/` 还是迁移前的 2.2 MB 旧书。
> 推送后要用 `curl` 复核这三条 URL，再回来改这一行。**进度表是声明，`curl` 才是事实。**

新增语言的标准操作：建 `code/<lang>/`（`chapters/` + `parts.json`）→ 在 `_build/languages.json`
注册 → `cd code/_build && python3 build.py`（位置参数：`python3 build.py python` 只构建一个）。
构建器无需改动。改完跑一次 `sh code/_build/check-idempotent.sh` 确认重跑构建零字节变化。

### 0.1 C/C++ 赛道：67 章总表与缺口

> **本节已于 2026-09-21 重写。** 旧版把 C/C++ 排到 ch43（44 章），那是单语言的规模；
> Lucas 要求"两门语言合一本，至少 50 章且更深"，随后 `DEPTH-AUDIT.md` 又补上两层，
> 因此**权威清单已迁移到 `code/cpp/OUTLINE.md`（67 章，ch00–66）**。本节只记录
> 现状、缺口与写作约束；逐章主题以 OUTLINE 为准，避免两处失同步。

**为什么要 67 章而不是 44：** ① C 与 C++ 是两门语言，各需完整主轴；② 深度审计
（`code/DEPTH-AUDIT.md`，全库零计数取证据）发现两个真实空洞并新增两个 Part——
**无代价理论**（全书零处 Big-O / amortised cost）→ Part VIII 59–63；**无安全层**
（零处 SSRF / 路径穿越 / 时序攻击）→ Part IX 64–65。审计同时确认长项应保留：
C++ 中位章节 4,398 词（下限 2,400）、无占位章。

**已完成 38 / 67（全部机器验证，整条赛道 602 个代码块全绿，ch00–37 连续无缺口）：**

| Part | 章号 | 状态 |
|---|---|---|
| 0 Start Here | 00–01 | ✅ |
| I · C Foundations | 02–09 | ✅（08 位/字节序/内存布局、09 编译流水线为上一轮新增） |
| II · C Advanced | 10–16 | ✅（15 预处理器、16 未定义行为与 Sanitizer 为上一轮新增） |
| III · 项目1 静态 HTTP 服务器 | 17–21 | ✅ |
| IV · 过渡到现代 C++ | 22–33 | ✅ **本轮补齐 31 / 32 / 33，Part IV 完成** |
| V · Track A Web 服务 | 34–45 | 🟡 已完成 34–37；**38–45 待写**（SQLite 可验证：SDK 有 `sqlite3.h` + `-lsqlite3`） |
| VI · Track B 游戏 | 46–54 | ⬜ 全部待写 |
| VII · 附录 | 55–58 | ⬜ 全部待写 |
| VIII · 算法与复杂度 | 59–63 | ⬜ 全部待写（审计新增） |
| IX · 安全加固 | 64–65 | ⬜ 全部待写（审计新增） |
| X · Where Next | 66 | ⬜ 待写 |

#### 本轮（2026-09-21 晚）完成的 3 章与实测数据

| 章 | 主题 | 块数 | 词数 | 关键实测结论 |
|---|---|---|---|---|
| 31 | Operator Overloading and Iterators | 20/20 | 6,007 | `(a + 3) += 5` **能编译**（成员 `+=` 可在右值上调用），只是修改随临时对象丢弃 → 比"编译报错"更值得讲；`std::sort` 作用在 `list` 上时，报错落在 `<algorithm>` 内部的 `__last - __first`，而非调用点 |
| 32 | Value Categories and Perfect Forwarding | 14/14 | 4,845 | `return std::move(local)` 被 `-Wpessimizing-move` 判为**错误**（`-Werror` 下编不过），故做成 `warn` 块；`std::move` 作用在 const 对象上静默复制，无任何诊断 |
| 33 | C++20 and C++23 | 15/15 | 4,873 | 本机 libc++ 实测可用：concepts / ranges / span / `<compare>` / `std::format`（c++20）与 `std::expected`（c++23）；**不支持** `{:.1%}` 浮点百分比格式（编译期报错）→ 已移除 |

#### 本轮对工具链的唯一改动：按章 `std:` 覆盖

ch33 需要 C++20/23，而校验器原来全局写死 `-std=c++17`。改动（`code/cpp/tools/verify_examples.py`）：

- 新增 `chapter_std(path)`：读章节 frontmatter 的 `std:` 行，白名单 `c++17 / c++20 / c++23 / c17 / c11`，**不在白名单即硬报错**（防止拼写静默通过）。
- `Block.__slots__` 增加 `std`，`Block.standard` 属性优先用它；`run_dir` 为每章的每个块赋值；`check_shell` 的 `-std=` 同步。
- **默认值不变**，因此既有 35 章的语义完全不受影响；需要新标准的章必须显式声明。
- 已写入 `code/cpp/STYLE.md`（新增"Raising the language standard for one chapter"一节）。
- **已做"故意移除即失败"验证**：临时章带 `std: c++20` 时 1/1 绿，删掉该行后同一份代码立即红（`error: expected expression`，`<concepts>` 不可用）。探针已删除。

**写作时的硬约束（实测，见 `code/cpp/STYLE.md`）：**
- **SDL2 / Raylib / GLFW / ncurses 均未安装，且无 homebrew、无 cmake** → Track B（46–54）
  的代码必须标注"未经机器验证"；可替代方案是自写软渲染器（帧缓冲 → PPM/像素断言），零依赖且可验证。
- **UBSan 退出码仍为 0**（macOS）→ UB 演示一律 `run-san-catch`，绝不用 `run`，否则会假绿。
- **macOS 无泄漏检测** → 泄漏演示只能标 SKIPPED，并在正文说明需在 Linux/valgrind 下复现。
- **C++20 modules 在 Apple clang 不可用** → 不写这一章。

写新章的固定流程（`code/cpp/STYLE.md` 是完整契约）：在 `tools/gen/<NN>/` 写真实源码 →
`gen.py` 编译运行并抓取**真实**输出拼装章节 → `tools/verify_examples.py <slug>` 必须零失败 →
`cd code/_build && python3 build.py` 重建。**严禁手写输出围栏。**

### 0.2 Java 赛道（P3）

已建：`code/java/`（STYLE.md + parts.json + `tools/verify_examples.py` + 自检夹具）· 已写 ch00–ch02。

**工具链（关键前提）**：本机原本**没有 JDK**（`/usr/bin/java` 只是 macOS 的安装引导桩，直接调用会
失败）。已下载 **Temurin JDK 21.0.12.1** 到 `~/.workbuddy/binaries/java/jdk-21.0.12.1+1/`（**仓库外**，
不入库）。校验器会依次探测 `JAVA_HOME` → 该目录 → `/Library/Java/JavaVirtualMachines/` → `PATH`，
并且只接受 `javac -version` 真正跑通的候选 —— 找不到 JDK 就 **exit 2，绝不假装通过**。

JDK 21 自带 `jar` / `jwebserver` / `jlink` / `jpackage` / `jdk.httpserver` 模块，**无第三方依赖即可
写 Web 服务**；`javax.swing` + `java.awt` 也在，Track B 用离屏 `BufferedImage` 渲染，可用像素断言
做机器验证。Maven / Gradle / JUnit / JavaFX / LibGDX **均未安装**，因此全书只用 JDK，正文里提一句
业界会用什么。

| 章 | Part | 主题 |
|---|---|---|
| 00 | 0 | 怎么用这本书 + JVM/字节码 + 文件名规则 |
| 01 | I | 第一个程序：`main` 签名、打印、参数、包与 classpath |
| 02 | I | 原始类型 vs 引用：溢出、浮点、`==` 与 `equals`、装箱缓存 |
| 03 | I | 字符串：不可变、interning、文本块、`StringBuilder` |
| 04 | I | 控制流：`switch` 模式匹配（Java 21）、循环、`break`/`continue` |
| 05 | I | 数组与增强 for |
| 06 | I | 方法、重载、值传递（含"对象内容可变、引用本身不可变"） |
| 07 | I | 类、字段、构造器、`this` |
| 08 | I | 包、classpath、JAR 打包（`jar --create --main-class`） |
| 09 | I | 异常：checked vs unchecked、try-with-resources |
| 10 | I | 文件与 NIO.2 |
| 11–17 | II | 接口/抽象类 · 泛型与擦除 · 集合 · `equals`/`hashCode`/`Comparable` · record/enum/sealed · Lambda 与 Stream · 手写测试 |
| 18–23 | III | 项目 1：**Quill** 命令行笔记库（命令模式 + JSON + 打包成可执行 JAR） |
| 24–30 | IV | Track A：**Bulletin** Web 服务（裸 socket → `HttpServer` → 路由 → 模板/转义 → 表单 → 持久化 → 会话与登录） |
| 31–36 | V | Track B：**Ironhold** 游戏（游戏循环 → 输入/计时 → 精灵与 AABB 碰撞 → 状态机 → 波次 → 打磨与打包） |
| 37–39 | VI | 附录：JVM 与调优 · **Kotlin 扩展模块** · 下一步 |

写新章流程与 C++ 一致：`code/java/STYLE.md` 是完整契约（围栏指令 `run` / `bad` / `warn` / `throw` /
`compile` / `-files` / `sh run`），先 `--self-test` 确认校验器没瞎，再逐章
`tools/verify_examples.py <slug>`，最后 `cd code/_build && python3 build.py`。

---

## 一、现状调研：Python Mastery 解剖

> ⚠️ **本节是 2026-09-19 的迁移前快照，其中的路径已全部过时。** 文中 `PYTHON/python-mastery/`、
> `PYTHON/verify/` 等路径在 P1 迁移后已不存在 —— 现为 `code/python/`、`code/verify/python/`。
> 保留原文是为了留住"为什么这么改"的推理过程；**要查当前布局请直接看 §2。**

### 1.1 目录与产物

| 路径 | 体积 | 作用 | 是否入库 |
|---|---|---|---|
| `PYTHON/index.html` | 2.21 MB | **实际部署的单文件站点**（`/dp-study-site/PYTHON/`） | 已入库 |
| `PYTHON/python-mastery/` | 1.3 MB（chapters 独占） | 源码：40 章 markdown + 构建器 + 资源 | 55 个文件已入库 |
| `PYTHON/verify/` | — | **真实可运行的参考实现**（TaskForge 完整 / StudyHub 部分） | 32 个文件已入库 |
| `PYTHON/verify-venv/` | 234 MB | 验证用虚拟环境（pygame/mypy/ruff） | 未入库（已 ignore） |

源码实际是**入库的**：`.gitignore` 虽列了 `PYTHON/python-mastery/`、`PYTHON/verify/`、`PYTHON/verify-venv/`，
但前两者是在 ignore 之前就被 add 的，git 对已跟踪文件不再应用 ignore，所以 55 + 32 个源文件有版本历史。
只有 234 MB 的 venv 被正确排除。

### 1.2 构建系统（`build.py`，17 KB，零第三方依赖）

单一职责：把 `chapters/*.md` 编成**一个自包含 HTML**（离线双击可开，无需服务器）。

- 占位符注入：`/*__STYLE__*/`、`/*__DATA__*/`、`/*__SCRIPT__*/`、`__NAV__`、`__CONTENT__`、`__PART_NAMES__`
- 自研 markdown 子集转换器：标题 `##`–`####`、代码围栏（带语言 + Copy 按钮）、表格、
  列表（含 `- [ ]` 任务勾选）、引用、`---`、图片 `![alt](figures/x.svg)`
- **8 种 callout**：`note / tip / warning / danger / pitfall / scenario / solution / try`
- 图形内联：SVG 直接内联（清晰、体积小），PNG/JPG 转 base64（用于真实运行截图）
- 排序：`(part, chapter)`；自动生成上一章/下一章翻页、右侧 TOC（从 h2/h3 抽取）
- front matter 键：`chapter / part / title / summary / minutes / tags`

### 1.3 内容结构：7 个 Part，40 章，3 个项目

| Part | 章节 | 内容 |
|---|---|---|
| 0 Start Here | 0 | 如何使用本书、三条规则 |
| I Foundations | 1–10 | 变量/字符串/控制流/函数/集合/推导式/文件/异常/模块/测试 |
| II Leveling Up | 11–17 | 调试、OOP I/II、迭代器生成器、装饰器、类型注解、文本时间数字 |
| III Real-World | 18–23 | HTTP/API、CSV+SQLite+SQLAlchemy、自动化 CLI、并发、Git 质量、**PROJECT: TaskForge** |
| IV Track A 全栈 Web | 24–30 | Web 原理、HTML/CSS/JS、FastAPI I/II、模板+HTMX+WebSocket、部署、**CAPSTONE A: StudyHub** |
| V Track B 游戏 | 31–36 | Pygame I/II、游戏架构、地图生成、AI 与敌人、**CAPSTONE B: Neon Dungeon** |
| VI Appendices | 37–39 | 场景 Cookbook、练习题、下一步 |

**三大项目**（正是你说的"一游戏 + 一网站 + 从零到综合"）：

| 项目 | 章节 | 形态 | 技术栈 |
|---|---|---|---|
| TaskForge | 23 | 可用 CLI 产品 | SQLAlchemy + Typer + pytest + 分层架构 |
| StudyHub | 30 | **全栈网站**（多用户间隔重复学习平台） | FastAPI + SQLAlchemy 2.x + HTMX + Alembic + Docker |
| Neon Dungeon | 36 | **完整游戏**（roguelike） | Pygame + 程序化地图 + 3 种敌人 AI + 2 个 Boss + PyInstaller 打包 |

### 1.4 规模实测

| 章节 | 词数 | 代码块数 |
|---|---|---|
| 04 Control Flow（普通章） | 3,088 | — |
| 23 TaskForge（项目） | 7,376 | 31 |
| 30 StudyHub（网站 capstone） | 10,441 | 51 |
| 31 Pygame I（普通章） | 3,744 | — |
| 36 Neon Dungeon（游戏 capstone） | **12,665** | **55** |

- chapters 目录 1.3 MB → 构建产物 2.21 MB
- 按 STYLE.md 规定每章 900–1600 词正文（项目章远超），**全书估算 12–16 万词**（该数字为估算）

### 1.5 阅读器功能（`app.js` 272 行 + `style.css` 284 行）

hash 路由 `#/slug`、全文搜索（`/` 聚焦）、进度条、明暗主题、每章 TOC、
"标记本章完成"、代码 Copy、`localStorage` key = **`python-mastery-v1`**、
折叠导航、面包屑（Part + 章号）。

### 1.6 与 Hub 的接线（根目录 `index.html`）

4 处硬编码引用 `PYTHON/`：
1. 顶部按钮 `<a class="btn btn--platform-python" href="PYTHON/">Python Mastery</a>`
2. 平台卡片 `platform-card--python`
3. "建议学习流"文案中的一个环节
4. 站点地图节点 + 页脚 `<li>`

### 1.7 部署模型 + 两个必须先修的问题

**问题 A — 构建不可复现（已确认的漂移）**
部署中的 `PYTHON/index.html` 被**手工改过**：内含两个 `.tb-site` 链接
（`../index.html` "Back to DP Learning" 和 `../qbank/` "Open the Question Bank"）以及对应 CSS，
而这三者**在 `template.html`、`assets/style.css`、`dist/index.html` 里都不存在**。
后果：现在重跑 `build.py` 会把这两个返回 Hub 的入口**丢掉**。
→ 在把它复制到其余 6 个赛道之前，必须先把这两个链接做回模板里，否则同一个漂移会被复制成 7 份。

**问题 B — 体积**
单个语言 2.2 MB。§4.1 共 **7 个完整赛道**（含 Python），若合成一个 HTML 约 **15.5 MB+**，单文件方案不可行。
→ 必须是**每种语言一个单文件书 + 一个平台首页**，不能合成一本。

---

## 二、目标架构

```
code/                        ← 新平台根目录（部署于 /dp-study-site/code/）
├── index.html               ← 平台首页：语言选择器 + 总进度 + 入口
├── _build/                  ← 共用构建系统（由 python-mastery/build.py 泛化而来）
│   ├── build.py             ← `python3 build.py` 构建全部；`python3 build.py python` 只构建一个
│   ├── template.html        ← 书页外壳（含三个返回链接：DP Hub / Question Bank / 平台首页）
│   ├── assets/style.css
│   ├── assets/app.js
│   └── languages.json       ← 语言注册表：id / 名称 / 口号 / 副标题 / kind / status / store / order
├── _shared/                 ← 跨语言通用章节素材（Git、调试、HTTP 原理、算法…）
├── python/                  ← 现有 python-mastery 整体迁入（内容一字不动）
├── java/
├── cpp/
├── csharp/  javascript/  go/  rust/   ← 后续语种
├── capstone/                ← 跨语言终极项目（独立一本书）
└── verify/<lang>/           ← 每种语言的真实参考实现（沿用现有 verify 机制）
```

**关键设计点**

| 决策 | 选择 | 理由 |
|---|---|---|
| 产物形态 | 每语言一个自包含 HTML + 一个平台首页 | 单个 13 MB 文件不可行（问题 B） |
| 进度存储 | 每语言 `code-mastery-<lang>-v1`；平台首页聚合 | 沿用现有 localStorage 机制；Python 保留旧 key 不丢进度 |
| 构建 | 一个泛化 `build.py`，位置参数驱动（`build.py <lang-id>`） | 避免 7 份构建器各自漂移 |
| 共享素材 | `_shared/` 提供跨语言复用章节 | Git/HTTP/调试等不随语言变，不重复写 6 遍 |
| 图形 | 沿用 SVG 内联 + PNG base64 | 已验证可用 |

---

## 三、每语言赛道模板（"结构相同或相似，由语言特性决定细节"）

通用骨架 = Python 现有骨架泛化：

```
Part 0  开始之前：本书用法 + 该语言工具链安装（SDK/编译器/包管理/IDE）
Part I  基础：类型、控制流、函数、集合、错误、文件 I/O、模块
Part II 进阶：该语言核心范式（见下表）、单元测试、构建系统、包管理
Part III 实战：并发、HTTP/API、数据持久化、CLI 工具、打包发布 → 【项目 1：实用强大应用】
Part IV Track A 全栈 Web → 【项目 2：完整网站】
Part V  Track B 游戏开发 → 【项目 3：完整游戏】
Part VI 附录：Cookbook、练习、下一步
```

**每语言的核心范式与项目栈映射**

| 语言 | 工具链（Part 0/II） | 核心范式章节（Python 无对应，必须新写） | Web 栈（项目 2） | 游戏栈（项目 3） | 测试 |
|---|---|---|---|---|---|
| **Python** | 已有，不动 | 已有（装饰器/生成器/类型注解） | FastAPI + HTMX | Pygame | pytest |
| **Java** | JDK + Maven/Gradle + JUnit | 接口/泛型/异常体系/集合框架/Stream/虚拟线程/JVM 内存 | Spring Boot + Thymeleaf/HTMX + JPA | LibGDX 或 JavaFX | JUnit 5 |
| **C++** | 编译器 + CMake + vcpkg/Conan | **RAII / 智能指针 / 移动语义 / 模板 / STL / 内存与 UB** | Drogon 或 Crow + 模板引擎 | SDL2 或 Raylib | Catch2 / GoogleTest |
| **C#** | .NET SDK + NuGet | LINQ / 委托事件 / async-await / 属性 | ASP.NET Core + Razor/Blazor | Unity 或 MonoGame | xUnit |
| **JS/TS** | Node + npm/pnpm + TS | 原型/闭包/**事件循环**/Promise-async/模块系统 | Express/Nest 或 Next.js + React | Canvas / Phaser | Vitest |
| **Go** | Go modules | **goroutine/channel/select**、接口即契约、错误处理 | net/http 或 Gin + templ | Ebiten | go test |
| **Rust** | Cargo | **所有权/借用/生命周期**、trait、Result | Axum 或 Actix + Askama | Bevy | cargo test |

要点：Python 的"装饰器"这类章节不可直译到 C++；C++ 必须新增"内存/UB/RAII"，
Rust 必须新增"所有权/借用"，Go 必须新增"goroutine/channel"。
**结构相同，章节内容由语言特性决定** —— 这正是你要求的。

---

## 四、语言席位（最终名单 v2）

调整已确认：**C 与 C++ 合并为一个 section**；**Kotlin 作为 Java section 的扩展模块**；
其余语言降级为 **mini-section（迷你赛道）**。

### 4.1 完整赛道 —— 7 个 section

| # | Section | 内含 | 网站栈（项目） | 游戏栈（项目） |
|---|---|---|---|---|
| 1 | **Python** | 现有 40 章原样迁入 | FastAPI + HTMX（StudyHub） | Pygame（Neon Dungeon） |
| 2 | **C / C++** | C 打底 → C++ 现代层（同一 section） | Drogon / Crow（C++ Web） | SDL2 / Raylib（C++ 游戏） |
| 3 | **Java**（+ Kotlin 扩展） | Java 主线 + Kotlin 扩展模块 | Spring Boot + JPA | LibGDX / JavaFX |
| 4 | **JavaScript / TypeScript** | JS 基础 → TS 工程化 | Next.js / NestJS | Canvas / Phaser |
| 5 | **C#** | .NET 全栈 | ASP.NET Core | Unity / MonoGame |
| 6 | **Go** | 语法小、并发强 | Gin + templ | Ebiten |
| 7 | **Rust** | 所有权/借用/生命周期 | Axum / Actix | Bevy |

### 4.2 迷你赛道 —— 7 个 mini-section

**定义**：约 **10–14 章**，压缩为"基础 → 该语言独门特性 → 1 个主项目"，
主项目放在**该语言最强的领域**（不硬凑"游戏+网站"双项目——PHP 写游戏、R 写游戏都是装样子）。

| # | mini-section | 主项目方向 | 栈 |
|---|---|---|---|
| 8 | **Swift** | iOS / macOS 原生 App | SwiftUI + Xcode |
| 9 | **PHP** | Web 应用 | Laravel + MySQL |
| 10 | **Ruby** | Web 应用 | Rails + Hotwire |
| 11 | **Scala** | 数据 / 后端服务 | Scala 3 + Spark 或 Play |
| 12 | **Dart** | 跨平台 App（含小游戏） | Flutter |
| 13 | **Lua** | 游戏脚本 / 嵌入式脚本 | Love2D + C 宿主嵌入 |
| 14 | **R** | 数据科学与可视化 | tidyverse + Shiny |

### 4.3 不做赛道，仅作为章节覆盖

| 语言 | 处理方式 |
|---|---|
| SQL | 每门语言的"数据持久化"章内讲（Python 现有 ch19 即如此） |
| Bash / Shell | 自动化与 CLI 章内讲 |
| HTML / CSS | 各语言 Track A 的"前端基础"章内讲（Python 现有 ch25） |

---

### 4.4 C / C++ 合并赛道的结构（怎么排才不乱）

C 是 C++ 的地基，同一 section 内**先 C 后 C++**，这样"为什么要 RAII / 智能指针"才有说服力：

| Part | 内容 |
|---|---|
| 0 | 工具链：gcc/clang、Make/CMake、gdb/lldb、sanitizer、Valgrind |
| I | **C 基础**：类型、指针与数组、**手动内存管理**、结构体、编译单元与头文件、字符串、文件 I/O |
| II | **C 进阶**：函数指针、位运算、预处理器、静态/动态库、Makefile |
| III | **【项目 1】C 系统项目**：一个有实际用途的底层程序（如 shell / 内存分配器 / 简易数据库 / 静态 HTTP 服务器）——体现"理解机器" |
| IV | **过渡到 C++**：为什么需要 C++、RAII、引用与移动语义、智能指针、类与继承、模板、STL、异常 |
| V | **Track A 网站** → 【项目 2】C++ Web 服务 |
| VI | **Track B 游戏** → 【项目 3】C++ 游戏 |
| VII | 附录：C/C++ 互操作、现代 C++20/23、性能与排错、下一步 |

### 4.5 Java + Kotlin 的结构

Java 走完整主线（Part 0–VI，含 Spring Boot 网站 + LibGDX 游戏），
**Kotlin 作为该 section 末尾的扩展模块**（不是独立赛道）：

- 与 Java 的语法差异、空安全（nullable 类型）、data class、扩展函数、协程
- 与 Java 的互操作（同一个 JVM 项目里混写）
- 一个 Kotlin 小项目（Ktor 后端 或 Android 入门）

### 4.6 排产建议

> **先用 1 个 section（C/C++，见决策 2B）跑通整条赛道**，再批量复制 —— 否则模板缺陷会复制到所有 section。
> 7 个完整赛道 ≈ 7 倍于现有 Python 的体量；建议顺序：**C/C++ → Java(+Kotlin) → TS → C# → Go → Rust**，
> 迷你赛道插在完整赛道之间当"调剂"，不并行开工。
> 顺序由决策 **2B** 决定：C++ 的范式差异最大，最能压测模板，所以它排第一。

---

## 五、跨语言终极项目（Capstone）

要求：多种语言协作、全栈、够复杂、可商用、耗时数月以上。

### 方案 A —「Nebula Arena」商业级多人在线对战游戏平台 ⭐推荐

| 层 | 语言 | 为什么必须是它 |
|---|---|---|
| 游戏引擎核心（物理/碰撞/寻路） | **C++**（同时编译到 WASM 给浏览器复用） | 性能敏感；同一份核心前后端共用 |
| 实时权威服务器（房间/帧同步/反作弊网关） | **Go** | goroutine 天然适合海量并发长连接 |
| 账号 / 计费 / 商城 / 订单（含真实支付） | **Java** Spring Boot | 企业级事务与生态最成熟 |
| 数据分析 / 匹配推荐 / 外挂检测 | **Python** | ML 与数据生态 |
| 前端（WebGL 客户端 + 管理后台） | **TypeScript** | 浏览器唯一选择 |
| 基础设施 | Postgres + Redis + Docker + CI/CD + K8s | 商用标配 |

**为什么推荐**：性能层、并发层、业务层、数据层各自有不可替代的语言优势 ——
多语言是**被需求逼出来的**，不是为用而用。天然耗时数月，且是真正可运营的商业产品。

### 方案 B —「Orbit Commerce」商业级全栈电商/SaaS 平台

网站向：多租户店铺、库存与订单、支付清算、实时推荐、运营看板。
语言分工：TS 前端 + Java 交易核心 + Go 高并发网关 + Python 推荐与分析 + （可选）C++ 搜索/图像处理。

### 方案 C —「StudyVerse」把本站产品化

学习 SaaS：题库 + 实时对战答题 + 订阅计费 + AI 助教 + 数据分析。
优势：与你现有 DP 学习站生态直接呼应，做完即可自用；劣势：与你已有项目重叠，商用想象空间略小。

| 方案 | 多语言合理性 | 商业想象 | 与你现有项目协同 | 工作量 |
|---|---|---|---|---|
| A 游戏平台 | ★★★★★（天然） | ★★★★★ | ★★☆ | 最大 |
| B 电商 SaaS | ★★★★☆ | ★★★★★ | ★★☆ | 大 |
| C 学习 SaaS | ★★★☆☆ | ★★★☆☆ | ★★★★★ | 大 |

---

## 六、分阶段路线图

> 本节与 §0 **共用同一套阶段编号（P0–P5）**：§0 记"现在到哪了"，本节记"每阶段要交出什么、依赖什么"。

| 阶段 | 内容 | 产出 | 前置 |
|---|---|---|---|
| **P0 地基** | 泛化 `build.py`（位置参数 + `languages.json` 注册表）、把两个返回链接做回模板（修问题 A）、建 `code/` 骨架与平台首页 | 可复现的多语言构建器 | 拍板目录方案 |
| **P1 迁移** | Python 原样迁入 `code/python/`（`git mv` 保历史）、Hub 接线、`PYTHON/` 跳转页、搜索索引重建 | Python 成为子栏目，URL 稳定 | P0 |
| **P2 模板验证** | 用 **C/C++**（决策 2B）跑完整条赛道：Part 0–VII 全章 + 3 个项目 + verify 参考实现 + 两条项目构建 | 证明模板通用；暴露缺陷。**这是闸门** | P1 |
| **P3 扩语种** | Java 主线 + Kotlin 扩展模块（同一个 section） | 每语言一本 | P2 通过 |
| **P4 扩语种** | TypeScript / C# / Go / Rust + 7 个迷你赛道 | 每语言一本 | P3 |
| **P5 终极项目** | 跨语言 capstone（方案 A/B/C）独立成书 + 真实可运行仓库 | 商用级全栈项目 | 至少 3 个语言赛道完成 |

> **P2 是唯一的闸门。** 7 个完整赛道 ≈ 280 章 + 21 个项目构建；真正的风险不是工作量，
> 而是**模板缺陷被放大 7 倍** —— 这正是问题 A 已经犯过一次的错。P2 未跑通前不要开第二个赛道。

---

## 七、决策记录（已拍板）

**五项均已决定，不再待议。** 下表保留当时的备选项，便于日后回溯"为什么不选另一条"。

| # | 决策点 | 备选项 | 决定 |
|---|---|---|---|
| 1 | 平台目录/URL | **A.** 新建 `code/`，Python 迁到 `code/python/`<br>**B.** 就地改造 `PYTHON/` 为平台根 | ✅ **1A** — 目录名与内容一致；旧链接用跳转页兜住 |
| 2 | 第二个语言（先跑通模板的） | **A.** Java（对接 IB CS）<br>**B.** C++（范式差异最大，最能压测模板） | ✅ **2B** — 模板缺陷要在最难的地方先暴露 |
| 3 | 终极项目 | **A.** Nebula Arena 游戏平台<br>**B.** Orbit Commerce 电商 SaaS<br>**C.** StudyVerse 学习 SaaS | ✅ **3A** — 多语言是被需求逼出来的，不是为用而用 |
| 4 | 每个新语言的体量 | **A.** 完全对标 Python：40 章 + 3 个项目<br>**B.** 精简版：约 25 章 + 3 个项目 | ✅ **4A** — 先按完整版做；P2 跑通后再评估是否降级 |
| 5 | 旧链接 `PYTHON/` | **A.** 保留 `PYTHON/index.html` 自动跳转页<br>**B.** 直接改 Hub 链接，旧 URL 失效 | ✅ **5A** — 已实现：1.5 KB `meta refresh` + `rel=canonical` |

---

## 八、风险与对策

| 风险 | 影响 | 对策 |
|---|---|---|
| 构建漂移（问题 A）复制到其余赛道 | 返工 | 模板已含返回链接（**问题 A 已修**）；再加一条**幂等检查**：`sh code/_build/check-idempotent.sh` —— 重跑构建必须零字节变化 |
| 单文件体积膨胀 | 加载慢 | 每语言独立文件；平台首页只放索引 |
| 40 章 × 7 个完整赛道 ≈ **280 章**（另加 7 个迷你赛道），再加 21 个项目构建 | 工期不可控 | 先用 1 个语言跑通（P2），再决定全量还是精简（决策 4） |
| `verify/` 参考实现跑不起来（Java/C++ 需 JDK/编译器） | 代码不可信 | 每种语言配一个可复现的 verify 脚本 + 环境说明；本机缺工具链时明确标注"未实机验证" |
| 与并发会话争抢同一仓库 | 提交冲突 | 沿用现有约定：只 add 明确路径，绝不 `git add -A` |
