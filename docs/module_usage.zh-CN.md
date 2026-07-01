# GeneFam-Pipeline 子模块使用说明

本文档记录每个子模块的用途、最简命令、常用参数、默认输入输出和结果文件。原则是：命令行尽量简洁，复杂参数留给必要时覆盖。

## 环境约定

推荐先激活项目环境：

```bash
source /Users/liuyue/miniforge3/etc/profile.d/conda.sh
conda activate GeneFamilyFlow
```

当前已确认 `GeneFamilyFlow` 中包含：

```text
hmmsearch  HMMER 3.4
hmmbuild   HMMER 3.4
mafft      v7.526
```

R 语言固定优先使用：

```text
/usr/local/bin/R
```

## 模块顺序

当前正式模块编号：

```text
01_preprocess  数据清洗与 reusable clean species bank
02_hmm         HMM-only 候选蛋白筛选
03_blastp      从模式植物 domain annotation 提取 seed sequences 并进行 BLASTP
04_identification  HMM 与 BLASTP 证据整合，后续开发
```

## 项目级配置

每次基因家族分析推荐使用一个项目目录，所有模块参数统一写入一个 `project.yaml`：

```text
projects/
  GDSL_2026/
    project.yaml
    config/
      hmm_profiles/
        PF00657.hmm
    results/

configs/
  03_blastp/
    reference_sources.tsv
    domain_annotations/
      Arabidopsis_thaliana.all.domains.txt
      Oryza_sativa.all.domains.txt
```

这里的 `projects/GDSL_2026/` 是 `GeneFam-Pipeline` 仓库内部的项目工作区，不是另一个仓库。也就是说，如果当前工作目录是：

```text
/Users/liuyue/Desktop/Github_repos/GeneFam-Pipeline
```

那么项目级配置文件实际路径就是：

```text
/Users/liuyue/Desktop/Github_repos/GeneFam-Pipeline/projects/GDSL_2026/project.yaml
```

也就是说：

- `01_preprocess` 的正式 clean bank 来自 `projects/GDSL_2026/results/01_preprocess/species_clean_bank`
- HMM profile 是项目/基因家族特异资源，放在项目目录下的 `config/hmm_profiles/`
- BLASTP reference source 和 Arabidopsis/Oryza domain annotation 是跨项目复用资源，放在仓库级 `configs/03_blastp/`
- 每个模块的参数统一写入项目根目录的 `project.yaml`
- 不再为每个模块单独维护一个 YAML

示例模板：

```text
projects/GDSL_2026/project.yaml
```

## 01_preprocess

### 作用

`01_preprocess` 负责从原始物种库构建可复用的 clean species bank。

它会：

- 清洗 protein/CDS FASTA ID
- 去掉蛋白序列末尾终止符 `*`
- 按最长蛋白选择每个基因的代表转录本
- 保留原始数据 `raw/`
- 输出清洗数据 `clean/`
- 输出审计表 `audit/`
- 生成 genome/chromosome 长度表
- 生成全物种 QC TSV 和 Excel
- 标记是否为染色体水平组装

### 输入目录

推荐结构：

```text
data/species_bank/
  Arabidopsis_thaliana/
    Arabidopsis_thaliana.pep.fa
    Arabidopsis_thaliana.cds.fa
    Arabidopsis_thaliana.genome.fa
    Arabidopsis_thaliana.gff3
```

### 最简命令

```bash
python bin/genefam/build_species_clean_bank.py --raw-root data/species_bank
```

### 常用命令

正式运行当前 12 物种 clean bank，推荐使用：

```bash
python bin/genefam/build_species_clean_bank.py \
  --raw-root data/species_bank \
  --outdir projects/GDSL_2026/results/01_preprocess \
  --require-cds \
  --require-genome \
  --require-gff3 \
  --scaffold-chromosome-min-bp 10000000
```

这条命令的含义是：

- `--raw-root data/species_bank`：读取原始物种库，每个物种一个文件夹。
- `--outdir projects/GDSL_2026/results/01_preprocess`：把 01 模块的正式结果写入当前基因家族项目目录，不污染工具仓库根目录。
- `--require-cds`：要求每个物种提供 CDS；缺失时该物种会被标记为 `missing_required_input`。
- `--require-genome`：要求每个物种提供 genome FASTA，用于 genome/chromosome 长度统计和后续 promoter/JCVI/circlize 等模块。
- `--require-gff3`：要求每个物种提供 GFF3，用于 transcript-gene 映射和后续基因结构/坐标分析。
- `--scaffold-chromosome-min-bp 10000000`：将长度不低于 10 Mb 的编号 scaffold，如 `scaffold_1`，近似提升为 chromosome；当前用于 Setaria italica 这类 scaffold 命名的染色体级组装。

