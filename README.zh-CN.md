# GeneFam-Pipeline 中文说明

GeneFam-Pipeline 是一个面向植物大范围、多物种基因家族分析的流程项目。目标是把一个包含很多物种的本地物种库，通过 YAML 配置选择本次要分析的物种，然后完成基因家族成员鉴定、结构与进化分析、可视化和报告输出。

当前流程优先使用：

- Nextflow DSL2 作为流程引擎
- YAML 作为参数配置入口
- Conda 环境名：`GeneFamilyFlow`
- R 路径：`/usr/local/bin/R`
- Python 脚本负责表格、FASTA、GFF3 等稳定格式转换
- R 脚本负责画图

## 现在能做什么

目前已经开发并测试过的能力包括：

- 从物种库中按物种名选择本次分析对象
- HMMER / DIAMOND 证据输入规划
- HMMER 结构域结果过滤
- 基因家族候选成员合并
- 多物种 copy number 汇总
- 家族成员蛋白序列提取
- MAFFT 多序列比对
- FastTree 快速构树，适合多物种大基因家族
- IQ-TREE 分支保留，适合更慢但更完整的模型选择或 bootstrap 分析
- MEME motif 结果解析与统计
- gene structure 统计
- chromosome location 提取
- promoter 提取与统计
- MCScanX `.collinearity` 结果解析
- MCScanX + `circlize` 共线性圆图可视化
- Ka/Ks 结果解析
- WGD layer 与 gamma / beta / alpha / theta 这类命名事件解释
- duplicate retention enrichment
- RNA-seq 表达矩阵整合
- 结果汇总表、PDF/PNG 图和 Markdown 报告

需要注意：Docker / Apptainer 封装材料已经有了，但这台机器当前还没有完成 Docker / Apptainer 运行时验证。所以现在的重点仍然是先把分析流程跑通，最后再封装容器。

## 输入数据怎么放

推荐使用一个大的物种库，每个物种一个文件夹，文件夹名就是物种名：

```text
data/species_bank/
  Arabidopsis_thaliana/
    Arabidopsis_thaliana.pep.fa
    Arabidopsis_thaliana.cds.fa
    Arabidopsis_thaliana.genome.fa
    Arabidopsis_thaliana.gff3
  Brassica_rapa/
    Brassica_rapa.pep.fa
    Brassica_rapa.cds.fa
    Brassica_rapa.genome.fa
    Brassica_rapa.gff3
  Capsella_rubella/
    Capsella_rubella.pep.fa
    Capsella_rubella.cds.fa
    Capsella_rubella.genome.fa
    Capsella_rubella.gff3
```

最基础分析至少需要：

- `pep`：蛋白质序列，用于 HMMER / DIAMOND / 构树
- `gff3`：基因注释，用于 gene structure、chromosome location

进阶模块还需要：

- `genome`：基因组序列，用于 promoter 提取
- `cds`：CDS 序列，用于 Ka/Ks
- expression matrix：表达谱整合
- MCScanX / KaKs 结果表：WGD、共线性、选择压力分析

## 配置文件怎么写

分析通过 YAML 文件控制。可以复制 `configs/example.config.yaml`，比如新建：

```bash
cp configs/example.config.yaml configs/my_3species.yaml
```

然后重点改这些地方：

```yaml
project:
  name: My_gene_family
  outdir: results/My_gene_family

input:
  mode: auto
  root: data/species_bank
  required:
    pep: true
    gff3: true
    cds: false
    genome: true

species:
  include:
    - Arabidopsis_thaliana
    - Brassica_rapa
    - Capsella_rubella
  exclude: []

gene_family:
  name: GDSL
  hmm_profiles:
    - id: PF00657
      path: data/hmm_profiles/PF00657.hmm
  reference_peptides: data/reference/GDSL_reference.pep.fa
```

第一轮真实试跑，建议先开这些模块：

