"""端到端冒烟测试：mock DeepSeek 响应，验证选文→精读→渲染→索引全链路。"""

import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src import llm  # noqa: E402

MOCK_READING = {
    "title_cn": "植物可变剪接的功能景观扩展",
    "summary": "本文综述了植物中可变剪接的最新进展，涵盖其调控机制、功能多样性与前沿研究方法。背景是植物基因表达调控中可变剪接的重要性日益凸显，核心内容系统梳理了剪接因子与剪接体组装、剪接决定细胞命运与胁迫响应、以及长读长测序等新技术带来的新认识。主要结论认为可变剪接是植物适应环境与发育的重要调控层，并展望了单细胞水平与空间转录组时代的剪接研究新范式。",
    "key_points": [
        "可变剪接在植物基因表达调控中的核心地位",
        "剪接因子调控网络决定组织与发育阶段特异性剪接",
        "胁迫响应中的剪接重编程",
        "长读长测序推动剪接异构体全景图谱",
        "剪接调控为作物改良提供新靶点",
    ],
    "bilingual_table": [
        {"en": "Alternative splicing is a key layer of gene expression regulation in plants, controlling development and stress responses.",
         "zh": "可变剪接是植物基因表达调控的关键层级，控制发育与胁迫响应。"},
        {"en": "The expanding functional landscape of alternative splicing in plants highlights its role in phenotypic plasticity.",
         "zh": "植物可变剪接功能景观的扩展凸显了其在表型可塑性中的作用。"},
    ],
    "glossary": [
        {"term": "Alternative splicing (AS)", "zh": "可变剪接",
         "note": "同一前体 mRNA 通过不同剪接方式产生多种成熟 mRNA 异构体，扩大蛋白质组多样性。"},
        {"term": "Spliceosome", "zh": "剪接体",
         "note": "催化前体 mRNA 剪接的核糖核蛋白复合体，由多种小核核糖核蛋白组成。"},
    ],
    "frontier_assessment": "本文发表于 Trends in Biochemical Sciences，紧跟长读长测序与单细胞技术重塑植物剪接研究的最新浪潮，属于领域前沿。当前处于技术驱动的认识加速期，局限在于全转录组剪接图谱仍以组织平均为主，单细胞分辨率不足；未来单细胞剪接定量与空间剪接图谱有望成为新范式。",
    "keywords": ["alternative splicing", "plants", "RNA biology"],
}


def fake_call(cfg, system, user):
    return json.dumps(MOCK_READING, ensure_ascii=False)


def main() -> int:
    llm.call_deepseek = fake_call
    llm.deep_read = lambda cfg, paper, text, label: dict(MOCK_READING)

    import src.main as m
    rc = m.main()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())