要求每个物种都尽量有 protein、CDS、genome、GFF3：

```bash
python bin/genefam/build_species_clean_bank.py \
  --raw-root data/species_bank \
  --require-cds \
  --require-genome \
  --require-gff3
```

输出到指定目录：

```bash
python bin/genefam/build_species_clean_bank.py \
  --raw-root data/species_bank \
  --outdir results/my_prepare
```

只处理指定物种：

```bash
python bin/genefam/build_species_clean_bank.py \
  --raw-root data/species_bank \
  --include Arabidopsis_thaliana,Brassica_rapa
```

默认情况下，`raw/` 目录中的 pep/CDS/genome/GFF3 都是指向原始物种库的软链接；`clean/` 目录中的 pep/CDS 会完成清洗并真实写入，genome/GFF3 默认仍为软链接。

```bash
python bin/genefam/build_species_clean_bank.py \
  --raw-root data/species_bank \
  --outdir projects/GDSL_2026/results/01_preprocess \
  --require-cds \
  --require-genome \
  --require-gff3
```

如果需要把 clean bank 打包迁移到其它机器，或者需要让 `clean/` 目录中的 genome/GFF3 也自包含，再显式复制 clean genome/GFF3。注意：`raw/` 目录仍然只保留软链接，用于追溯原始输入，不作为归档主体。

```bash
python bin/genefam/build_species_clean_bank.py \
  --raw-root data/species_bank \
  --outdir projects/GDSL_2026/results/01_preprocess_archive \
  --require-cds \
  --require-genome \
  --require-gff3 \
  --large-file-mode copy
```

如果某些物种的染色体被命名为 `scaffold_1`、`scaffold_2` 这类编号 scaffold，并且你已经确认长 scaffold 可以近似作为染色体使用，可以加长度阈值。例如 Setaria italica 的前 9 条 scaffold 均为几十 Mb，而 `scaffold_10` 只有约 423 kb，因此可以用 10 Mb 阈值只提升前 9 条：

```bash
python bin/genefam/build_species_clean_bank.py \
  --raw-root data/species_bank \
  --outdir projects/GDSL_2026/results/01_preprocess \
  --require-cds \
  --require-genome \
  --require-gff3 \
  --scaffold-chromosome-min-bp 10000000
```

### 主要参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--raw-root` | 必填 | 原始物种库目录 |
| `--outdir` | `results` | 结果根目录 |
| `--out-root` | `<outdir>/species_clean_bank` | clean bank 输出目录，高级覆盖项 |
| `--manifest` | `<outdir>/species_clean_bank_manifest.tsv` | 全局 manifest 输出 |
| `--qc` | `<outdir>/species_clean_bank_qc.tsv` | 全局 QC TSV |
| `--qc-excel` | `<outdir>/species_clean_bank_qc.xlsx` | 全局 QC Excel |
| `--failed` | `<outdir>/species_clean_bank_failed.tsv` | 失败或未准备完整物种记录 |
| `--summary` | `<outdir>/species_clean_bank_summary.md` | Markdown 汇总 |
| `--include` | `all` | 只处理指定物种，逗号分隔 |
| `--exclude` | 空 | 排除指定物种，逗号分隔 |
| `--require-cds` | false | 缺 CDS 时标记为 `missing_required_input` |
| `--require-genome` | false | 缺 genome 时标记为 `missing_required_input` |
| `--require-gff3` | false | 缺 GFF3 时标记为 `missing_required_input` |
| `--large-file-mode` | `symlink` | genome/GFF3 写入方式：默认软链接以节省空间；`copy` 用于可迁移归档；`skip` 不写入 clean/raw 副本并在 manifest 中引用原始路径 |
| `--scaffold-chromosome-min-bp` | `0` | 将长度达到阈值的编号 scaffold，如 `scaffold_1`，提升为 chromosome；`0` 表示关闭，避免误判 |

### 默认输出

```text
projects/GDSL_2026/results/01_preprocess/
  species_clean_bank/
    <species>/
      raw/
      clean/
      audit/
  species_clean_bank_manifest.tsv
  species_clean_bank_qc.tsv
  species_clean_bank_qc.xlsx
  species_clean_bank_failed.tsv
  species_clean_bank_summary.md
```

每个物种的核心清洗结果：

