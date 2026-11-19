# 结构化科研结果数据规范 v1.0.0

**状态：** 本规范拟用于本仓库的新数值计算、模拟、参数扫描和计算验证；合并后对新运行生效。历史结果不追溯改写。  
**规范版本：** `1.0.0`；JSON Schema：Draft 2020-12。  
**适用边界：** 本规范统一数据结构、运行来源和归档方式；它不把软件测试通过等同于物理结论成立。

## 1. 标准结果包

重要计算的规范结果目录采用以下角色分离。实际项目可以按专题目录组织，不要求每个任务机械地创建所有文件。

```text
results/<run_label>/
├── run_manifest.json       # 本次真实执行的来源、配置、环境、命令和输出清单
├── result_summary.json     # 物理/数值结果摘要及其适用范围
├── validation_report.json  # 实际执行的解析、数值、收敛和独立验证
├── *.csv                   # 可直接分析的逐点数据、扫描表或积分表
├── SHA256SUMS.txt          # 结果文件的 SHA-256
└── README.md               # 人类可读的结论、复算命令和状态
```

- 对重要运行，必须有 `run_manifest.json` 或字段等价的机器可读运行清单。
- 对正式数值结果，必须有 `result_summary.json`；现有项目中已承担相同角色的 JSON 可以保留原文件名。
- 进行了验证时，应记录 `validation_report.json`，或在运行清单中完整保存同等检查信息。
- 存在逐点数值、能谱、径向曲线、参数扫描或响应网格时，优先保存原生 CSV/ROOT/HDF5/Parquet 等数据文件，不把大数组全部塞入 JSON。
- `README.md` 解释结果；它不能代替底层 JSON、CSV、脚本和输入数据。

## 2. 三类 JSON 的职责

### 2.1 `run_manifest.json`：这次计算是怎样产生的

至少记录：

- `schema_version`、`record_type=run_manifest`、稳定的 `run_id` 和 UTC 时间；
- 仓库、项目和工作流标识；
- 实际运行所用 Git commit SHA、分支、入口脚本路径及脚本指纹；
- 输入文件的来源、版本、格式、路径/URI、大小、SHA-256，以及所有数据转换；若输入字节不可取得，必须提供不可变 URI 和明确版本；
- 物理参数、数值参数和约定：质量、耦合、单位、近似、网格、求积阶数、精度、容差、边界条件、随机种子等；
- 操作系统、运行时、依赖包版本、硬件；
- 精确命令、开始/结束时间、退出码和运行时长；
- 每个输出文件的相对路径、角色、格式、字节数、SHA-256；CSV 还记录行数、列名和单位；
- 验证状态、各项检查的实际结果，以及 Git 归档状态。

运行清单记录**实际执行的版本**，不能写当前分支最新 SHA 来替代计算发生时的源码 SHA。

### 2.2 `result_summary.json`：计算得到了什么

至少记录：

- `run_id`，并与运行清单一一对应；
- 计算对象、过程、模型分支和研究范围；
- benchmark 的完整物理参数与单位；
- 关键可观测量：数值、单位、定义、误差/不确定度，以及必要的维度标签（例如极化、同位素、通道、耦合点）；
- 对应逐点数据文件的路径、SHA-256、行数、列名和单位；
- 科学状态：`diagnostic`、`provisional`、`reproducible`、`validated`、`historical` 或 `superseded`；
- 结果解释、适用范围和明确排除的内容。

数值应保存为 JSON number，不要把数值写成带单位的字符串。单位放在独立字段。未计算的量使用 `null` 并标注 `not_computed`；不得用 0 代表缺失或未执行。每个 observable 都必须有 `status`：`computed`、`not_computed` 或 `not_applicable`。

下面是**纯格式示例**，数值为人为构造，不是科研结果：

```json
{
  "schema_version": "1.0.0",
  "record_type": "result_summary",
  "run_id": "EXAMPLE-RUN-001",
  "created_at": "2026-11-20T00:00:00Z",
  "project": {
    "repository": "example/research",
    "project_id": "example-project"
  },
  "calculation": "Synthetic schema fixture only",
  "scope": {
    "included": ["data-format validation"],
    "excluded": []
  },
  "benchmark": {
    "mass": {"value": 1.0, "unit": "MeV"}
  },
  "observables": [
    {
      "name": "example_quantity",
      "value": 1.0,
      "unit": "arb.",
      "status": "computed"
    }
  ],
  "data_files": [],
  "scientific_status": "diagnostic",
  "interpretation": "Synthetic example; not a physical result."
}
```

### 2.3 `validation_report.json`：哪些检查实际通过

每项检查记录唯一 ID、名称、类别、状态、方法、观测值、阈值、单位和证据路径。至少区分：

- 解析恒等式和极限；
- 单位、量纲和归一化；
- 软件单元/回归测试；
- 数值积分和网格收敛；
- 独立实现或文献基准交叉验证；
- 物理适用范围检查；
- 文件完整性和哈希检查。

