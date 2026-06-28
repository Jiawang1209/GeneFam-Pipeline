# Reference-to-Pipeline 严格映射

本文档是 GeneFam-Pipeline 的开发约束，不是结果宣传页。所有模块必须以
`Reference/Long_Weixiong_20240323_1_GDSL/Evolution_LWX_GDSL_2024.md`
和 `Reference/Long_Weixiong_20240323_1_GDSL/R/` 为准；如果当前流程只是
“功能类似”，必须标为 `adapted` 或 `partial`，不能写成 `exact`。

## 状态定义

- `exact`: 命令路线、核心输入、核心输出和图形结构与 Reference 基本一致，只做物种名、路径、线程数、通用化参数的必要改写。
- `adapted`: 生物学意图一致，但为 Nextflow、多物种 YAML、真实软件可用性或大规模数据做了等价改写。
- `partial`: 只完成了主干或部分输出，距离 Reference 的结果文件夹或图形还缺关键内容。
- `missing`: 尚未接入正式流程。
- `skip-by-input`: Reference 有该模块，但当前真实数据没有对应输入；流程必须跳过而不是整体失败。

## Reference Step 映射

| Reference step | Reference 路线 | 当前 Pipeline 位置 | 状态 | 必须保留或补齐的内容 |
| --- | --- | --- | --- | --- |
| `1.database` | 手工整理每个物种的 genome/pep/cds/gff3 到 `1.database` | `00_preprocess/`, `bin/genefam/preprocess_species.py` | `adapted` | 已改成 `data/species_bank/<species>/` 自动发现；必须继续保留最长转录本、pep/cds ID 清洗、去除 `|PACid`、去除蛋白终止 `*`、CDS/pep 对应关系、清洗日志和 warning 表。 |
| `2.hmmsearch` | `PF00657.hmm` 一轮 hmmsearch，筛选 hit，提取序列，ClustalW 比对，`hmmbuild new_GDSL.hmm`，二轮 hmmsearch | `01_gene_identification/`, `02_domain_filtering/`, `build_rebuilt_hmmer_inputs.py` | `adapted` | 当前支持两轮 HMMER 和 `hmmbuild`，但比对工具按流程配置可用工具适配；输出必须保留 first-pass hit、alignment、rebuilt HMM、second-pass domtblout 和 `2st_id` 等等价文件。 |
| `3.blast` | 从 `all.domains.txt` 中 grep PF 号，提取 Arabidopsis reference 蛋白，`makeblastdb` 后所有物种 `blastp` | `02_domain_filtering/`, `build_reference_from_tair_domains.py` | `adapted` | 必须以 HMM/PFAM 号命名 Reference，例如 `PF00657_reference.pep.fa`；必须保留 reference ID、missing ID、每物种 blast/diamond 原始证据和筛选后的 `species_*.blast.id`。 |
| `4.identification` | HMM 二轮结果和 BLAST 结果取交集；再用 `hmmscan` 或 `pfam_scan.pl` 确认；输出 `identify.ID.fa` | `01_gene_identification/`, `run_pfam_confirmation.py` | `adapted` | 有 Pfam DB 或预计算结果时必须确认结构域；没有 DB 时模块状态写 `missing_input` 或 `missing_dependency`，流程继续。 |
| `5.genefamily_info` | `clean_ID.R` 清洗 ID，合并 GFF，后续 R 脚本输出 `Gene_Information.xlsx` 和 `species_gene_info.pdf` | `15_gene_family_summary/`, `scripts/plot_gene_family_info.R` | `partial` | 已有蛋白属性和汇总，但需要进一步按 `5.GeneFamily_Info.R` 复刻：species tree 拼接、Length/MW/Hydrophobicity/pI 四类箱线/蜂群图、`Gene_Information_stat.xlsx`。 |
| `6.tree` | MUSCLE 比对，IQ-TREE `-m MFP -bb 1000 -bnni`，`6.tree.R` 用 ggtree 标注 clade/species/support | `03_alignment/`, `04_phylogeny/`, `scripts/plot_tree_features.R` | `partial` | FastTree 是大规模默认分支必须保留；同时需要提供 IQ-TREE 可选分支，并按 `6.tree.R` 复刻 group 表、clade strip、support point、species 分布图。 |
| `7.motif_genestructure` | 清洗 `identify.ID.fa`，MEME `-mod anr -protein -nmotifs 10 -minw 20 -maxw 150` | `05_motif_analysis/`, `06_gene_structure/` | `partial` | MEME raw 输出已接入方向正确；还要把 motif、gene structure、domain 三类图按 Reference 风格放入模块文件夹，并输出统计表。 |
| `8.collinearity` | JCVI：GFF 转 BED、BED uniq、pep 子集、`jcvi.compara.catalog ortholog`、`synteny screen --minspan=30`、手工 `seqids/layout`、`jcvi.graphics.karyotype` | `10_synteny_jcvi/`, `prepare_jcvi_collinearity.py`, `run_jcvi_collinearity.py` | `adapted` | JCVI 只负责物种间共线性；必须保留 BED/pep、pair manifest、ortholog/screen/karyotype 命令、`.anchors.simple`、colored family anchors、`karyotype.pdf`。 |
| `8.1 KaKs` | 从 JCVI `*color2` 取 gene-pair，提取 pep/cds，清洗 CDS ID，交给 Ka/Ks | `14_duplication_retention_kaks/`, `prepare_reference_kaks_inputs.py`, `run_reference_kaks_calculator.py` | `partial` | 已接入 JCVI gene pair 和 KaKs_Calculator2；真实三物种运行得到 230 pairs、125 成功、105 失败，失败已按 QC 分类。下一步要继续处理 length mismatch 和可替代 Ka/Ks 工具。 |
| `9.mcscanx` | 物种内 MCScanX self；提取 family BED；读取 `.gene_type`、`.tandem2`、`.collinearity2`；每个物种画 Circos | `11_mcscanx/`, `build_mcscanx_self_inputs.py`, `run_mcscanx_self.py`, `build_circlize_inputs.py`, `scripts/plot_mcscanx_circlize.R` | `adapted` | MCScanX self 是必须分支，不是可选附属。当前通用脚本已按 `9.Circos_AT.R` 核心图层复刻：染色体、family labels、500 kb density、duplicate type 轨道、collinearity/tandem links、ComplexHeatmap legend，并输出全局图以及 `species/<species>/circos_<species>.pdf/png`。后续只剩可选物种专属配色进一步贴近原脚本。 |
| `9.1 KaKs` | 合并各物种 `*.gene_pairs.ID.csv`，提取 all.ID pep/cds，清洗后做 Ka/Ks；`9.mcscanx_KaKs.R` 作图 | `14_duplication_retention_kaks/`, `scripts/plot_duplicate_type_kaks.R` | `partial` | MCScanX self pairs 已进入 Ka/Ks 输入；需要进一步复刻 `9.mcscanx_KaKs.R` 的 duplicate type x Ka/Ks facet 图，并把每物种 gene pair CSV 放在模块内。 |
| `10.promoter` | 提取 2 kb upstream promoter；大 FASTA split；提交 PlantCARE；`10.promoter.R` 结合 species tree 和 cis-element 描述作图 | `08_promoter/`, `09_promoter_cis/`, `extract_promoters.py`, `split_promoter_fasta_for_plantcare.py`, `plot_promoter_cis_elements.R` | `partial` | promoter 提取、FASTA split、PlantCARE gene-level 命中表导入、`cir_element.desc*.xlsx` 字典注释、`promoter1.pdf/png` 和 `species_promoter2.pdf/png` 已接入；当前只有 `cir_element.desc.20240509.xlsx` 字典、没有命中表时仍标为缺输入并不中断整体分析。还缺 `10.promoter.R` 中 ggtree species tree 拼接式排版。 |
| `11.ppi` | 家族蛋白与 Arabidopsis 双向 BLAST，映射 AraNet，补 Pfam 注释，`11.ppi.R` 使用 `ggNetView` 作图 | `12_ppi/`, `build_aranet_ppi_from_reciprocal_blast.py`, `build_ppi_tables.py`, `plot_ppi_ggnetview.R` | `partial` | 已基于用户提供的 `AraNet.txt` 做跨物种 Arabidopsis ortholog PPI 转移，不直接把 AraNet 当所有物种 PPI；PPI 可视化按项目要求统一使用 `ggNetView`，输出 `ppi_ggnetview.pdf/png`，并将 `ppi.pdf/png` 作为 Reference 命名兼容副本；同时输出 `node_annotation.tsv`、`species_ppi_annotation.tsv`、hub/QC/evidence 表。剩余差距：Pfam scan 原始域注释输入仍需继续 exact 复刻。 |
| `12.rnaseq` | Reference 文档中 shell 部分为空，`12.rnaseq.R` 对 Rice/Wheat cold RNA-seq 矩阵做 pheatmap | `13_expression/`, `plot_expression_heatmap.R` | `skip-by-input` | 没有 expression matrix 时必须跳过并记录；有矩阵时输出热图、清洗矩阵和样本分组统计。 |