```yaml
modules:
  identification: true
  domain_filtering: true
  family_summary: true
  phylogeny: true
  motif: false
  synteny: false
  duplication_retention: false
  kaks: false
  chromosome_location: true
  expression: false
  report: true
```

为什么第一轮不建议全开？因为第一次真实数据最容易出问题的是路径、物种名、GFF3 gene ID、HMM profile 和 reference peptide。先把主线跑通，再逐步加 promoter、motif、expression、MCScanX、Ka/Ks 和 WGD 解释，会更稳。

## 跑前检查是干什么的

正式跑之前，先做配置体检：

```bash
python bin/genefam/validate_config.py configs/my_3species.yaml --check-paths
```

它不会真正分析数据，只检查：

- YAML 是否能读
- `input.root` 是否存在
- 你选择的物种能不能找到
- 每个物种是否有必须的 `pep` / `gff3` / `genome` / `cds`
- HMM profile 是否存在
- DIAMOND reference peptide 是否存在
- 模块依赖是否合理
- expression matrix、WGD event map 等路径是否存在

通过时会显示：

```text
Configuration OK
```

如果失败，会直接告诉你缺哪个路径或哪个模块配置不合理。这个步骤的作用是避免 Nextflow 跑了很久之后才因为一个文件路径写错而失败。

## 真实 3 物种第一轮测试

你现在准备好的物种库可以直接作为第一轮真实测试输入：

```text
data/species_bank/
  Arabidopsis_thaliana/
    Arabidopsis_thaliana.pep.fa
    Arabidopsis_thaliana.genome.fa
    Arabidopsis_thaliana.cds.fa
    Arabidopsis_thaliana.gff3
  Brassica_rapa/
    Brassica_rapa.pep.fa
    Brassica_rapa.genome.fa
    Brassica_rapa.cds.fa
    Brassica_rapa.gff3
  Capsella_rubella/
    Capsella_rubella.pep.fa
    Capsella_rubella.genome.fa
    Capsella_rubella.cds.fa
    Capsella_rubella.gff3
```

建议真实物种库统一使用 `.pep.fa` 命名；模板也保留了 `.protein.fa` 兼容模式。下一步先复制真实测试模板：

```bash
cp configs/real_3species.template.yaml configs/my_3species.yaml
```

然后先确认这两个真实输入文件已经准备好，并按你的基因家族改掉路径：

```text
data/hmm_profiles/PF00657.hmm
data/reference/GDSL_reference.pep.fa
```

如果你已经有 TAIR 的 `all.domains.txt`，建议放在这里：

```text
data/domain_annotations/all.domains.txt
```

这个文件不是最终的 DIAMOND reference FASTA，而是 TAIR 已有 domain 注释索引。它在 Reference 流程里的核心用法是：

```bash
grep 'PF00657' all.domains.txt|awk -F '.' '{print $1}'|sort|uniq > PF00657.TAIR.ID
seqkit grep -r -f PF00657.TAIR.ID AT.clean.pep.fasta -o PF00657.TAIR.ID.fa
```

也就是说，先从 `all.domains.txt` 里筛出包含 `PF00657` 的拟南芥 TAIR gene ID，再从拟南芥蛋白 FASTA 中提取这些序列，生成 `data/reference/GDSL_reference.pep.fa`。这个生成出的 FASTA 才是后续 DIAMOND/BLAST 使用的 reference peptide。

模板里已经预留：

```yaml
domain_annotation:
  tair_all_domains: data/domain_annotations/all.domains.txt

reference_generation:
  source: tair_all_domains
  species_id: Arabidopsis_thaliana
  peptides: data/species_bank/Arabidopsis_thaliana/Arabidopsis_thaliana.pep.fa
  all_domains: data/domain_annotations/all.domains.txt
  domain_terms:
    - PF00657
    - GDSL_lipase/esterase
  output: data/reference/GDSL_reference.pep.fa
  ids_output: data/reference/GDSL_reference.ids.txt
```

