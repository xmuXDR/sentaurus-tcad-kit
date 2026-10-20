# sentaurus-tcad-kit

面向 AI 助手的 Synopsys Sentaurus TCAD 仿真全流程技能包：让 AI 帮你做器件/工艺仿真时，**先查资料再仿真、全程 SWB 可见、结果可复现可追溯**，并自带一组免安装的实用脚本。

> **注意**：本包不含 Sentaurus 软件。使用者必须自行拥有合法的 Synopsys Sentaurus 许可和可用的仿真环境（通常在 Linux 服务器上）。

## 它能帮你做什么

| 场景 | 能力 |
|---|---|
| 新建/修复仿真项目 | 强制走 SWB Workbench 项目树（swbpy2 建 traditional 项目），禁止绕过状态管理 |
| 跑仿真 | 强制 `gsub` 提交 + 后台监控，禁止直接跑 `sdevice`；并发默认 ≤3 |
| 收敛失败/异常漏电/击穿定位 | log → plt → tdr 四层分层诊断流程，两次失败规则防盲试 |
| GaN/p-GaN HEMT、SiC IGBT、BV、HeavyIon/SEB | 内置经官方例子对齐的物理模型与参数经验（极化 Activation、buffer trap、eAvalanche、SEB 判据等） |
| 查手册 | 自带脚本把**你自己服务器上的官方 PDF 手册**转纯文本，秒级全文检索、带页码（不存在第三方手册站的版本偏差） |
| 处理结果 | `.plt` 一键解析导出 CSV（支持多段曲线），自动批量出出版级图 |
| 工艺结构质检 | 从 sprocess `.grd` 提取材料边界、自动量测突起/凹陷 |
| 任务管理 | 仿真队列记录（提交/完成/失败/状态），跨对话可追溯 |

## 快速开始（Kimi Work / Claude Code 等）

**方式 A（推荐）**：把整个文件夹复制为技能

- Kimi Work：复制到 `~/.kimi/daimon/skills/sentaurus-tcad-kit/`，或项目级 `.agents/skills/sentaurus-tcad-kit/`
- Claude Code：`cp -r` 到 `~/.claude/skills/sentaurus-tcad-kit/`

然后直接说："**用 sentaurus-tcad-kit 帮我……**"（例如"帮我从零建一个 p-GaN HEMT 项目跑 IdVg 和 BV"、"诊断 BV 在 720V 的 Step-size is too small"）。

**方式 B**：无技能机制的环境，把 `SKILL.md` 和 `references/` 作为系统提示/知识库喂给 AI，需要细节时让它读对应 reference 文件。

## 首次使用前的体检

新机器/新服务器第一次用，先让 AI 做 preflight（环境变量、license、swbpy2、队列、可视化、手册路径），**通过后再写 deck**。对 AI 说：

> 用 sentaurus-tcad-kit 先检查这台机器能不能跑 Sentaurus 仿真，不要直接写 deck 或提交 gsub。

## 目录结构

```
sentaurus-tcad-kit/
├── SKILL.md            # AI 主入口：流程、红线、何时读哪个 reference
├── README.md           # 本文件（给用户看）
├── README_FOR_AI.md    # 给 AI 的导读
├── LICENSE             # MIT
├── NOTICE.md           # 上游代码署名
├── references/         # 分层细节文档（按需读取）
│   ├── new-device-preflight.md    # 新机器环境体检
│   ├── swbpy2-gsub.md             # SWB 项目树 / swbpy2 / gsub / 监控
│   ├── sde-mesh-patterns.md       # SDE 几何/掺杂/接触/网格
│   ├── sdevice-patterns.md        # SDevice Physics/Math/Solve/Plot
│   ├── gan-hemt-and-seb.md        # GaN/p-GaN HEMT、BV、HeavyIon/SEB
│   └── results-reporting.md       # 可视化/出图/报告模板
└── scripts/            # 免安装脚本（python3 / bash）
    ├── plt_parse.py                    # .plt → CSV/预览（纯标准库）
    ├── sim_queue.py                    # 仿真队列记录
    ├── build_index.sh + search.py      # 官方手册本地全文索引
    └── extract_material_vertices.py
        + measure_material_features.py  # sprocess 几何质检
```

## 推荐搭配（可选）

- **VSCode 扩展 "Sentaurus TCAD Syntax"**（Marketplace 搜 `onegayi.sentaurus-tcad-syntax`）：deck 语法高亮 + 中英文悬停文档 + 自动补全，写 cmd 基本不用翻手册

## 来源与许可

- MIT License，详见 `LICENSE`；上游代码署名见 `NOTICE.md`
- 基于 starlight-w/claude-sentaurus-skill（MIT）改造，几何质检脚本来自 ltj3000/sprocess-geometry-feature-extractor（MIT，含一处 bug 修复）
- 本包不包含任何 Synopsys 专有资料