```text
projects/GDSL_2026/results/01_preprocess/species_clean_bank/<species>/clean/
  <species>.protein.clean.fa
  <species>.cds.clean.fa
  <species>.genome.fa
  <species>.gff3
  <species>.chromosome.lengths.tsv
```

其中 `protein.clean.fa` 和 `cds.clean.fa` 是清洗后的真实文件；默认情况下 `genome.fa` 和 `gff3` 是软链接；`chromosome.lengths.tsv` 是真实生成的染色体长度表。

`species_clean_bank_qc.xlsx` 用于人工检查，重点字段：

| 字段 | 说明 |
| --- | --- |
| `assembly_level` | `chromosome`、`scaffold_or_contig`、`missing_genome` 等 |
| `chromosome_analysis_ready` | 是否适合进入染色体级 MCScanX/circlize/JCVI 分析 |
| `chromosome_seq_count` | 识别出的染色体序列数量 |
| `unassembled_seq_count` | scaffold/contig/unplaced 等序列数量 |

## 02_hmm

### 作用

`02_hmm` 只使用 HMM 方法筛选候选蛋白序列，不使用 BLASTP。

它支持：

- 单个 HMM profile
- 多个 HMM profile
- 多 HMM 的 `any` 或 `all` 合并规则
- 直接 HMM 搜索
- Reference 风格 two-pass：first-pass HMM search、提取命中蛋白、MAFFT、hmmbuild、自建 HMM、second-pass HMM search

### HMM 输入目录

只需要传入 HMM 文件夹：

```text
projects/GDSL_2026/config/hmm_profiles/
  PF00657.hmm
```

或多个：

```text
projects/GDSL_2026/config/hmm_profiles/
  PF00001.hmm
  PF00002.hmm
```

脚本会自动扫描 `*.hmm`，并使用文件名去掉 `.hmm` 后的部分作为 `hmm_id`。

### 最简命令

```bash
python bin/genefam/run_hmm_module.py \
  --hmm-dir projects/GDSL_2026/config/hmm_profiles
```

如果使用项目级配置：

```bash
python bin/genefam/run_hmm_module.py \
  --config projects/GDSL_2026/project.yaml
```

默认读取：

```text
projects/GDSL_2026/results/01_preprocess/species_clean_bank
```

默认输出：

```text
projects/GDSL_2026/results/02_hmm
```

### 指定 clean bank 和输出目录

```bash
python bin/genefam/run_hmm_module.py \
  --clean-bank projects/GDSL_2026/results/01_preprocess/species_clean_bank \
  --hmm-dir projects/GDSL_2026/config/hmm_profiles \
  --outdir projects/GDSL_2026/results/02_hmm
```

### 多 HMM 合并规则

命中任意 HMM 即为候选：

```bash
python bin/genefam/run_hmm_module.py \
  --hmm-dir projects/GDSL_2026/config/hmm_profiles \
  --combine-rule any
```

必须命中所有 HMM 才为候选：

```bash
python bin/genefam/run_hmm_module.py \
  --hmm-dir projects/GDSL_2026/config/hmm_profiles \
  --combine-rule all
```

默认是：

```text
any
```

### two-pass 自建 HMM

Reference 风格 two-pass：

```bash
python bin/genefam/run_hmm_module.py \
  --hmm-dir projects/GDSL_2026/config/hmm_profiles \
  --rebuild-hmm \
  --family-name GDSL
```

流程：

```text
input HMM profiles
  -> first-pass hmmsearch
  -> first-pass hits peptide FASTA
  -> MAFFT alignment
  -> hmmbuild <family-name>.rebuilt.hmm
  -> second-pass hmmsearch
  -> final HMM candidates
```

当前 `projects/GDSL_2026/project.yaml` 已启用：

```yaml
hmm:
  rebuild_hmm: true
  family_name: GDSL
```

因此正式 `02_hmm` 输出使用 second-pass HMM search 作为最终 HMM candidates。

### 主要参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--clean-bank` | `projects/GDSL_2026/results/01_preprocess/species_clean_bank` | `01_preprocess` 输出的 clean bank |
| `--config` | 空 | 项目级 `project.yaml` |
| `--hmm-dir` | 必填 | 存放 `.hmm` 文件的目录 |
| `--outdir` | `projects/GDSL_2026/results/02_hmm` | `02_hmm` 输出目录 |
| `--combine-rule` | `any` | 多 HMM 合并规则：`any` 或 `all` |
| `--evalue` | `1e-10` | HMMER domain e-value 过滤阈值 |
| `--min-bitscore` | `0.0` | 最低 bit score |
| `--min-domain-coverage` | `0.0` | 最低 HMM domain coverage |
| `--rebuild-hmm` | false | 是否执行 two-pass 自建 HMM |
| `--family-name` | `family` | 自建 HMM 文件名前缀 |

