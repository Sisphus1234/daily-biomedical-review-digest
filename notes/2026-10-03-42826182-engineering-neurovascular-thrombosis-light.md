# Engineering neurovascular thrombosis: Light-based bioprinting for patient-specific modeling and women's cerebrovascular health.

> **每日精读 · 2026-10-03** ｜ **类型：摘要精读** ｜ 原文来源：PubMed 摘要 ｜ 阅读时长：约 10-15 分钟

## 文章信息

| 项目 | 内容 |
| --- | --- |
| 中文标题 | 工程化神经血管血栓形成：基于光学的生物打印用于患者特异性建模与女性脑血管健康 |
| 期刊 | Science advances |
| 发表日期 | 2026/10/02 |
| 作者 | Dei-Awuku L, Yap NA, Zhao YC, et al. (13 authors) |
| DOI | [10.1126/sciadv.aeh3952](https://doi.org/10.1126/sciadv.aeh3952) |
| PMID | [42826182](https://pubmed.ncbi.nlm.nih.gov/42826182/) |

---

## 一、文章概览

本文是一篇发表于《Science Advances》的前沿观点（Perspective）文章，聚焦于两种女性高发的脑血管疾病——脑静脉窦血栓形成（cerebral venous sinus thrombosis, CVST）与颈动脉蹼（carotid web, CW），提出以光学三维生物打印技术构建患者特异性血栓模型的新范式。文章指出，CVST与CW虽在解剖位置和临床表现上不同，但共享一个核心病理机制：血管几何形态异常、血流动力学紊乱（disturbed hemodynamics）与内皮细胞激活（endothelial activation）三者相互作用，共同驱动血栓形成。然而，这两种疾病长期被研究不足，根本原因在于传统体外模型无法复现复杂的三维管腔轮廓（three-dimensional lumen profiles），导致病理血流环境难以被真实还原。作者提出，基于光学的光刻生物制造策略——特别是数字光处理（digital light processing, DLP）与体积生物打印（volumetric bioprinting）——能够制造封闭、可灌注的水凝胶网络，并具备高保真表面形貌。将这些打印结构整合入动态的血管芯片（vessel-on-chip）灌注回路，并结合临床影像与计算流体力学（computational fluid dynamics, CFD）指导，可模拟病理性血流停滞与再循环区、非均一剪切应力梯度以及位点特异性细胞聚集。该生物制造路径有望实现个性化疾病建模与具有转化价值的风险评估，为推进女性脑血管健康提供关键平台。文章属于观点性综述，未提供原始实验数据，其核心贡献在于提出技术整合框架与研究议程。

## 二、核心要点

1. CVST与CW是两种不同的脑血管疾病，但均以血管几何、血流动力学紊乱与内皮激活的交互作用为血栓驱动核心。
2. 两种疾病均不成比例地影响女性，但因传统平台无法复现复杂三维管腔轮廓而长期研究不足。
3. 光学三维生物打印（DLP与体积生物打印）可制造封闭、可灌注的水凝胶网络，具备高保真表面形貌。
4. 将打印结构整合入动态血管芯片灌注回路，可模拟病理性血流停滞、再循环区与非均一剪切应力梯度。
5. 临床影像与计算流体力学（CFD）为打印模型提供患者特异性几何与血流边界条件。
6. 该平台可模拟位点特异性细胞聚集，实现个性化疾病建模。
7. 该技术路径有望用于转化相关的风险评估，而非仅停留在基础机制研究。
8. 文章定位为Perspective，提出技术整合框架与研究议程，而非报告原始实验数据。
9. 女性脑血管健康是该研究的核心应用导向，强调性别差异在疾病建模中的重要性。
10. 光学生物打印与器官芯片、CFD的跨学科整合是推动患者特异性血栓建模的关键方向。

## 三、分节深度解读（10-15 分钟精读）

### 1. 背景与问题：被忽视的女性脑血管血栓疾病

**英文原文：**

> Cerebral venous sinus thrombosis (CVST) and carotid web (CW) are distinct cerebrovascular disorders where vascular geometry, disturbed hemodynamics, and endothelial activation interact to drive thrombosis.


**中文翻译：**

> 脑静脉窦血栓形成（CVST）与颈动脉蹼（CW）是两种不同的脑血管疾病，其血栓形成由血管几何形态、血流动力学紊乱与内皮激活三者相互作用所驱动。


**英文原文：**

> Both conditions disproportionately affect women, yet remain understudied because of the inability of traditional platforms to replicate complex three-dimensional lumen profiles.


**中文翻译：**

> 这两种疾病均不成比例地影响女性，但由于传统平台无法复现复杂的三维管腔轮廓，相关研究仍显不足。


> **深度解读：** 本节确立了全文的问题意识：CVST与CW在解剖与临床上是两种不同疾病，但被作者归入同一病理逻辑框架——血管几何、血流动力学与内皮激活的三角互动。这一归纳具有启发性：它提示血栓形成并非单一分子事件，而是力学—几何—细胞三者耦合的结果。更关键的是，作者点出了研究不足的结构性原因：传统体外平台（如二维培养、简单微流控）无法复现复杂三维管腔轮廓，因而无法真实还原病理性血流环境。这一判断切中当前血栓建模的核心瓶颈。值得注意的是，作者特别强调两种疾病对女性的不成比例影响，将性别差异置于研究议程中心，这既呼应了女性健康研究的政策趋势，也提示未来模型必须纳入性别相关变量（如激素、血管壁特性）。批判性思考：将CVST与CW并置是否过度简化？两者在静脉与动脉系统中的血流参数差异巨大，统一建模框架需谨慎处理边界条件。


### 2. 机制与方法：光学生物打印与动态灌注回路的整合

**英文原文：**

> This perspective positions light-based lithography as a powerful biofabrication strategy for patient-specific modeling.


**中文翻译：**

> 本观点文章将基于光学的光刻技术定位为一种用于患者特异性建模的强大生物制造策略。


**英文原文：**

> Digital light processing and volumetric bioprinting render enclosed, perfusable hydrogel networks with high-fidelity surface topography.


**中文翻译：**

> 数字光处理与体积生物打印可构建封闭、可灌注的水凝胶网络，并具备高保真表面形貌。


**英文原文：**

> When integrated into dynamic vessel-on-chip perfusion loops guided by clinical imaging and computational fluid dynamics, these platforms simulate pathological flow stasis and recirculation zones, heterogeneous shear-stress gradients, and site-specific cellular aggregation.


**中文翻译：**

> 当整合入由临床影像与计算流体力学指导的动态血管芯片灌注回路时，这些平台可模拟病理性血流停滞与再循环区、非均一剪切应力梯度以及位点特异性细胞聚集。


> **深度解读：** 本节是全文的技术核心。作者提出两条技术路线的整合：一是光学生物打印（DLP与体积生物打印），二是动态血管芯片灌注回路。DLP通过逐层光固化实现高分辨率结构，体积生物打印则通过旋转照射在数秒至数十秒内成型，二者均能制造封闭、可灌注的水凝胶网络，这是传统挤出式打印难以实现的。高保真表面形貌对血栓建模至关重要，因为内皮表面的微观几何直接影响局部剪切应力分布与细胞行为。进一步，作者强调将打印结构嵌入动态灌注回路，并由临床影像与CFD提供边界条件，从而复现血流停滞、再循环区与非均一剪切应力梯度。这一整合思路的亮点在于“影像—计算—制造—灌注”的闭环：影像提供患者几何，CFD预测血流热点，打印复现几何，灌注验证假设。批判性思考：水凝胶的力学与光学特性是否能长期承受动态灌注？内皮化与血液相容性仍是未解难题，文章未提供具体解决方案。


### 3. 核心发现与证据：观点性框架而非原始数据

**英文原文：**

> This biofabrication approach enables personalized disease modeling and translationally relevant risk assessment, providing a critical platform for advancing women's cerebrovascular health.


**中文翻译：**

> 该生物制造方法可实现个性化疾病建模与具有转化价值的风险评估，为推进女性脑血管健康提供关键平台。


> **深度解读：** 需要明确指出，本文为Perspective（观点）文章，其“核心发现”并非实验数据，而是一个技术整合框架与研究议程。作者的核心主张是：光学生物打印结合动态灌注与CFD，能够实现个性化疾病建模与转化相关的风险评估。这一主张的证据基础来自对现有技术能力的综述与逻辑推演，而非新实验。因此，读者应将其视为“路线图”而非“验证结果”。从证据等级看，该框架尚处于概念验证前的阶段，其可行性依赖于多个技术模块的成熟度：打印分辨率、水凝胶生物相容性、内皮化、血液灌注稳定性、CFD与实测流场的吻合度等。批判性思考：文章未讨论模型验证标准（如与临床血栓样本的组织学对比），也未涉及样本量与统计设计，这些是未来从观点走向实证必须补齐的环节。


### 4. 临床意义与应用：从机制研究到风险评估

**英文原文：**

> This biofabrication approach enables personalized disease modeling and translationally relevant risk assessment.


**中文翻译：**

> 该生物制造方法可实现个性化疾病建模与具有转化价值的风险评估。


**英文原文：**

> providing a critical platform for advancing women's cerebrovascular health.


**中文翻译：**

> 为推进女性脑血管健康提供关键平台。


> **深度解读：** 本节讨论该平台的临床转化潜力。作者提出两个应用方向：个性化疾病建模与转化相关的风险评估。前者意味着用患者自身影像数据打印其血管几何，在体外复现其血栓倾向；后者意味着该平台可能用于评估个体化抗栓策略或器械干预效果。这一设想若实现，将改变当前CVST与CW的管理模式——从群体化经验治疗转向个体化风险分层。尤其对女性患者，该平台可纳入激素、妊娠、口服避孕药等性别相关因素，弥补传统模型忽视性别差异的缺陷。批判性思考：转化路径仍面临监管与标准化挑战，例如如何定义“患者特异性模型”的验证终点、如何确保批次间一致性、以及成本效益是否支持临床常规使用。文章未展开这些实施细节，属于展望性表述。


### 5. 挑战与局限：技术整合的未解难题

**英文原文：**

> yet remain understudied because of the inability of traditional platforms to replicate complex three-dimensional lumen profiles.


**中文翻译：**

> 但由于传统平台无法复现复杂的三维管腔轮廓，相关研究仍显不足。


> **深度解读：** 文章虽以观点性框架为主，但其对局限的暗示值得深挖。首先，传统平台无法复现三维管腔轮廓是已知瓶颈，但光学打印是否完全解决这一问题仍需验证——打印分辨率与真实血管内皮的微观形貌之间仍有差距。其次，文章未讨论血液相容性、内皮化稳定性、长期灌注下的血栓自发形成等关键问题。第三，CFD模拟依赖假设（如牛顿流体、刚性壁），而真实血管具有弹性与搏动性，这些差异可能影响剪切应力预测的准确性。第四，性别差异的纳入需要生物学依据，而不仅是统计关联。批判性思考：该框架的成败取决于跨学科整合的深度，而非单一技术的突破。未来研究应优先建立标准化验证流程，包括与临床样本的对比、流场实测与CFD的吻合度评估，以及多中心可重复性测试。


### 6. 展望：走向患者特异性血栓建模的路线图

**英文原文：**

> This perspective positions light-based lithography as a powerful biofabrication strategy for patient-specific modeling.


**中文翻译：**

> 本观点文章将基于光学的光刻技术定位为一种用于患者特异性建模的强大生物制造策略。


**英文原文：**

> When integrated into dynamic vessel-on-chip perfusion loops guided by clinical imaging and computational fluid dynamics, these platforms simulate pathological flow stasis and recirculation zones, heterogeneous shear-stress gradients, and site-specific cellular aggregation.


**中文翻译：**

> 当整合入由临床影像与计算流体力学指导的动态血管芯片灌注回路时，这些平台可模拟病理性血流停滞与再循环区、非均一剪切应力梯度以及位点特异性细胞聚集。


> **深度解读：** 展望部分的核心是“整合”二字：光学打印提供几何，血管芯片提供生理灌注，临床影像提供患者特异性，CFD提供血流预测。作者将其描绘为一条从影像到制造再到验证的闭环路线。这一愿景的前沿性在于它跨越了生物制造、器官芯片、计算流体力学与女性健康四个领域。未来方向可能包括：多细胞共培养（内皮、平滑肌、血小板）、搏动性灌注、以及人工智能辅助的CFD快速求解。批判性思考：路线图的实现需要解决标准化、规模化与监管三大问题。此外，女性脑血管健康的强调应转化为具体的研究设计，例如纳入月经周期、妊娠状态等变量。总体而言，本文的价值在于提出议程而非给出答案，其影响力将取决于后续实证研究能否兑现这一框架。


## 四、原文精读摘录（学英语/看综述写作）

### 原文摘录 1

**英文原文：**

> Cerebral venous sinus thrombosis (CVST) and carotid web (CW) are distinct cerebrovascular disorders where vascular geometry, disturbed hemodynamics, and endothelial activation interact to drive thrombosis. Both conditions disproportionately affect women, yet remain understudied because of the inability of traditional platforms to replicate complex three-dimensional lumen profiles. This perspective positions light-based lithography as a powerful biofabrication strategy for patient-specific modeling.


**中文翻译：**

> 脑静脉窦血栓形成（CVST）与颈动脉蹼（CW）是两种不同的脑血管疾病，其血栓形成由血管几何形态、血流动力学紊乱与内皮激活三者相互作用所驱动。这两种疾病均不成比例地影响女性，但由于传统平台无法复现复杂的三维管腔轮廓，相关研究仍显不足。本观点文章将基于光学的光刻技术定位为一种用于患者特异性建模的强大生物制造策略。


### 原文摘录 2

**英文原文：**

> Digital light processing and volumetric bioprinting render enclosed, perfusable hydrogel networks with high-fidelity surface topography. When integrated into dynamic vessel-on-chip perfusion loops guided by clinical imaging and computational fluid dynamics, these platforms simulate pathological flow stasis and recirculation zones, heterogeneous shear-stress gradients, and site-specific cellular aggregation.


**中文翻译：**

> 数字光处理与体积生物打印可构建封闭、可灌注的水凝胶网络，并具备高保真表面形貌。当整合入由临床影像与计算流体力学指导的动态血管芯片灌注回路时，这些平台可模拟病理性血流停滞与再循环区、非均一剪切应力梯度以及位点特异性细胞聚集。


### 原文摘录 3

**英文原文：**

> This biofabrication approach enables personalized disease modeling and translationally relevant risk assessment, providing a critical platform for advancing women's cerebrovascular health.


**中文翻译：**

> 该生物制造方法可实现个性化疾病建模与具有转化价值的风险评估，为推进女性脑血管健康提供关键平台。


## 五、中英对照精读表

| 英文原文 | 中文对照 |
| --- | --- |
| Cerebral venous sinus thrombosis (CVST) and carotid web (CW) are distinct cerebrovascular disorders | 脑静脉窦血栓形成（CVST）与颈动脉蹼（CW）是两种不同的脑血管疾病 |
| where vascular geometry, disturbed hemodynamics, and endothelial activation interact to drive thrombosis | 其血栓形成由血管几何形态、血流动力学紊乱与内皮激活三者相互作用所驱动 |
| Both conditions disproportionately affect women | 这两种疾病均不成比例地影响女性 |
| yet remain understudied because of the inability of traditional platforms to replicate complex three-dimensional lumen profiles | 但由于传统平台无法复现复杂的三维管腔轮廓，相关研究仍显不足 |
| This perspective positions light-based lithography as a powerful biofabrication strategy for patient-specific modeling | 本观点文章将基于光学的光刻技术定位为一种用于患者特异性建模的强大生物制造策略 |
| Digital light processing and volumetric bioprinting render enclosed, perfusable hydrogel networks with high-fidelity surface topography | 数字光处理与体积生物打印可构建封闭、可灌注的水凝胶网络，并具备高保真表面形貌 |
| When integrated into dynamic vessel-on-chip perfusion loops guided by clinical imaging and computational fluid dynamics | 当整合入由临床影像与计算流体力学指导的动态血管芯片灌注回路时 |
| these platforms simulate pathological flow stasis and recirculation zones | 这些平台可模拟病理性血流停滞与再循环区 |
| heterogeneous shear-stress gradients | 非均一剪切应力梯度 |
| and site-specific cellular aggregation | 以及位点特异性细胞聚集 |
| This biofabrication approach enables personalized disease modeling and translationally relevant risk assessment | 该生物制造方法可实现个性化疾病建模与具有转化价值的风险评估 |
| providing a critical platform for advancing women's cerebrovascular health | 为推进女性脑血管健康提供关键平台 |

## 六、专业术语表

| 术语 | 中文译名 | 简要解释 |
| --- | --- | --- |
| Cerebral venous sinus thrombosis (CVST) | 脑静脉窦血栓形成 | 脑静脉窦内血栓形成，导致静脉回流受阻，可引发头痛、癫痫甚至颅内出血。 |
| Carotid web (CW) | 颈动脉蹼 | 颈动脉分叉处内膜的薄层纤维隔膜，可造成局部血流紊乱并增加隐源性卒中风险。 |
| Vascular geometry | 血管几何形态 | 血管的管径、弯曲度、分叉角度等三维结构特征，直接影响局部血流模式。 |
| Disturbed hemodynamics | 血流动力学紊乱 | 血流速度、方向与剪切应力异常，常表现为停滞、再循环与涡流。 |
| Endothelial activation | 内皮激活 | 内皮细胞在力学或炎症刺激下表达黏附分子与促凝因子，促进血栓形成。 |
| Thrombosis | 血栓形成 | 血管内血液凝固形成血栓的过程，可导致缺血或栓塞。 |
| Three-dimensional lumen profiles | 三维管腔轮廓 | 血管内腔的立体形态，包括直径变化、分支与表面微观起伏。 |
| Light-based lithography | 基于光学的光刻技术 | 利用光固化原理制造三维结构的技术，包括DLP与体积打印。 |
| Biofabrication | 生物制造 | 利用工程与材料手段制造具有生物功能的组织或器官模型。 |
| Patient-specific modeling | 患者特异性建模 | 基于个体影像或生物学数据构建的定制化疾病模型。 |
| Digital light processing (DLP) | 数字光处理 | 通过数字微镜逐层投射光图案固化树脂或水凝胶的打印技术。 |
| Volumetric bioprinting | 体积生物打印 | 通过多角度光照射在体积内一次性固化成型，速度远快于逐层打印。 |
| Perfusable hydrogel networks | 可灌注水凝胶网络 | 具有连通通道、可通液体的亲水聚合物网络，用于模拟血管。 |
| High-fidelity surface topography | 高保真表面形貌 | 打印结构表面能精确复现目标血管的微观几何特征。 |
| Vessel-on-chip | 血管芯片 | 在微流控芯片上构建的血管模型，可施加生理或病理血流。 |
| Perfusion loops | 灌注回路 | 使液体在体外模型中循环流动的管路系统。 |
| Computational fluid dynamics (CFD) | 计算流体力学 | 用数值方法求解流体运动方程，预测血流速度、压力与剪切应力。 |
| Flow stasis | 血流停滞 | 局部血流速度极低或停滞，是血栓形成的经典危险因素。 |
| Recirculation zones | 再循环区 | 血流在几何突变处形成的回流或涡流区域，易促发血栓。 |
| Shear-stress gradients | 剪切应力梯度 | 血流对血管壁施加的摩擦力在空间上的变化，影响内皮功能。 |
| Site-specific cellular aggregation | 位点特异性细胞聚集 | 细胞在特定血流或几何位置聚集，模拟血栓起始部位。 |
| Translationally relevant risk assessment | 具有转化价值的风险评估 | 可直接指导临床决策的个体化风险评价。 |
| Women's cerebrovascular health | 女性脑血管健康 | 关注女性特有的脑血管疾病风险与机制的研究领域。 |
| Perspective | 观点文章 | 学术期刊中的一种文章类型，提出新框架或议程，通常不含原始数据。 |

## 七、前沿性与时效性点评

本文发表于《Science Advances》，属于观点性文章（Perspective），其前沿性体现在将光学三维生物打印、血管芯片、计算流体力学与女性脑血管健康四个领域进行整合，提出患者特异性血栓建模的技术路线图。CVST与CW均为女性高发但研究不足的疾病，传统模型无法复现三维管腔轮廓是核心瓶颈，因此该框架具有明确的问题导向。当前该领域处于概念提出与早期技术整合阶段，DLP与体积生物打印已在组织工程中展示能力，但将其用于血栓建模并整合动态灌注与CFD，尚缺乏系统性验证。主要局限包括：文章未提供原始实验数据，未讨论水凝胶血液相容性、内皮化稳定性、长期灌注下的自发血栓形成等关键问题；CFD假设（牛顿流体、刚性壁）与真实血管存在差异；性别差异的纳入尚停留在倡导层面。未来展望应聚焦于建立标准化验证流程，包括与临床血栓样本的组织学对比、流场实测与CFD的吻合度评估、多中心可重复性测试，以及纳入激素与妊娠等性别相关变量。总体而言，本文的价值在于提出议程而非给出答案，其影响力将取决于后续实证研究能否兑现这一框架。

## 八、关键词

cerebral venous sinus thrombosis, carotid web, neurovascular thrombosis, light-based bioprinting, digital light processing, volumetric bioprinting, vessel-on-chip, computational fluid dynamics, women's cerebrovascular health, patient-specific modeling

---

*本精读由 DeepSeek 自动生成，仅供参考，请以原文为准。*
