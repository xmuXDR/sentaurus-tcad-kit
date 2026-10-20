# 第三方代码归属（NOTICE）

本 skill 基于并包含以下 MIT 协议开源项目的代码或衍生代码，版权归原作者所有：

1. **claude-sentaurus-skill**（作者：starlight-w）
   - 来源：https://github.com/starlight-w/claude-sentaurus-skill
   - 用于：SKILL.md 主体工作流与 references/ 文档体系（经改造适配 Kimi Work）

2. **sprocess-geometry-feature-extractor**（作者：ltj3000）
   - 来源：https://github.com/ltj3000/sprocess-geometry-feature-extractor
   - 用于：`scripts/extract_material_vertices.py`、`scripts/measure_material_features.py`（含一处上游 bug 修复：元素行 0 边ID 过滤）

以下脚本为本 skill 作者自研：

- `scripts/plt_parse.py`（.plt 解析器，设计参考了 pytaurus 的思路但为独立实现）
- `scripts/sim_queue.py`（仿真队列记录）
- `scripts/build_index.sh`、`scripts/search.py`（官方手册本地全文索引）

本仓库不包含任何 Synopsys 专有资料（软件、license、官方手册 PDF、Applications Library）。使用者须自行拥有合法的 Sentaurus 授权。