### 默认输出

```text
results/02_hmm/
  inputs/
    hmm_profiles.tsv
    species_peptides.tsv
  raw/
    <species>.<hmm_id>.domtblout
    <species>.<hmm_id>.hmmout
  tables/
    hmm_hits.raw.tsv
    hmm_hits.filtered.tsv
    hmm_candidates.tsv
    hmm_candidate_ids.txt
    per_search/
  fasta/
    hmm_candidates.pep.fa
  rebuilt_hmm/
    first_pass_hits.pep.fa
    first_pass_hits.aln.fa
    <family-name>.rebuilt.hmm
    hmmbuild.log
  report/
    hmm_summary.tsv
    hmm_summary.md
```

`hmm_candidates.tsv` 是这个模块最重要的候选表。

核心字段：

| 字段 | 说明 |
| --- | --- |
| `species_id` | 物种 ID |
| `gene_id` | 候选基因/蛋白 ID |
| `matched_hmm_count` | 命中的 HMM 数量 |
| `required_hmm_count` | 本次输入的 HMM 总数 |
| `matched_hmm_ids` | 命中的 HMM ID 列表 |
| `combine_rule` | 使用的合并规则 |
| `best_evalue` | 最优 e-value |
| `best_bitscore` | 最高 bit score |

## 03_blastp

### 作用

`03_blastp` 根据 Arabidopsis 和 Oryza sativa 等模式植物的 domain annotation 提取 seed/reference peptide，建立 BLASTP 数据库，再用所有物种的 clean protein 进行 BLASTP 证据搜索。

它会：

- 读取 `project.yaml` 中的 `blastp.domain_terms`
- 读取全局 `configs/03_blastp/reference_sources.tsv`
- 从 `01_preprocess` 的 clean bank 中找到参考物种 protein clean FASTA
- 从 domain annotation 中筛选包含目标 PFAM/domain term 的转录本 ID，例如 `AT1G06990.1`、`LOC_Os01g11570.1`
- 将转录本 ID 归一化为 clean bank 中的基因级 ID，例如 `AT1G06990`、`LOC_Os01g11570`
- 从 `01_preprocess` 的 clean protein 中提取 Arabidopsis/Oryza seed/reference peptide
- 合并 seed peptide 并运行 `makeblastdb`
- 对所有物种运行 `blastp`
- 输出 raw hits、filtered hits、candidate genes 和 summary

全局复用配置建议放在：

```text
configs/03_blastp/
  reference_sources.tsv
  domain_annotations/
    Arabidopsis_thaliana.all.domains.txt
    Oryza_sativa.all.domains.txt
```

其中 `reference_sources.tsv` 记录每个参考物种对应的 domain annotation 路径；`domain_annotations/` 下的真实外部注释文件不提交到 git，只在本地保留。

这一步的核心不是直接用 BLASTP 找全家族，而是先从高可信模式植物注释中提取 seed sequences。当前 `seed/` 是正式语义输出；`reference/` 目录保留同一批序列的兼容命名，方便后续模块或旧脚本读取。

### 最简命令

```bash
python bin/genefam/run_blastp_module.py \
  --config projects/GDSL_2026/project.yaml
```

默认读取：

```text
projects/GDSL_2026/results/01_preprocess/species_clean_bank
configs/03_blastp/reference_sources.tsv
```

默认输出：

```text
projects/GDSL_2026/results/03_blastp
```

### 主要参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--config` | 空 | 项目级 `project.yaml` |
| `--clean-bank` | `project.yaml` 中的 `database.species_clean_bank` | `01_preprocess` 输出的 clean bank |
| `--reference-sources` | `project.yaml` 中的 `blastp.reference_sources` | 参考物种 domain annotation 来源表 |
| `--domain-terms` | `project.yaml` 中的 `blastp.domain_terms` | 需要筛选的 PFAM/domain term，如 `PF00657` |
| `--outdir` | `<project.outdir>/03_blastp` | 03 模块输出目录 |
| `--evalue` | `project.yaml` 中的 `blastp.evalue` | BLASTP e-value 阈值 |
| `--num-threads` | `project.yaml` 中的 `blastp.num_threads` | BLASTP 线程数 |
| `--num-alignments` | `project.yaml` 中的 `blastp.num_alignments` | 每个 query 保留的 BLASTP alignment 数 |

