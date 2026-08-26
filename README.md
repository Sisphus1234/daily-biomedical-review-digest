# 每日生物医学综述精读

每天自动从 **PubMed** 精选一篇最近发表的**前沿综述（Review）**，用 **DeepSeek** 生成中文精读材料，包括：中文概要、核心要点、**中英对照精读表**、**专业术语标注表**、前沿性点评。结果以 Markdown 存入 `notes/` 并自动提交到 git 仓库。

> 架构灵感参考自 [research-radar](https://github.com/Prezblublu-Sun/research-radar)（arXiv+PubMed 拉取 + LLM 打分的自动化流水线）。

## 功能特性

- 每日定时（GitHub Actions cron，默认每天 09:17 北京时间）自动运行
- 数据源：NCBI PubMed E-utilities（官方接口，无需爬虫）
- 时效新：只看最近 5 天内发表的 Review（可配置）
- 行业前端：按期刊权威度（Nature Reviews / Science / Cell / NEJM 等加分）+ 前沿关键词 打分
- 生物医学聚焦：标题+摘要命中生物医学关键词才入选，排除明显非医学期刊
- 全文优先：命中开放获取（PMC）的综述自动抓全文精读，否则退化为摘要精读
- 中英对照精读表 + 专业术语表（DeepSeek 生成，JSON 结构化）
- 去重：`data/seen.json` 记录已读 PMID，避免重复
- 零服务器成本：GitHub Actions 免费额度 + 每天约 1-2 万 token 的 DeepSeek 调用（约 ¥0.1-0.3/天）

## 目录结构

```
.
├── .github/workflows/daily.yml   # 每日定时任务
├── src/
│   ├── config.py                 # 环境变量配置
│   ├── pubmed.py                 # PubMed/Europe PMC 拉取
│   ├── scoring.py                # 前沿性打分与生物医学筛选
│   ├── llm.py                    # DeepSeek 精读
│   ├── render.py                 # Markdown 渲染与索引
│   └── main.py                   # 流水线入口
├── prompts/deep_reader.txt       # 精读提示词（可自行调整）
├── notes/                        # 每日精读输出 + 索引
├── data/seen.json                # 已读 PMID 记录
├── .env.example                  # 环境变量示例
└── requirements.txt
```

## 快速开始

### 1. 本地运行

```powershell
# 准备环境变量
Copy-Item .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY 和 PUBMED_EMAIL

# 安装依赖
python -m pip install -r requirements.txt

# 试运行（不调用 LLM，只看今天会选哪篇）
python -m src.main --dry-run

# 正式运行（生成精读 Markdown 并提交 git）
python -m src.main --commit
```

### 2. 部署到 GitHub（启用每日自动运行）

1. 在 GitHub 创建仓库并推送本目录代码
2. 仓库 Settings → Secrets and variables → Actions 配置以下密钥：
   - **Secrets**（机密，仅可写入不可读取）：
     - `DEEPSEEK_API_KEY` — DeepSeek 的 API Key（[platform.deepseek.com](https://platform.deepseek.com) 申请）
     - `PUBMED_EMAIL` — 你的邮箱（NCBI 要求）
     - `NCBI_API_KEY`（可选）— [NCBI 免费申请](https://www.ncbi.nlm.nih.gov/account/settings/)，提高接口限额
   - **Variables**（可选项）：
     - `DEEPSEEK_MODEL` — 默认 `deepseek-chat`
     - `LOOKBACK_DAYS` — 默认 `5`
     - `RETMAX` — 默认 `30`
3. 推送后到 Actions 页面手动触发一次 `Daily Biomedical Review Digestion` 验证

## 参数说明

| 环境变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `DEEPSEEK_API_KEY` | 是 | - | DeepSeek API Key |
| `PUBMED_EMAIL` | 是 | - | NCBI 要求提供的邮箱 |
| `DEEPSEEK_MODEL` | 否 | `deepseek-chat` | DeepSeek 模型名 |
| `DEEPSEEK_BASE_URL` | 否 | `https://api.deepseek.com` | OpenAI 兼容接口地址 |
| `NCBI_API_KEY` | 否 | - | NCBI E-utilities API Key |
| `LOOKBACK_DAYS` | 否 | `5` | 回溯最近 N 天的综述 |
| `RETMAX` | 否 | `30` | 每次检索的候选数 |
| `GIT_COMMIT` | 否 | `false` | 是否自动 git 提交推送 |
| `MAX_TEXT_CHARS` | 否 | `20000` | 喂给 LLM 的最大原文字符数 |

## 命令行参数

```
python -m src.main [--date YYYY-MM-DD] [--dry-run] [--force] [--commit]
```

- `--date`：指定精读日期（默认今天，影响文件名前缀）
- `--dry-run`：只做选文不调用 LLM，用于测试
- `--force`：忽略 `data/seen.json` 去重记录
- `--commit`：完成后自动 `git commit` + `git push`

## 输出示例

`notes/2026-08-19-42613270-the-expanding-functional-landscape-of-alternative-splicing-in-plants.md` 包含：

1. 文章信息（标题、期刊、DOI、PMID、作者）
2. 中文概要（500-800 字）
3. 核心要点（5-8 条）
4. 中英对照精读表（8-15 条原文↔译文）
5. 专业术语表（10-20 条术语 + 中文译名 + 解释）
6. 前沿性与时效性点评
7. 关键词

## 自定义精读提示词

编辑 `prompts/deep_reader.txt` 即可调整精读风格、篇幅、对照粒度等，改完提交后次日生效。

## 许可

MIT