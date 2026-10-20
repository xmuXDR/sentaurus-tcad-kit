# README for AI Agents（给 AI 看的导读）

你是接手这个技能包的 AI 助手。人类用户可能已经看过 `README.md`；你的操作手册是 `SKILL.md`。本文件帮你 30 秒上手。

## 启动顺序（不要跳步）

1. **先读 `SKILL.md` 全文**（约 200 行）。它是主入口：仿真闭环流程、不可违反的执行规则、何时读哪个 reference。
2. 用户任务涉及某个具体环节时，**按需读 `references/` 对应文件**（preflight / swbpy2-gsub / sde / sdevice / gan-seb / reporting），不要一次性全读。
3. Sentaurus 在远程 Linux 服务器时，所有 shell 命令经 SSH 在远端执行；本机没有 Sentaurus 就不要假装有。

## 不可违反的红线（违反 = 无效交付）

- 仿真必须进 SWB 项目树（新项目 `Deck(path, False)` traditional），**必须用 `gsub -q <队列> -e <节点> <项目>` 提交**
- 禁止直接 `sdevice pp*_des.cmd` 或树外孤立 deck
- 改模型/参数前必须先查官方依据（服务器本地手册索引脚本见下），同类失败最多试两次
- 结束后必须按 log → plt → tdr 分层诊断，并留持久化产物（图/表/报告 + progress/findings 记录）

## 内置脚本速查（scripts/，免安装）

| 任务 | 命令 |
|---|---|
| 解析 .plt 导出曲线 | `python3 scripts/plt_parse.py <file.plt> --keys / --head 5 / --csv out.csv`（多 Data 块自动拆 `_b0/_b1`） |
| 查官方手册 | 先 `bash scripts/build_index.sh`（一次性，在服务器上，把 `$STROOT/tcad/$STRELEASE/manuals/olh_sentaurus/pdf/` 的 PDF 转文本到 `~/manual_index/text/`），然后 `python3 scripts/search.py "关键词" -t sdevice -n 5`，结果带 PDF 页码。多词短语可能因排版断行搜不到，用单词或 `-r` 正则 |
| 记录仿真队列 | `python3 scripts/sim_queue.py add <node> <project> "描述"` / `done` / `fail` / `status`（辅助记录，不替代 SWB 状态） |
| 结构几何 QA | `python3 scripts/extract_material_vertices.py --grd x.grd --target-region R --target-material M --xmin .. --xmax .. --ymin .. --ymax .. --json-out v.json --csv-out p.csv`，再 `python3 scripts/measure_material_features.py --input v.json --json-out f.json --csv-out f.csv`。适合 spacer/侧壁类窄特征；宽大结构结果要人工核对 |

## 和用户协作的约定

- 大任务先建 `task_plan.md` / `progress.md` / `findings.md` 再开工
- 提交仿真前向用户确认：项目路径、节点号、参数值、队列名
- preflight 未通过就停下报阻塞项，**不要把环境/license 问题当物理模型问题修**
- 报告文字用自然中文书面语；数值、单位、节点号必须精确