### 默认输出

```text
projects/GDSL_2026/results/03_blastp/
  inputs/
    reference_sources.tsv
    species_peptides.tsv
  seed/
    Arabidopsis_thaliana.seed.ids.txt
    Arabidopsis_thaliana.seed.missing_ids.txt
    Arabidopsis_thaliana.seed.pep.fa
    Oryza_sativa.seed.ids.txt
    Oryza_sativa.seed.missing_ids.txt
    Oryza_sativa.seed.pep.fa
    combined_seed.pep.fa
    seed_manifest.tsv
  reference/
    Arabidopsis_thaliana.reference.ids.txt
    Arabidopsis_thaliana.reference.missing_ids.txt
    Arabidopsis_thaliana.reference.pep.fa
    Oryza_sativa.reference.ids.txt
    Oryza_sativa.reference.missing_ids.txt
    Oryza_sativa.reference.pep.fa
    blastp_reference.pep.fa
    reference_manifest.tsv
  database/
    blastp_reference.*
  raw/
    <species>.blastp.tsv
  tables/
    blastp_hits.raw.tsv
    blastp_hits.filtered.tsv
    blastp_candidates.tsv
    blastp_candidate_ids.txt
  report/
    blastp_summary.tsv
    blastp_summary.md
```

`seed/seed_manifest.tsv` 记录每个参考物种从 domain annotation 中筛到多少 ID、成功提取多少 seed peptide，以及有多少 ID 在 clean protein 中缺失。

`blastp_candidates.tsv` 是这个模块最终输出的 BLASTP 候选表。

### 04_identification

### 作用

`04_identification` 严格对齐 Reference Step4 的思路：

```text
02_hmm two-pass HMM candidates
  + 03_blastp seed/reference BLASTP candidates
  -> HMM ∩ BLASTP 交集 inter.ID
  -> 提取 inter.ID.fa
  -> 使用目标 HMM profile 再做 domain confirmation
  -> identify.ID.fa
```

也就是说，默认最终成员不是 HMM 和 BLASTP 的简单并集，而是：

```text
final identification = two-pass HMM candidates ∩ BLASTP candidates ∩ PF00657/domain confirmation
```

### 最简命令

```bash
python bin/genefam/run_identification_module.py \
  --config projects/GDSL_2026/project.yaml
```

默认读取：

```text
projects/GDSL_2026/results/02_hmm/tables/hmm_candidates.tsv
projects/GDSL_2026/results/03_blastp/tables/blastp_candidates.tsv
projects/GDSL_2026/results/01_preprocess/species_clean_bank
projects/GDSL_2026/config/hmm_profiles/PF00657.hmm
```

默认输出：

```text
projects/GDSL_2026/results/04_identification
```

### 主要参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--config` | 空 | 项目级 `project.yaml` |
| `--clean-bank` | `project.yaml` 中的 `database.species_clean_bank` | `01_preprocess` 输出的 clean bank |
| `--hmm-candidates` | `<project.outdir>/02_hmm/tables/hmm_candidates.tsv` | `02_hmm` 输出的 HMM 候选表 |
| `--blastp-candidates` | `<project.outdir>/03_blastp/tables/blastp_candidates.tsv` | `03_blastp` 输出的 BLASTP 候选表 |
| `--hmm-profile` | `hmm.hmm_dir` 下第一个 `.hmm` 文件 | 用于 domain confirmation 的 HMM profile |
| `--domain-terms` | `identification.domain_terms` | 需要确认的结构域 ID，例如 `PF00657` |
| `--domain-evalue` | `1e-5` | domain confirmation 的 e-value 阈值 |
| `--domain-method` | `hmmsearch` | domain confirmation 方法：`hmmsearch` 或 `pfam_scan` |
| `--pfam-scan-dir` | `identification.pfam_scan_dir` | `pfam_scan.pl` 使用的 Pfam 数据库目录 |
| `--pfam-scan-executable` | `pfam_scan.pl` | `pfam_scan.pl` 可执行文件名或路径 |
| `--final-rule` | `intersection` | 候选证据合并规则：`intersection`、`union` 或 `hmm_only` |
| `--outdir` | `<project.outdir>/04_identification` | 04 模块输出目录 |

`final_rule` 是正式接口：

```yaml
identification:
  final_rule: intersection  # 推荐，Reference 风格：HMM ∩ BLASTP
```