生成 reference peptide：

```bash
mkdir -p data/reference
python bin/genefam/build_reference_from_tair_domains.py \
  --domains data/domain_annotations/all.domains.txt \
  --peptides data/species_bank/Arabidopsis_thaliana/Arabidopsis_thaliana.pep.fa \
  --terms PF00657 \
  --out data/reference/GDSL_reference.pep.fa \
  --ids-out data/reference/GDSL_reference.ids.txt \
  --allow-missing \
  --missing-out data/reference/GDSL_reference.missing_ids.txt
```

这个生成的 `GDSL_reference.pep.fa` 才是 `gene_family.reference_peptides` 使用的 DIAMOND query reference。`GDSL_reference.ids.txt` 等价于 Reference 里的 `PF00657.TAIR.ID`；如果 TAIR domain 注释版本和拟南芥 peptide FASTA 版本不完全一致，缺失的 TAIR gene ID 会写入 `GDSL_reference.missing_ids.txt`。`all.domains.txt` 和生成的 reference FASTA 都属于本地输入/派生数据，不要提交到 git。

第一轮建议保持模板里的保守模块组合：打开 identification、domain_filtering、family_summary、phylogeny、chromosome_location 和 report；先不要打开 promoter_cis、ppi、synteny、kaks、duplication_retention。这样可以先确认物种名、GFF3 gene ID、蛋白 ID、HMM profile 和 reference peptide 都能对上。

先做路径体检：

```bash
python bin/genefam/validate_config.py configs/my_3species.yaml --check-paths
```

如果返回 `Configuration OK`，再跑正式标准主线：

```bash
PATH="/Users/liuyue/miniforge3/envs/GeneFamilyFlow/bin:$PATH" \
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  -profile activated \
  --config configs/my_3species.yaml
```

第一轮重点查看：

```text
results/My_3species_GDSL/
```

如果第一轮能生成候选成员表、family members FASTA、FastTree 进化树、chromosome location 和 `final_report.md`，再进入第二轮，逐步打开 promoter、motif、expression、MCScanX/circlize、Ka/Ks/WGD 和论文级可视化模块。

## 本地验收入口

如果你想快速判断当前仓库是不是已经达到 MVP 交付状态，优先运行：

```bash
bash scripts/run_local_acceptance.sh
```

这个脚本会刷新 release gate、quickstart handoff、论文级报告闭环检查和最终交付索引，并生成：

```text
results/local_acceptance/local_acceptance_summary.md
results/publication_report_audit/publication_report_audit.md
results/report_index_audit/standard_report_index_audit.md
results/report_index_audit/wgd_report_index_audit.md
results/reference_visual_alignment/reference_visual_alignment.md
results/delivery_bundle/figure_gallery.tsv
results/delivery_bundle/figure_gallery.md
results/delivery_bundle_smoke/figure_gallery_audit.md
results/delivery_bundle_smoke/delivery_manifest_audit.md
results/delivery_bundle/final_delivery_manifest_audit.md
```

`results/local_acceptance/local_acceptance_summary.md` 是最短的通过/失败/阻塞索引；它会单独列出 release gate、quickstart、publication_report_audit、report-index audit、`figure_gallery_audit`、release-gate 的 `delivery_manifest_audit`、最终交付包的 `final_delivery_manifest_audit` 和 delivery bundle 的状态。

`results/publication_report_audit/publication_report_audit.md` 用来确认最终报告是否真的把图件格式、只精读已注册图件、图件清单与精读表路径一致性、QC、逐图方法/软件版本和复现命令闭环。

`results/report_index_audit/standard_report_index_audit.md` 和 `results/report_index_audit/wgd_report_index_audit.md` 用来检查标准分析分支和 WGD 分支的 report-index 是否把 plot_manifest、software_versions、figure_interpretations、`final_report.md` 和 figure_traceability_matrix 都挂到索引里，并确认所有 available 索引路径都真实存在。

