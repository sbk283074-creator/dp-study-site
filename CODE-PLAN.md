# CODE 平台改造计划 — 把 Python Mastery 升级为多语言编程平台

> 状态：**已开工**。决策已拍板（1A / 2B / 3A / 4A / 5A），**P0 地基 + P1 迁移已完成**。
> 调研日期：2026-09-19。所有数字为本机实测，非估算（估算已单独标注）。

### 0. 进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| **P0** | `code/` 骨架 + 泛化构建器（`_build/`，`--lang` + `languages.json` 注册表）+ 平台首页 | ✅ 完成 |
| **P1** | Python 迁入 `code/python`（`git mv`，历史保留）+ Hub 接线 + `PYTHON/` 跳转页 + 搜索索引重建 | ✅ 完成 |
| **P2** | C/C++ 赛道骨架 + 前几章 | ⬜ 未开始 |
| **P3** | Java (+Kotlin) 赛道 | ⬜ 未开始 |
| **P4** | TypeScript / C# / Go / Rust 赛道 + 迷你赛道 | ⬜ 未开始 |
| **P5** | 终极项目 Nebula Arena（全栈多语言） | ⬜ 未开始 |

新增语言的标准操作：建 `code/<lang>/`（`chapters/` + `parts.json`）→ 在 `_build/languages.json`
注册 → `cd code/_build && python3 build.py`。构建器无需改动。

---

## 一、现状调研：Python Mastery 解剖

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
→ 在把它复制成 6 种语言之前，必须先把这两个链接做回模板里，否则漂移会被放大 6 倍。

**问题 B — 体积**
单个语言 2.2 MB。若把 6 种语言塞进一个 HTML，约 13 MB+，单文件方案不可行。
→ 必须是**每种语言一个单文件书 + 一个平台首页**，不能合成一本。

---

## 二、目标架构

```
code/                        ← 新平台根目录（部署于 /dp-study-site/code/）
├── index.html               ← 平台首页：语言选择器 + 总进度 + 入口
├── _build/                  ← 共用构建系统（由 python-mastery/build.py 泛化而来）
│   ├── build.py             ← 支持 --lang；或 build.py --all
│   ├── template.html        ← 书页外壳（含返回 Hub / 返回平台 两个链接，修复问题 A）
│   ├── assets/style.css
│   ├── assets/app.js
│   └── languages.yaml       ← 语言注册表：id / 名称 / 口号 / 副标题 / 顺序 / 状态
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
| 构建 | 一个泛化 `build.py`，`--lang` 参数驱动 | 避免 6 份构建器各自漂移 |
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

> **先用 1 个 section（Java 或 C/C++）跑通整条赛道**，再批量复制 —— 否则模板缺陷会复制到所有 section。
> 7 个完整赛道 ≈ 7 倍于现有 Python 的体量；建议顺序：Java → C/C++ → TS → C# → Go → Rust，
> 迷你赛道插在完整赛道之间当"调剂"，不并行开工。

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

| 阶段 | 内容 | 产出 | 前置 |
|---|---|---|---|
| **P0 地基** | 泛化 `build.py`（多语言 + `languages.yaml`）、把两个返回链接做回模板（修问题 A）、建 `code/` 骨架 | 可复现的多语言构建器 | 拍板目录方案 |
| **P1 迁移** | Python 原样迁入 `code/python/`，构建验证与线上逐字节比对 | Python 成为子栏目，URL 稳定 | P0 |
| **P2 模板验证** | 用 **1 个新语言**（Java 或 C++）跑完整条赛道，含 3 个项目 + verify 实现 | 证明模板通用；暴露缺陷 | P1 |
| **P3 扩语种** | 按优先级批量产出其余语言 | 每语言一本 | P2 通过 |
| **P4 终极项目** | 跨语言 capstone（方案 A/B/C）独立成书 + 真实可运行仓库 | 商用级全栈项目 | 至少 3 个语言赛道完成 |

---

## 七、需要你拍板的决策

| # | 决策点 | 选项 |
|---|---|---|
| 1 | 平台目录/URL | **A.** 新建 `code/`，Python 迁到 `code/python/`（干净，但 `PYTHON/` 旧链接需处理）<br>**B.** 直接把 `PYTHON/` 就地改造成平台根（URL 不变，但目录名与内容不符） |
| 2 | 第二个语言（先跑通模板的） | **A.** Java（对接 IB CS）<br>**B.** C++（范式差异最大，最能压测模板） |
| 3 | 终极项目 | **A.** Nebula Arena 游戏平台（推荐）<br>**B.** Orbit Commerce 电商 SaaS<br>**C.** StudyVerse 学习 SaaS |
| 4 | 每个新语言的体量 | **A.** 完全对标 Python：40 章 + 3 个项目（最完整，最耗时）<br>**B.** 精简版：约 25 章 + 3 个项目（保留"零基础→游戏+网站"主线） |
| 5 | 旧链接 `PYTHON/` | **A.** 保留一个 `PYTHON/index.html` 自动跳转页<br>**B.** 直接改 Hub 链接，旧 URL 失效 |

---

## 八、风险与对策

| 风险 | 影响 | 对策 |
|---|---|---|
| 构建漂移（问题 A）复制到 6 个语言 | 返工 | P0 先把返回链接做进模板，并加一条"dist 与部署文件必须逐字节一致"的检查 |
| 单文件体积膨胀 | 加载慢 | 每语言独立文件；平台首页只放索引 |
| 40 章 × 6 语言 = 巨量写作 | 工期不可控 | 先用 1 个语言跑通（P2），再决定全量还是精简（决策 4） |
| `verify/` 参考实现跑不起来（Java/C++ 需 JDK/编译器） | 代码不可信 | 每种语言配一个可复现的 verify 脚本 + 环境说明；本机缺工具链时明确标注"未实机验证" |
| 与并发会话争抢同一仓库 | 提交冲突 | 沿用现有约定：只 add 明确路径，绝不 `git add -A` |