## R 脚本逐项复刻审计

| Reference R script | Reference 图/表 | 当前脚本 | 状态 | 下一步 |
| --- | --- | --- | --- | --- |
| `5.GeneFamily_Info.R` | `Gene_Information.xlsx`, `Gene_Information_stat.xlsx`, `species_gene_info.pdf` | `plot_gene_family_info.R`, `build_gene_family_info.py` | `partial` | 复刻 ggtree species tree + protein property facet + beeswarm/boxplot 组合。 |
| `6.tree.R` | `tmp.pdf`, `tree_group.xlsx`, `p_plot.pdf`, `species.pdf` | `plot_tree_features.R` | `partial` | 增加 IQ-TREE 可选输出、clade strip、support 分层点、species/group 统计图。 |
| `8.collinearity_kaks.R` | `8.jcvi_Kaks.pdf` | `plot_kaks.R` 或 Ka/Ks plot branch | `partial` | 按 Reference 使用 boxplot + quasirandom + `facet_wrap(~Type)` + y=1 参考线。 |
| `9.Circos_*.R` | 每物种 `circos_*.pdf`, `*.gene_pairs.csv`, `*.gene_pairs.ID.csv` | `plot_mcscanx_circlize.R`, `build_circlize_inputs.py` | `adapted` | 已复刻核心 circlize 图层，并生成每物种 `species/<species>/circos_<species>.pdf/png`；可选继续补每个 Reference 物种脚本中的专属染色体填充色。 |
| `9.mcscanx_KaKs.R` | `9.mcscanx_Kaks.pdf` | `plot_duplicate_type_kaks.R` | `partial` | 对齐 `facet_grid(Duplcate Type ~ Type)` 和 duplicate type 统计。 |
| `10.promoter.R` | `promoter1.pdf`, `species_promoter2.pdf` | `plot_promoter_cis_elements.R` | `partial` | 已生成 Reference 命名的 `promoter1.pdf/png` 与 `species_promoter2.pdf/png`，并进入正式 report index 与 `09_promoter_cis` 模块结果包；还需进一步复刻 species tree + promoter heatmap 的拼接布局。 |
| `11.ppi.R` | `ppi.pdf`, `ppi_ggnetview.pdf`, node annotation xlsx | `plot_ppi_ggnetview.R`, `build_aranet_ppi_from_reciprocal_blast.py`, `build_ppi_tables.py` | `partial` | 已补 `ggNetView` 按物种网络图，并将 Reference 命名 `ppi.pdf/png` 指向同一 ggNetView 可视化；已补 `node_annotation.tsv`、`species_ppi_annotation.tsv`、hub/QC/evidence 表；继续补 Pfam scan 原始域注释输入。 |
| `12.rnaseq.R` | `Rice_pheatmap_cold.pdf`, `Ta_pheatmap_cold.pdf`, expression xlsx | `plot_expression_heatmap.R` | `skip-by-input` | 只有用户提供 expression matrix 后启用；否则 report 写跳过原因。 |