`results/reference_visual_alignment/reference_visual_alignment.md` 是 Reference visual alignment audit 的人工入口；它会检查 `reference_visual_alignment` 交付行，确认标准分支和 WGD 分支的 plot manifest 覆盖论文级图件模块，包括 gene family information、tree+motif+gene structure+domain、MCScanX/synteny/circlize、promoter cis-element、expression heatmap、ggNetView PPI，以及 Ka/Ks/WGD gamma beta alpha theta 图件，并确认对应图件都有逐图精读解释。

`results/delivery_bundle/figure_gallery.tsv` 和 `results/delivery_bundle/figure_gallery.md` 是全局论文图件目录：每一行把标准分析和 WGD 分支的图件 PDF 连接到逐图精读、软件/R 包版本表和最终报告，适合交付时快速定位所有图。

`results/delivery_bundle_smoke/figure_gallery_audit.md` 是全局图件目录的链接检查，确认 figure gallery 里的图件、精读、软件版本、最终报告和 traceability anchor 都能找到，并检查 PDF/PNG/SVG 的全局图件文件签名，避免空壳或损坏图片仅凭路径存在就通过；`results/delivery_bundle_smoke/delivery_manifest_audit.md` 是 release gate 里的交付清单 smoke 检查。`results/delivery_bundle/final_delivery_manifest_audit.md` 是最终用户交付包的路径检查，确认 `results/delivery_bundle/delivery_manifest.tsv` 里 available 和 blocked 的 handoff index 路径都能解析到真实文件或被接受的运行时定位符。

如果当前机器还没有 Docker / Apptainer，`local_acceptance_summary.md` 可能显示 `Overall status: blocked`。这不是说分析流程失败，而是表示分析证据已经达到 release-ready，剩余的是最终容器封装验证。此时优先查看 `final_stage_blocker` 行；当前预期 blocker 是 Docker / Apptainer 运行时验证，对应的解除入口在 `results/readiness/runtime_bootstrap.sh`。

## 论文级报告闭环检查

完整 release 会额外生成：

```text
results/publication_report_audit/publication_report_audit.md
```

这一步检查最终报告是否把每个注册图件都闭环到：

- 每张图的结果精读
- PDF/PNG/SVG 图件格式有效性
- 只允许精读已注册到 plot_manifest 的图件
- 图件清单与精读表 output_path 一致
- QC 表和限制说明
- 方法、软件和 R 包版本
- 逐图方法/软件版本覆盖
- 可复现命令

如果这一步失败，说明图可能已经生成了，但还没有达到“结题报告/论文结果包”的交付标准。

## 第一轮真实分析怎么跑

如果 `GeneFamilyFlow` 环境已经可用，可以跑标准识别分支：

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  -profile activated \
  --config configs/my_3species.yaml \
  --run_identification true \
  --tree_builder fasttree \
  --final_rule intersection
```

建议第一轮使用 `fasttree`，因为它快，适合多物种大基因家族。等结果稳定后，如果你需要更正式的系统发育树，再考虑 `iqtree`。

如果你已经准备好了规范化的 MCScanX syntenic pair 表，也可以在正式标准分支里打开 feature summary 和 MCScanX circlize 图：

```yaml
modules:
  feature_summary: true
  synteny: true
plotting:
  syntenic_pairs: path/to/syntenic_pairs.tsv
```

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  -profile activated \
  --config configs/my_3species.yaml \
  --run_identification true \
  --tree_builder fasttree
```

如果要在正式标准分支里提取启动子，需要每个物种都有 genome FASTA。启动子提取仍可以用 CLI 打开；如果你已经有 PlantCARE 等 cis-element 注释表，则建议直接写进 YAML：

```yaml
modules:
  promoter: true
  promoter_cis: true
promoter:
  cis_elements: path/to/plantcare_cis_elements.tsv
```

