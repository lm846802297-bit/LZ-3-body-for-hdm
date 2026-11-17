from pathlib import Path
import json

folder = Path(__file__).resolve().parent
source = (folder / 'elastic_vector_compare.wls').read_text(encoding='utf-8')
source = source.replace('DirectoryName[DirectoryName[$InputFileName]]', 'DirectoryName[NotebookDirectory[]]')
explanations = {
    'base =': '根据笔记本位置找到 AFH 程序所在目录',
    'Get[': '加载 AFH 程序',
    'a =': '设置同位素、自旋及 AFH 约定的核子和核质量',
    'mChi =': '设置暗物质质量、介子质量及两个耦合常数',
    'speedKms =': '设置速度并转换成自然单位',
    'referenceMass =': '设置 AFH 参考尺度和反冲能量列表',
    'dmformfactor`ZeroCoeffs': '清零 AFH 的相互作用系数',
    'dmformfactor`SetJChi': '设置暗物质自旋',
    'dmformfactor`SetMChi': '设置暗物质质量',
    'dmformfactor`SetIsotope': '加载 Xe-131 的默认核密度',
    'dmformfactor`SetHelm': '使用核密度计算的响应，而不使用 Helm 近似',
    'response =': '提取 AFH 的 M 型等标量核响应',
    'oscillator =': '计算谐振子长度，单位为 GeV 的倒数',
    'wzero =': '计算零动量转移处的响应',
    'rawRzero =': '计算 AFH 原始响应对应的零动量相干因子',
    'evaluate[': '定义单个反冲能量的两种截面计算',
    'q2 =': '计算动量转移平方，反冲能量由 keV 换成 GeV',
    'yval =': '计算核响应的无量纲变量 y',
    'w =': '在当前反冲能量处计算 AFH 核响应',
    'rRaw =': '转换 AFH 响应的等标量及核自旋归一化',
    'rNormalized =': '按三体程序的约定将零动量值归一化为 A 平方',
    'c =': '匹配 AFH 的无量纲系数及传播子',
    'dmformfactor`SetCoeffsNonrel': '设置对应核子的 O1 相互作用系数',
    'afh =': '调用 AFH 计算截面并化成 GeV 的负三次方',
    'direct =': '由直接振幅的领先阶公式计算截面',
    'normalized =': '使用归一化核响应计算同一个直接公式',
    '{er,': '依次返回能量、截面和相对差',
    'rows =': '对所有反冲能量执行比较',
    'Scan[': '逐行显示对照结果',
    'If[': '判断所有数值和相对误差是否满足要求',
    'Print[': '显示参数、表头或检验结果',
    '];': '结束当前定义或判断',
}
annotated = []
for line in source.splitlines():
    stripped = line.strip()
    if stripped and not stripped.startswith('(*'):
        explanation = next((value for key, value in explanations.items() if stripped.startswith(key)), '继续计算当前表达式')
        line += '  (* ' + explanation + ' *)'
    annotated.append(line)
source = '\n'.join(annotated) + '\n'
parts = source.split('(* Equal p and n couplings:')
head = parts[0]
tail = '(* Equal p and n couplings:' + parts[1]
def cell(text, style):
    encoded = json.dumps(text, ensure_ascii=True)
    encoded = encoded.replace('\\u', '\\:')
    return 'Cell[' + encoded + ', ' + json.dumps(style) + ']'
cells = [
    cell('两体矢量散射：直接振幅与 AFH 对照', 'Title'),
    cell('从上到下依次按 Shift+Enter。本文建立一个对角矢量耦合的独立两体基准，并不把它当作原模型的三体过程。所有截面单位为 GeV^-3；运行前请确认同目录上一级存在 dmformfactor-V6.m。', 'Text'),
    cell('一、物理模型与比较范围', 'Section'),
    cell('模型：gχ Vμ χ̄ γμ χ + gN Vμ N̄ γμ N，取质子和中子耦合相等。直接方法由领先阶矢量电荷振幅得到 dσ/dER = mA (gχ gN)^2 R(E_R) / [2π v² (mV² + 2 mA ER)²]。AFH 方法则设置质子和中子的 O1 系数，再调用 DiffCrossSection。两边共同使用 AFH 核密度数据，因此这不是对核结构数据的独立验证。', 'Text'),
    cell('二、设置参数并加载 AFH', 'Section'),
    cell('请修改下面的 mChi、mV、gChi、gN、speedKms 和 recoilValues。此对照选 Xe-131。mA 采用 AFH 内部的 A × 0.938272 GeV；速度采用 AFH 自带的 km/s 换算。', 'Text'),
    cell(head, 'Input'),
    cell('三、逐点比较两种方法', 'Section'),
    cell('AFH 将无量纲 c1 除以 (246.2 GeV)^2；为保留矢量传播子的动量依赖，每个 ER 单独设置 c1 = gχ gN (246.2 GeV)^2/(mV²+q²)。先比较 AFH 的原始核响应，再比较原三体程序采用的 R(0)=A² 归一化。', 'Text'),
    cell(tail, 'Input'),
    cell('四、读结果', 'Section'),
    cell('每一行依次为 ER、AFH 截面、直接公式截面、直接公式相对差、A² 归一化截面、归一化截面相对差。PASS 表示原始响应的各点相对差低于 10^-8。数值接近响应零点时相对差可能更敏感。此对照只验证该两体领先阶匹配，不能证明三体振幅或相空间正确。', 'Text'),
]
(folder / 'Elastic_Vector_AFH_vs_Direct.nb').write_text('Notebook[{\n' + ',\n'.join(cells) + '\n}, WindowTitle -> "Elastic Vector Comparison", StyleDefinitions -> "Default.nb"]\n', encoding='ascii')