如果需要并集：

```bash
python bin/genefam/run_identification_module.py \
  --config projects/GDSL_2026/project.yaml \
  --final-rule union
```

`pfam_scan.pl` 也是正式接口。当前 `GeneFamilyFlow` 环境里尚未检测到 `pfam_scan.pl` 和本地 Pfam 数据库目录，所以默认仍使用 `hmmsearch` 对目标 HMM profile 做 domain confirmation。等本地 Pfam 数据库准备好后，可以切换为：

```yaml
identification:
  domain_method: pfam_scan
  pfam_scan_executable: pfam_scan.pl
  pfam_scan_dir: /path/to/Pfam
```

或命令行直接指定：

```bash
python bin/genefam/run_identification_module.py \
  --config projects/GDSL_2026/project.yaml \
  --domain-method pfam_scan \
  --pfam-scan-dir /path/to/Pfam
```

### 默认输出

```text
projects/GDSL_2026/results/04_identification/
  tables/
    family_candidates.tsv
    inter.ID
    union.ID
    domain_confirmed.id
  fasta/
    inter.ID.fa
    identify.ID.fa
  domain_confirmation/
    domain_confirmation.domtblout
    domain_confirmation.hmmout
    Pfam_scan.out       # 使用 --domain-method pfam_scan 时生成
    Pfam_scan.log       # 使用 --domain-method pfam_scan 时生成
  report/
    identification_summary.tsv
    identification_summary.md
```

当前真实 GDSL_2026 运行结果：

```text
HMM two-pass candidates: 2023
BLASTP candidates: 3550
HMM ∩ BLASTP: 2023
PF00657/domain-confirmed final members: 1958
```

## 05_genefamily_info

### 作用

`05_genefamily_info` 对齐 Reference Step5，基于 `04_identification` 得到的最终家族成员：

- 读取 `identify.ID.fa`
- 解析 `01_preprocess` clean bank 中每个物种的 clean GFF3
- 生成全基因 BED 表 `all_species_gene.bed`
- 为最终家族成员匹配染色体、起止坐标、链方向
- 计算蛋白质理化性质：长度、分子量、疏水性/GRAVY、等电点 pI
- 输出 `Gene_Information.tsv/xlsx`
- 输出 `Gene_Information_stat.tsv/xlsx`
- 输出拷贝数、扩张/收缩、pangenome presence 等统计表
- 可选调用 `/usr/local/bin/R` 生成 `gene_family_info_summary.pdf/png`

### 最简命令

```bash
python bin/genefam/run_genefamily_info_module.py \
  --config projects/GDSL_2026/project.yaml
```

默认读取：

```text
projects/GDSL_2026/results/04_identification/fasta/identify.ID.fa
projects/GDSL_2026/results/01_preprocess/species_clean_bank
```

默认输出：

```text
projects/GDSL_2026/results/05_genefamily_info
```

### 主要参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--config` | 空 | 项目级 `project.yaml` |
| `--clean-bank` | `database.species_clean_bank` | `01_preprocess` 输出的 clean bank |
| `--members-fasta` | `<project.outdir>/04_identification/fasta/identify.ID.fa` | 最终家族成员蛋白 FASTA |
| `--outdir` | `<project.outdir>/05_genefamily_info` | 05 模块输出目录 |
| `--r-bin` | `/usr/local/bin/R` | 绘图使用的 R |
| `--plot` | YAML 中 `genefamily_info.plot` | 生成 summary PDF/PNG |
| `--skip-plot` | false | 跳过绘图，仅生成表格 |

项目配置：

```yaml
modules:
  genefamily_info: true

genefamily_info:
  plot: true
  r_bin: /usr/local/bin/R
```

### 默认输出

```text
projects/GDSL_2026/results/05_genefamily_info/
  tables/
    Gene_Information.tsv
    Gene_Information.xlsx
    Gene_Information_stat.tsv
    Gene_Information_stat.xlsx
    all_species_gene.bed
    gene_family_copy_number.tsv
    gene_family_copy_number_summary.tsv
    gene_family_species_order.tsv
    gene_family_copy_number_expansion.tsv
    gene_family_pangenome_summary.tsv
    gene_family_protein_properties.tsv
  plots/
    gene_family_info_summary.pdf
    gene_family_info_summary.png
  report/
    genefamily_info_summary.md
```

当前真实 GDSL_2026 运行结果：

```text
Final family members: 1958
Members matched to GFF coordinates: 1958
Species with members: 12
GFF gene BED rows: 547058
```