不能用一个总的 `PASS` 替代检查明细，也不能把未执行的检查标成通过。

## 3. CSV 与数值数组规范

1. 第一行为稳定列名；每列只表达一个物理量。
2. 单位必须明确：优先在列名中使用 `r_km`、`omega_MeV`、`ER_keV` 等，或在 JSON 的 `units` 字典中逐列声明。不得依赖读者猜测单位。
3. 多维数据采用 long/tidy format：每行对应一个网格点/样本，极化、同位素、过程、耦合等作为独立维度列；不要把不同极化或同位素混在无标签的数组里。
4. 数值列只放数值；不把单位、注释或状态文字混入数值列。缺失值与物理零值必须区分。
5. 不写入 NaN 或 Infinity。缺失项使用空字段并在数据字典中说明，或使用单独状态列。
6. 保留足以复现计算的有效数字；不得在归档时擅自降低精度、改变列顺序或重采样。
7. JSON/CSV 中的数值、行数、单位、积分网格和结果摘要必须相互一致。

对大数组和大型事件样本，使用项目允许的原生二进制格式或 Git LFS/持久版本化存储，并在清单中记录格式、记录数、大小、不可变位置和 SHA-256。

## 4. 三种状态必须分开

| 字段 | 含义 | 推荐值 |
|---|---|---|
| `execution.status` | 程序是否实际执行 | `succeeded`、`partial`、`failed`、`cancelled`、`blocked`、`running`、`not_started` |
| `validation.status` | 已执行的检查结果 | `passed`、`partial`、`failed`、`blocked`、`inconclusive`、`not_run` |
| `scientific_status` | 结果支持的科学成熟度 | `diagnostic`、`provisional`、`reproducible`、`validated`、`historical`、`superseded` |
| `archive.status` | 文件实际归档位置 | `local_only`、`committed_to_pr_branch`、`merged_and_verified_on_main` |

程序正常退出不等于数值收敛；测试通过不等于物理结论已经验证；文件上传成功不等于已经在 main 上完成归档。

## 5. 项目扩展方式

公共字段放在规范顶层；研究领域特有字段放入 `extensions`，使用稳定的领域名称作为命名空间。不要为了统一格式而丢弃物理上必要的变量，也不要把不同物理层级混为一个观测量。

## 6. Schema 校验和归档验收

本仓库配套的 `research/schemas/research-result-record-v1.0.0.schema.json` 使用 JSON Schema Draft 2020-12，支持 `run_manifest`、`result_summary` 和 `validation_report` 三类记录。安装依赖并执行本仓库校验器：

```powershell
python -m pip install -r research/schemas/requirements-result-validation.txt
python research/schemas/validate_result_records.py --repo-root . <run_manifest.json> <result_summary.json> <validation_report.json>
```

校验器检查 Schema、严格 JSON 数值、引用文件路径/字节数/SHA-256，以及 CSV 的行数、列名、逐列单位和非有限数值。只传入本次实际存在的 JSON 文件。

归档前逐项检查：

- JSON 能严格解析且通过 Schema；
- CSV 列名、单位、行数、数值有限性和网格覆盖正确；
- 所有引用文件存在，字节数、行数和 SHA-256 相符；
- 运行清单的源码 SHA、输入指纹、参数和命令对应真实执行；
- 验证状态只反映实际执行的检查；
- 推送后重新从 GitHub 读取文件，核对路径、大小、数量和 SHA-256。

## 7. 历史结果迁移

本规范从采用后的新运行开始执行。既有 JSON、CSV、日志、图像和历史运行记录保持原样，不为满足新格式而重写原始数据、改变精度或伪造缺失字段。旧文件可由新的索引/运行清单引用，并明确标记为 legacy；只有在能从原始记录中核实的字段才允许补充。

---

## 本仓库的领域扩展

### 暗物质三体散射 / AFH 核响应 / 氙探测器

`extensions.direct_detection` 应记录：

- (m_{\chi_1},m_{\chi_2},m_s,m_V)、(g_1,g_2,g_{VN})、粒子 Dirac/Majorana 性质及宽度方案；
- 三体过程、相空间边界、参考系、(q_A)、(q_N)、(t_N)、(E_R) 的独立定义；
- 固定速度、halo-folded、天然氙、探测器响应和 likelihood 的计算层级；
- 同位素、核质量、丰度来源、AFH 版本、响应通道、(W_M,W_{\Phi''}) 等响应定义；
- 核子 Dirac–Pauli 形状因子 (F_1,F_2)、动量变量、插值方法和归一化；
- halo 分布、局域密度、实验室速度、效率、能量分辨率、曝光和统计方法（仅在相应层级实际包含时记录）。

CSV 推荐按 (E_R)、同位素、响应通道、核模型、速度/halo 节点等维度逐行保存。必须明确区分 (d\sigma_A/dE_R)、halo rate 和 detector-level event prediction；不得把它们放进同一列或用同一状态表示。AFH 响应表应保留 (q_A) 或 (y_A)、同位素、(	au,	au')、响应类型及归一化约定。