```bash
--run_promoter true \
--promoter_upstream_bp 2000 \
--promoter_downstream_bp 0
```

PPI 和表达谱也可以从 YAML 驱动：

```yaml
modules:
  ppi: true
  expression: true
ppi:
  edges: path/to/ppi_edges.tsv
  nodes: path/to/ppi_nodes.tsv
expression:
  matrix: path/to/family_expression.tsv
  metadata: path/to/sample_metadata.tsv
```

`bin/genefam/run_nextflow_standard_smoke.py` 会读取这些 YAML 字段并自动转成 Nextflow 参数，用于验证正式标准分支的论文级图件链路。

## 结果在哪里看

常见结果会在你的 `project.outdir` 下面，例如：

```text
results/My_gene_family/
  tables/
  sequences/
  alignment/
  phylogeny/
  plots/
  report/
```

重点看：

- `tables/family_candidates.tsv`：候选基因家族成员
- `tables/family_counts.tsv`：每个物种的成员数量
- `sequences/family_members.faa`：家族成员蛋白序列
- `tables/gene_structure_summary.tsv`：基因结构统计
- `tables/chromosome_locations.tsv`：染色体位置
- `alignment/*.aln.faa`：多序列比对结果
- `phylogeny/*.treefile`：进化树
- `report/final_report.md`：最终报告

如果运行 promoter 模块或相关 smoke，会看到：

- `tables/promoters.bed`
- `sequences/promoters.fa`
- `plots/feature_summary.pdf`

如果运行 MCScanX + circlize 可视化，会看到：

- `tables/circlize_chromosomes.tsv`
- `tables/circlize_links.tsv`
- `tables/circlize_skipped_links.tsv`
- `plots/mcscanx_circlize.pdf`
- `plots/mcscanx_circlize.png`

## 单物种、3 个物种、很多物种该怎么选

单物种适合检查：

- 输入文件格式
- HMMER / DIAMOND 能否识别家族成员
- GFF3 gene ID 是否匹配
- chromosome location / gene structure 是否正常
- promoter 是否能提取

3 个物种更适合第一轮真实试跑，因为它可以额外检查：

- 多物种 copy number 对比
- 多物种家族成员 FASTA 汇总
- MAFFT + FastTree 是否能跑通
- 初步多物种报告是否合理

很多物种适合最后正式分析。建议顺序是：

```text
1 个物种 -> 3 个物种 -> 10 个物种 -> 全部物种
```

## 关于 gamma / beta / alpha / theta

这些不是软件直接“测出来”的事件名，而是对 WGD/WGT 层的生物学解释。

流程里会先做更底层的证据：

- MCScanX 共线性
- duplicate type
- Ka/Ks
- WGD layer

然后再通过 YAML 里的事件配置，把某些 WGD layer 解释成：

- `gamma`
- `beta`
- `alpha`
- `theta`
- 或你自己定义的事件名

也就是说：

```text
synteny + Ks + layer classification -> anonymous WGD layers
anonymous WGD layers + event YAML/literature metadata -> gamma/beta/alpha/theta
```

这样做的好处是流程不会把事件名当成原始事实，而是明确区分“观测证据”和“文献解释”。

## 真实 MCScanX / KaKs 到 WGD 分支

如果你已经有真实的 MCScanX `.collinearity` 文件和 KaKs_Calculator 结果表，可以直接让 Nextflow 生成 WGD 分支需要的中间表：

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  --config configs/example.config.yaml \
  --run_duplication_retention true \
  --family_members path/to/family_candidates.tsv \
  --mcscanx_collinearity path/to/sample.collinearity \
  --kaks_results path/to/kaks_calculator.tsv \
  --events_config configs/wgd_events.brassicaceae.yaml \
  --ks_bins 0.3,0.8,1.5 \
  --wgd_event_args "--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta"