## 当前真实三物种证据

最近一次真实三物种检查目录：
`results/real_3species_reference_goal_run_kaks_clean`

- MCScanX self：已产生 `.blast/.collinearity/.tandem/html`、`species_pairs/*.gene_pairs.csv`、`species_pairs/*.gene_pairs.ID.csv`、circlize 输入表和图。
- Reference-style circlize 复测：`/usr/local/bin/R` 直接运行 `scripts/plot_mcscanx_circlize.R` 于真实三物种表，生成 `/tmp/genefam_reference_circlize_species_check/mcscanx_circlize.pdf`、`.png`，以及 `species/Arabidopsis_thaliana/circos_Arabidopsis_thaliana.*`、`species/Brassica_rapa/circos_Brassica_rapa.*`、`species/Capsella_rubella/circos_Capsella_rubella.*`。
- Ka/Ks：真实三物种当前为 230 pairs，125 个非空结果，105 个失败；终止密码子清洗已处理，剩余主要是 length mismatch 或基础 QC 不通过。
- Expression：当前没有 expression matrix，必须是 `skip-by-input`。
- PlantCARE：有 gene-level 命中表时可生成 `promoter_cis_elements.*`、`promoter1.*` 和 `species_promoter2.*`；当前真实三物种只有 `cir_element.desc.20240509.xlsx` 字典、没有 PlantCARE gene-level 命中结果时，只能生成提取/提交/导入准备并标为 `missing_input`，不能假装完成 cis-element 统计。

## 开发优先级

1. 继续对齐 `11.ppi.R`，在已完成 reciprocal BLAST + AraNet ortholog transfer + `ggNetView` + 节点注释表 + Reference 命名 `ppi.pdf/png` 基础上，补 Pfam scan 原始域注释输入；PPI 绘图不再引入额外 ggraph 分支。
2. 对齐 `5.GeneFamily_Info.R` 和 `6.tree.R`，把蛋白属性、species tree、group/clade/support 图补成 Reference 风格。
3. 对齐 `8.collinearity_kaks.R` 和 `9.mcscanx_KaKs.R`，让 JCVI Ka/Ks 与 MCScanX duplicate type Ka/Ks 分开作图、分开解释。
4. 继续增强 `10.promoter.R`：补 species tree + promoter heatmap 的拼接布局。
5. 可选增强 `9.Circos_*.R`：按物种配置 Reference 脚本中的染色体填充色。

## 验收原则

- 每个模块结果必须放入独立文件夹，不能只在总 report 里出现。
- 每张图都要有来源表、绘图脚本、运行状态和报告解读。
- Reference 已经写明的步骤，不能被泛化模块悄悄替代；如果替代，必须在本文件标为 `adapted` 并说明原因。
- 缺少输入或软件时，模块状态应叫停该模块，而不是叫停整个工作流。
