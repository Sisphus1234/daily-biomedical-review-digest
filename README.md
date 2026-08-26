# 每日生物医学综述精读 + 每日考研词汇

每天自动从 **PubMed** 精选一篇最近发表的**前沿综述（Review）**，用 **DeepSeek** 生成中文精读材料，包括：中文概要、核心要点、**中英对照精读表**、**专业术语标注表**、前沿性点评。结果以 Markdown 存入 `notes/` 并自动提交到 git 仓库。

同时每天按**考研真题词频**生成 **15 个考研词汇**学习卡片（IPA 音标 + 中英释义 + 例句 + DeepSeek 考点提示），存入 `vocab/` 并自动提交。

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
├── .github/workflows/daily.yml   # 每日精读定时任务
├── .github/workflows/vocab.yml   # 每日考研词汇定时任务
├── src/
│   ├── config.py                 # 环境变量配置
│   ├── pubmed.py                 # PubMed/Europe PMC 拉取
│   ├── scoring.py                # 前沿性打分与生物医学筛选
│   ├── llm.py                    # DeepSeek 精读
│   ├── render.py                 # Markdown 渲染与索引
│   ├── main.py                   # 精读流水线入口
│   ├── vocab_main.py             # 词汇流水线入口
│   └── vocab/                    # 词汇模块（选词/词典API/精读/渲染）
├── prompts/deep_reader.txt       # 精读提示词（可自行调整）
├── notes/                        # 每日精读输出 + 索引
├── vocab/                        # 每日考研词汇输出 + 索引
├── data/seen.json                # 已读 PMID 记录
├── data/netem_full_list.json     # 考研词频表（5530 词，来源见下）
├── data/vocab_progress.json      # 词汇学习进度
├── data/vocab_dict_cache.json    # 词典释义缓存
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

## 每日考研词汇

每天 08:00（北京时间）自动按**真题词频**推送考研词汇，高频优先，自动跳过已掌握的 CET-4 基础词。**手机网页版**（GitHub Pages，每天更新，只保留当天词汇）：

> https://sisphus1234.github.io/daily-biomedical-review-digest/vocab.html

每次运行只保留**当天**的单词文件（前一天自动删除），Markdown 存于 `vocab/YYYY-MM-DD.md`，网页存于根目录 `vocab.html`。

### 本地运行

```powershell
python -m src.vocab_main --dry-run    # 只看今天会选哪些词
python -m src.vocab_main              # 正式生成（词典 API + DeepSeek）
python -m src.vocab_main --commit     # 生成后自动 git 提交推送
```

### 输出示例

`vocab/2026-08-26.md` 每个单词包含：词频排名、IPA 音标、中文释义（DeepSeek 精读）、英文释义与例句（Free Dictionary API）、考点提示（熟词僻义/固定搭配）、今日学习建议。

### 数据与进度

- 词表：`data/netem_full_list.json`，5530 个考研大纲词按词频降序（来源 [exam-data/NETEMVocabulary](https://github.com/exam-data/NETEMVocabulary)，CC BY-NC-SA 4.0；前 2444 个为高频词）
- 进度：`data/vocab_progress.json` 记录已学到第几个词，按天推进，到表尾自动回绕
- 词典缓存：`data/vocab_dict_cache.json`，避免重复请求

### 词汇参数

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `VOCAB_PER_DAY` | `15` | 每天单词数 |
| `VOCAB_START` | `0` | 起始位置（0 = 从最高频开始） |
| `VOCAB_SKIP_WORDS` | 内置基础词表 | 追加跳过的基础词（逗号分隔，如 `a,the`） |
| `VOCAB_SKIP_CET4` | `true` | 是否跳过 CET-4 已掌握词汇（`false` 则全部推送） |

> 说明：牛津词典官方 API 需付费 key 无免费额度，故英文释义使用免费开源的 Free Dictionary API（Wiktionary 词源），中文释义由 DeepSeek 精读生成，二者结合。
> CET-4 词表来源 [mahavivo/english-wordlists](https://github.com/mahavivo/english-wordlists)（`data/cet4_words.txt`，4531 词）。

## 许可

MIT