```

它会先写出：

- `mcscanx_kaks_handoff/tables/syntenic_pairs.tsv`
- `mcscanx_kaks_handoff/tables/duplicate_types.tsv`
- `mcscanx_kaks_handoff/tables/normalized_kaks.tsv`
- `mcscanx_kaks_handoff/tables/kaks_pairs.tsv`
- `mcscanx_kaks_handoff/mcscanx_kaks_handoff.md`

然后再进入 WGD layer、gamma/beta/alpha/theta 事件解释、家族保留统计和报告生成。

## MCScanX + circlize 可视化

目前已经有一个专门的 smoke：

```bash
python bin/genefam/run_mcscanx_circlize_smoke.py \
  --r-bin /usr/local/bin/R \
  --outdir results/mcscanx_circlize_smoke
```

它会生成：

- `results/mcscanx_circlize_smoke/tables/circlize_chromosomes.tsv`
- `results/mcscanx_circlize_smoke/tables/circlize_links.tsv`
- `results/mcscanx_circlize_smoke/tables/circlize_skipped_links.tsv`
- `results/mcscanx_circlize_smoke/plots/mcscanx_circlize.pdf`
- `results/mcscanx_circlize_smoke/plots/mcscanx_circlize.png`

真实数据中，如果某些 MCScanX gene pair 找不到坐标，不会直接崩掉，而是写入 `circlize_skipped_links.tsv`，方便你检查是不是 gene ID 不一致。

## 开发和验收状态

常用检查命令：

```bash
python -m pytest tests -q
python bin/genefam/run_release_checks.py --outdir results/release_checks
```

当前已知状态：

- Python / R / Nextflow 主流程开发已基本成型
- `GeneFamilyFlow` 环境用于本地运行
- `/usr/local/bin/R` 用于 R 图
- Docker / Apptainer 是最后的封装和可重复运行验证，不是当前第一轮真实数据试跑的前置条件

查看总体验收状态：

```text
results/release_checks/release_checks.md
results/objective_audit/objective_audit.md
results/handoff/handoff_report.md
results/local_acceptance/local_acceptance_summary.md
```

如果 release gate 里 required failed 为 0，但总目标仍显示 blocked，优先看 `results/local_acceptance/local_acceptance_summary.md` 里的 `final_stage_blocker`，再看 `results/delivery_bundle_smoke/figure_gallery_audit.md` 和 `results/delivery_bundle/final_delivery_manifest_audit.md`。前者确认论文级图件目录可导航，后者确认最终交付清单路径可解析。

## 重要文件

- `configs/example.config.yaml`：最基础配置示例
- `configs/advanced_modules.example.yaml`：高级模块配置示例
- `configs/publication_modules.example.yaml`：论文级标准分支可视化 smoke 的 YAML-only 配置示例
- `docs/input_contract.md`：输入文件规范
- `docs/quickstart.md`：快速运行说明
- `docs/release_audit.md`：开发目标和证据对照表
- `docs/wgd_event_evidence.md`：WGD 事件解释说明
- `docs/standard_to_wgd_handoff.md`：标准分析到 WGD 分析的衔接说明
- `HISTORY.md`：开发日记和 commit 记录
- `Reference/`：论文和参考脚本，只作为参考材料，不直接修改

## 推荐你下一步怎么做

我建议你下一步准备 3 个物种的数据，然后新建一个 `configs/my_3species.yaml`。

先跑：

```bash
python bin/genefam/validate_config.py configs/my_3species.yaml --check-paths
```

通过后再跑：

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  -profile activated \
  --config configs/my_3species.yaml \
  --run_identification true \
  --tree_builder fasttree \
  --final_rule intersection
```

第一轮目标不是把所有高级模块一次性跑完，而是先确认：

- 3 个物种能被识别
- HMMER / DIAMOND 能找到候选成员
- 候选成员数量合理
- GFF3 坐标能匹配
- family_members.faa 能生成
- FastTree 能生成树
- final_report.md 能打开阅读
