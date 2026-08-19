"""端到端冒烟测试：mock DeepSeek 响应，验证选文→精读→渲染→索引全链路。"""

import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src import llm  # noqa: E402

MOCK_READING = {
    "title_cn": "GLP-1受体激动剂治疗阿尔茨海默病：试验教训与转化挑战",
    "summary": "阿尔茨海默病（AD）是一种多因素疾病，需要超越淀粉样蛋白清除的联合治疗策略。GLP-1受体激动剂在神经保护方面有强大机制基础和流行病学支持，但在症状性AD的大型随机试验中未显示临床获益。本文回顾试验教训，探讨从临床前研究到临床转化的挑战，包括剂量、生物利用度、患者选择、结局指标和试验设计等问题。",
    "key_points": [
        "AD是多因素疾病，需要联合治疗策略。",
        "GLP-1受体激动剂在神经保护方面有机制和流行病学证据。",
        "大型随机试验在症状性AD中未显示临床获益。",
        "试验阴性结果可能受剂量、患者选择和结局指标影响。",
        "转化挑战包括血脑屏障通透性和药物暴露。",
        "未来需优化试验设计和生物标志物分层。",
        "GLP-1受体激动剂可能对特定AD亚群有效。",
        "需要更多研究探索联合治疗和长期效果。",
    ],
    "deep_sections": [
        {
            "title": "1. 背景与问题：为什么需要超越淀粉样蛋白策略？",
            "sections_en_zh": [
                {"en": "Alzheimer's disease (AD) is a multifactorial disorder that requires combined therapeutic strategies beyond amyloid clearance.",
                 "zh": "阿尔茨海默病（AD）是一种多因素疾病，需要超越淀粉样蛋白清除的联合治疗策略。", },
                {"en": "Although GLP-1 receptor agonists show strong mechanistic rationale and supportive epidemiological signals for neuroprotection, large randomized trials in symptomatic AD have yielded negative clinical outcomes and do not support the therapeutic use in AD.",
                 "zh": "尽管GLP-1受体激动剂显示出强有力的机制依据和流行病学支持信号，表明其具有神经保护作用，但在症状性AD中的大型随机试验却产生了阴性临床结果，不支持其在AD中的治疗应用。", },
            ],
            "deep_dive": "AD的病理机制远比单一的β-淀粉样蛋白级联假说复杂。过去十年针对淀粉样蛋白的单抗药物（如aducanumab、lecanemab）虽获加速批准，但临床获益有限且伴随淀粉样蛋白相关影像学异常（ARIA）风险。GLP-1受体激动剂代表了一条完全不同的干预思路：它不直接清除淀粉样蛋白，而是通过改善代谢、抗炎和线粒体功能作用于神经退行性变的上游过程。这种代谢-神经保护轴正是AD与糖尿病共病机制的核心。",
        },
        {
            "title": "2. 机制基础：GLP-1受体的神经保护通路",
            "sections_en_zh": [
                {"en": "GLP-1 receptor agonists exert neuroprotection via multiple mechanisms including reducing neuroinflammation, improving mitochondrial function, enhancing synaptic plasticity, and promoting neurogenesis.",
                 "zh": "GLP-1受体激动剂通过多种机制发挥神经保护作用，包括减少神经炎症、改善线粒体功能、增强突触可塑性和促进神经发生。", },
            ],
            "deep_dive": "GLP-1受体在脑内广泛表达，尤其在海马、下丘脑等认知相关脑区。其激动剂通过激活PI3K/AKT和cAMP/PKA通路增强胰岛素信号敏感性，抑制tau蛋白磷酸化，并调节自噬清除蛋白聚集体。",
        },
        {
            "title": "3. 临床证据：从流行病学到随机对照试验",
            "sections_en_zh": [
                {"en": "Epidemiological data show that diabetic patients using GLP-1 receptor agonists have reduced risk of AD, providing supportive evidence for its use in AD therapy.",
                 "zh": "流行病学数据显示，使用GLP-1受体激动剂的糖尿病患者患AD的风险降低，为其在AD治疗中的应用提供了支持性证据。", },
            ],
            "deep_dive": "真实世界研究显示，二甲双胍联合GLP-1受体激动剂的糖尿病患者，AD发病率显著低于未使用者。但观察性研究存在残余混杂因素，如健康使用者偏倚。这提醒读者区分相关性与因果性，是循证医学的核心素养。",
        },
        {
            "title": "4. 转化挑战与未来方向",
            "sections_en_zh": [
                {"en": "Future research should focus on earlier stages of AD, biomarker-guided patient stratification, and combination therapy strategies.",
                 "zh": "未来研究应聚焦于AD早期阶段、生物标志物分层和联合治疗策略。", },
            ],
            "deep_dive": "转化医学的核心挑战在于时间窗口：一旦认知症状出现，神经元损伤已不可逆。未来设计试验需从症状性AD前移至高危人群进行预防性干预，并采用生物标志物分层。",
        },
    ],
    "original_excerpts": [
        {"en": "Alzheimer's disease (AD) is a multifactorial disorder that requires combined therapeutic strategies beyond amyloid clearance. The disease is driven by complex interactions between amyloid-beta accumulation, tau hyperphosphorylation, neuroinflammation, insulin resistance, and mitochondrial dysfunction. Therefore, single-target approaches targeting amyloid have proven insufficient, and the field is increasingly moving toward combination strategies that address multiple pathological axes simultaneously.",
         "zh": "阿尔茨海默病（AD）是一种多因素疾病，需要超越淀粉样蛋白清除的联合治疗策略。该病由β-淀粉样蛋白积聚、tau蛋白过度磷酸化、神经炎症、胰岛素抵抗和线粒体功能障碍之间的复杂相互作用驱动。因此，单一靶向淀粉样蛋白的策略已被证明不足，该领域正日益转向同时处理多个病理轴的联合策略。", },
    ],
    "bilingual_table": [
        {"en": "Alzheimer's disease (AD) is a multifactorial disorder that requires combined therapeutic strategies beyond amyloid clearance.",
         "zh": "阿尔茨海默病（AD）是一种多因素疾病，需要超越淀粉样蛋白清除的联合治疗策略。", },
        {"en": "Although GLP-1 receptor agonists show strong mechanistic rationale and supportive epidemiological signals for neuroprotection, large randomized trials in symptomatic AD have yielded negative clinical outcomes and do not support the therapeutic use in AD.",
         "zh": "尽管GLP-1受体激动剂显示出强有力的机制依据和流行病学支持信号，表明其具有神经保护作用，但在症状性AD中的大型随机试验却产生了阴性临床结果，不支持其在AD中的治疗应用。", },
    ],
    "glossary": [
        {"term": "Alzheimer's disease (AD)", "zh": "阿尔茨海默病", "note": "一种进行性神经退行性疾病，以认知功能障碍和记忆丧失为主要特征。", },
        {"term": "GLP-1 receptor agonists", "zh": "GLP-1受体激动剂", "note": "胰高血糖素样肽-1受体激动剂，最初用于治疗2型糖尿病，现研究其神经保护作用。", },
        {"term": "amyloid clearance", "zh": "淀粉样蛋白清除", "note": "指清除大脑中β-淀粉样蛋白沉积的过程，是AD治疗的传统靶点。", },
        {"term": "neuroprotection", "zh": "神经保护", "note": "保护神经元免受损伤或死亡，以维持神经功能的策略。", },
        {"term": "randomized trials", "zh": "随机试验", "note": "将受试者随机分配到不同治疗组以比较疗效的临床试验。", },
        {"term": "symptomatic AD", "zh": "症状性AD", "note": "已表现出认知或功能症状的阿尔茨海默病阶段。", },
        {"term": "translational challenges", "zh": "转化挑战", "note": "将基础研究结果转化为临床应用过程中遇到的困难。", },
        {"term": "blood-brain barrier", "zh": "血脑屏障", "note": "保护大脑的选择性通透屏障，也阻碍药物入脑。", },
        {"term": "biomarkers", "zh": "生物标志物", "note": "指示疾病状态或疗效的生物学指标。", },
        {"term": "neuroinflammation", "zh": "神经炎症", "note": "中枢神经系统的炎症反应，参与AD病理过程。", },
        {"term": "patient stratification", "zh": "患者分层", "note": "根据生物标志物或临床特征将患者分组以优化治疗。", },
        {"term": "insulin resistance", "zh": "胰岛素抵抗", "note": "细胞对胰岛素反应减弱，与AD风险增加相关。", },
    ],
    "frontier_assessment": "该论文聚焦于GLP-1受体激动剂在AD治疗中的转化挑战，时效性与前沿性俱佳。尽管大型随机试验结果阴性，但文章强调了机制基础和流行病学证据，提示该类药物在AD预防和特定亚群中的潜在价值。当前研究处于从基础向临床转化的关键阶段，主要局限在于药物脑内递送不足和试验设计不完善。未来需要开发更有效的递送系统、优化患者分层和结局指标，并探索联合治疗策略。",
    "keywords": ["Alzheimer's disease", "GLP-1 receptor agonists", "neuroprotection", "clinical trials", "translational challenges"],
}


def fake_call(cfg, system, user):
    return json.dumps(MOCK_READING, ensure_ascii=False)


def main() -> int:
    llm.call_deepseek = fake_call
    llm.deep_read = lambda cfg, paper, text, label: dict(MOCK_READING)

    import src.main as m
    return m.main()


if __name__ == "__main__":
    raise SystemExit(main())