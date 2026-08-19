"""端到端冒烟测试：mock DeepSeek 响应，验证选文→精读→渲染→索引全链路。"""

import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src import llm  # noqa: E402

MOCK_READING = {
    "title_cn": "GLP-1受体激动剂治疗阿尔茨海默病：试验教训与转化挑战",
    "summary": "阿尔茨海默病（AD）是一种多因素疾病，其病理机制复杂，涉及β-淀粉样蛋白沉积、tau蛋白过度磷酸化、神经炎症、胰岛素抵抗和线粒体功能障碍等。因此，单一靶向淀粉样蛋白的治疗策略可能不足以应对疾病的全貌，需要联合治疗策略。近年来，胰高血糖素样肽-1（GLP-1）受体激动剂因其在2型糖尿病中的代谢调节作用而受到关注，并展现出神经保护潜力。临床前研究表明，GLP-1受体激动剂可通过多种机制发挥神经保护作用，包括减少神经炎症、改善线粒体功能、增强突触可塑性、促进神经发生，并可能通过调节胰岛素信号通路影响淀粉样蛋白代谢。流行病学数据显示，使用GLP-1受体激动剂的糖尿病患者患AD的风险降低，这为将其用于AD治疗提供了支持性证据。然而，在症状性AD患者中进行的大型随机对照试验（如EXCEEL和ELAD研究）未能显示出显著的临床获益，主要终点（如认知和功能量表评分）未达到预期改善。这些阴性结果提示，GLP-1受体激动剂可能对早期或无症状阶段更有效，或者需要更长的治疗周期和更敏感的结局指标。此外，试验设计中的局限性，如患者选择、剂量、给药途径和生物标志物分层等，也可能影响结果。本文回顾了GLP-1受体激动剂在AD中的机制基础、临床前证据和临床试验结果，分析了转化失败的可能原因，并提出了未来研究方向，包括在AD早期阶段进行试验、采用精准医学方法、结合生物标志物进行患者分层，以及探索联合治疗策略。尽管目前证据不支持在症状性AD中常规使用GLP-1受体激动剂，但其在AD预防和早期干预中的潜力仍需进一步探索。",
    "key_points": [
        "AD是多因素疾病，需要联合治疗策略，而非仅清除淀粉样蛋白。",
        "GLP-1受体激动剂具有神经保护作用的机制基础，包括抗炎、改善线粒体功能和突触可塑性。",
        "流行病学数据支持GLP-1受体激动剂可能降低AD风险，但大型随机试验在症状性AD中未显示临床获益。",
        "试验阴性结果可能归因于患者选择、治疗时机、剂量和结局指标等因素。",
        "未来研究应聚焦于AD早期阶段、生物标志物分层和联合治疗策略。",
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
            "deep_dive": "AD的病理机制远比单一的β-淀粉样蛋白级联假说复杂。过去十年针对淀粉样蛋白的单抗药物（如aducanumab、lecanemab）虽获加速批准，但临床获益有限且伴随淀粉样蛋白相关影像学异常（ARIA）风险。GLP-1受体激动剂代表了一条完全不同的干预思路：它不直接清除淀粉样蛋白，而是通过改善代谢、抗炎和线粒体功能作用于神经退行性变的上游过程。这种代谢-神经保护轴正是AD与糖尿病共病机制的核心。读者需要思考：单靶点策略的失败是否意味着机制假设本身错误，还是试验设计（患者分期、终点选择）的问题？这是理解本文结论的关键前提。",
        },
        {
            "title": "2. 机制基础：GLP-1受体的神经保护通路",
            "sections_en_zh": [
                {"en": "GLP-1 receptor agonists exert neuroprotection via multiple mechanisms including reducing neuroinflammation, improving mitochondrial function, enhancing synaptic plasticity, and promoting neurogenesis.",
                 "zh": "GLP-1受体激动剂通过多种机制发挥神经保护作用，包括减少神经炎症、改善线粒体功能、增强突触可塑性和促进神经发生。", },
            ],
            "deep_dive": "GLP-1受体在脑内广泛表达，尤其在海马、下丘脑等认知相关脑区。其激动剂通过激活PI3K/AKT和cAMP/PKA通路增强胰岛素信号敏感性，抑制tau蛋白磷酸化，并调节自噬清除蛋白聚集体。近年来研究还发现其在血脑屏障通透性方面存在差异，这解释了为何部分药物（如liraglutide）的临床结果优于其他药物。理解这些机制差异，有助于解释临床试验结果的不一致性，也为联合用药提供了分子层面的理论基础。",
        },
        {
            "title": "3. 临床证据：从流行病学到随机对照试验",
            "sections_en_zh": [
                {"en": "Epidemiological data show that diabetic patients using GLP-1 receptor agonists have reduced risk of AD, providing supportive evidence for its use in AD therapy.",
                 "zh": "流行病学数据显示，使用GLP-1受体激动剂的糖尿病患者患AD的风险降低，为其在AD治疗中的应用提供了支持性证据。", },
            ],
            "deep_dive": "真实世界研究显示，二甲双胍联合GLP-1受体激动剂的糖尿病患者，AD发病率显著低于未使用者。这种效应可能并非直接神经保护，而是通过改善血管危险因素（高血压、高血糖）间接保护大脑。但观察性研究存在残余混杂因素，如健康使用者偏倚（healthy-user bias）。本文作者明确指出，这些数据只能作为hypothesis-generating，不能替代随机对照试验的直接证据。这提醒读者区分相关性与因果性，是循证医学的核心素养。",
        },
        {
            "title": "4. 转化挑战与未来方向",
            "sections_en_zh": [
                {"en": "Future research should focus on earlier stages of AD, biomarker-guided patient stratification, and combination therapy strategies.",
                 "zh": "未来研究应聚焦于AD早期阶段、生物标志物分层和联合治疗策略。", },
            ],
            "deep_dive": "转化医学的核心挑战在于时间窗口：一旦认知症状出现，神经元损伤已不可逆，药物干预为时已晚。未来设计试验需从症状性AD前移至高危人群（如载脂蛋白E4携带者）进行预防性干预，并采用PET淀粉样蛋白、血液p-tau217等生物标志物分层。联合治疗方向包括GLP-1受体激动剂联合抗淀粉样蛋白抗体、减重手术、运动干预等多维策略。本文为这种精准医疗范式提供了坚实的理论基础。",
        },
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
        {"term": "mechanistic rationale", "zh": "机制依据", "note": "基于生物学机制的理论支持，解释药物可能有效的原理。", },
        {"term": "epidemiological signals", "zh": "流行病学信号", "note": "来自人群研究的数据提示，可能表明药物暴露与疾病风险之间的关联。", },
        {"term": "translational challenges", "zh": "转化挑战", "note": "将基础研究结果转化为临床应用过程中遇到的困难。", },
        {"term": "multifactorial disorder", "zh": "多因素疾病", "note": "由多种遗传和环境因素共同作用导致的疾病。", },
    ],
    "frontier_assessment": "该论文聚焦于GLP-1受体激动剂在AD治疗中的前沿应用，反映了当前AD研究从单一靶点向多靶点联合治疗转变的趋势。尽管临床前和流行病学证据支持其潜力，但大型随机试验的阴性结果凸显了转化医学的挑战。该领域处于探索阶段，主要局限在于试验设计可能未充分考虑AD的异质性和治疗时机。未来展望包括在AD早期或高风险人群中进行预防性试验，利用生物标志物进行患者分层，以及探索与其他药物（如抗淀粉样蛋白抗体）的联合治疗。该研究为AD治疗策略的优化提供了重要参考。",
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