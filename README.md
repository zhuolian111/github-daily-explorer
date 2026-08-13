# GitHub Daily Explorer

每天从近期活跃的 GitHub 仓库里挑出最多 3 个真正值得点开的项目：科研探索、工程成长、今日整活各一个。它不是 Trending 搬运工，也不按 star 数简单排队；候选会经过历史去重、轻量质量预筛和模型判断，最后生成 3～5 分钟能读完的中文 HTML/纯文本邮件。

## 它怎样工作

```text
多组 GitHub Search 查询 → 去掉历史推荐 → 平衡三个类别
→ 只为约 15 个短名单读取 README → 模型输出严格 JSON
→ 渲染 HTML + 纯文本 → SMTP 发送成功 → 写入 history.json
```

先发送、后记历史很重要：如果 QQ 邮箱临时失败，下一次重试不会误以为这些项目已经推荐过。模型可以少选低质量类别，但不能为了凑数乱选，也不能选候选池之外的仓库。

## 文件结构

```text
.
├── .github/workflows/daily.yml       # 每天 08:00 和手动运行入口
├── config/topics.yaml                # 兴趣查询和候选规模
├── data/history.json                 # 永久去重记录
├── src/github_daily_explorer/
│   ├── app.py                        # 流程编排和事务边界
│   ├── collector.py                  # 候选收集、预筛、README 短名单
│   ├── github_client.py              # GitHub REST API
│   ├── selector.py                   # OpenAI-compatible 模型调用和校验
│   ├── renderer.py                   # HTML / plain text
│   ├── mailer.py                     # QQ SMTP SSL
│   ├── history.py                    # 历史去重和原子写入
│   └── models.py                     # 数据结构
├── tests/
├── .env.example
├── main.py
└── pyproject.toml
```

## 本地运行

需要 Python 3.11 或更新版本。

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

把 `.env.example` 作为变量清单，但不要提交 `.env`。本项目不会自动读取 `.env`，这是刻意的：避免凭据被工具或日志意外带出。请在当前 shell 中设置环境变量，或使用你信任的 secrets 工具。

PowerShell 示例（只在当前窗口生效）：

```powershell
$env:MODEL_PROVIDER = "openai"
$env:MODEL_API_KEY = "你的密钥"
$env:MODEL_NAME = "gpt-4.1-mini"
$env:SMTP_USER = "你的QQ邮箱"
$env:SMTP_AUTH_CODE = "QQ邮箱生成的SMTP授权码"
$env:DIGEST_TO = "收件地址"
```

本地访问 GitHub 时 `GITHUB_TOKEN` 可选；匿名额度较低，频繁测试时建议设置一个仅在本机使用的 token。GitHub Actions 会自动提供仓库内置的 `GITHUB_TOKEN`，无需额外创建 Personal Access Token。

先运行安全预览：

```bash
python main.py --dry-run
```

它会真实搜索 GitHub、调用模型，并把结果写到 `output/digest-YYYY-MM-DD.html` 和 `.txt`；不会连接 SMTP，也不会修改历史。确认预览后，完整运行：

```bash
python main.py
```

完整运行会发信；只有发送成功后才更新 `data/history.json`。

## 选择 OpenAI 或 DeepSeek

两者都走 OpenAI-compatible `/chat/completions` 接口，provider 没有写死。

| 变量 | OpenAI 示例 | DeepSeek 示例 |
|---|---|---|
| `MODEL_PROVIDER` | `openai` | `deepseek` |
| `MODEL_NAME` | `gpt-4.1-mini` | `deepseek-chat` |
| `MODEL_BASE_URL` | 可省略，默认 `https://api.openai.com/v1` | 可省略，默认 `https://api.deepseek.com` |
| `MODEL_API_KEY` | 对应平台密钥 | 对应平台密钥 |

如果使用兼容代理或自建网关，才需要设置 `MODEL_BASE_URL`。不要把 key 写进代码、命令行参数、配置文件或 issue。

## 配置 QQ 邮箱 SMTP

1. 在 QQ 邮箱设置中开启 SMTP 服务并生成授权码。授权码不是 QQ 登录密码。
2. 设置 `SMTP_USER`、`SMTP_AUTH_CODE`、`DIGEST_TO`。
3. 默认使用 `smtp.qq.com:465` 和 SSL；一般不需要设置 `SMTP_HOST`、`SMTP_PORT`。
4. 先执行 `python main.py --dry-run` 检查内容。它不会测试 SMTP。
5. 要真正测试 SMTP，只能执行 `python main.py`。这会发送一封真实邮件，并在成功后写历史。

程序不会记录授权码；认证错误只会提示检查账号和授权码，不会把服务器响应或凭据输出到日志。

## 配置 GitHub Actions

在 GitHub 仓库页面依次打开 **Settings → Secrets and variables → Actions → New repository secret**。Secrets 是加密变量，工作流运行时才注入，适合保存凭据。

必须创建这些 **Repository secrets**：

- `MODEL_PROVIDER`：`openai` 或 `deepseek`
- `MODEL_API_KEY`：对应模型服务密钥
- `MODEL_NAME`：实际模型名
- `SMTP_USER`：QQ 邮箱地址
- `SMTP_AUTH_CODE`：QQ SMTP 授权码
- `DIGEST_TO`：收件地址

可选 secret：

- `MODEL_BASE_URL`：只有使用自定义地址时才需要；为空时根据 provider 使用默认值

可选的非敏感 **Repository variables**：

- `SMTP_HOST`：默认 `smtp.qq.com`
- `SMTP_PORT`：默认 `465`

不要自己创建 `GITHUB_TOKEN` secret。Actions 会为每次运行自动生成它；工作流只给它 `contents: write`，用于读取 API 和提交 `history.json`。

### 手动测试 Action

推送代码后打开 **Actions → GitHub Daily Explorer → Run workflow → Run workflow**。`workflow_dispatch` 就是这个按钮的来源。先观察 “Generate and send digest” 是否成功，再确认 “Commit recommendation history” 产生了 bot commit。

定时表达式 `0 0 * * *` 使用 UTC，对应中国/新加坡时间每天 08:00。GitHub 的定时任务可能有几分钟排队延迟，不保证卡秒执行。

如果默认分支启用了保护规则，bot push 可能被拒绝。需要允许 GitHub Actions 写入默认分支，或调整保护规则；邮件已经发出但历史提交失败时，应先手工保留当次 `history.json`，避免以后重复。

## 修改兴趣和探索范围

编辑 `config/topics.yaml`：

- `queries` 决定三个类别分别搜什么；采用 GitHub Search 语法。
- `lookback_days` 决定“近期活跃”的时间窗。
- `candidate_pool_size` 控制粗候选目标。
- `readme_shortlist_size` 控制真正读取 README 的数量，也是模型 token 成本的主要旋钮。

建议每类保留 2～4 个不同方向的 query。扩大兴趣时替换其中一条，而不是不断追加；这样既保留约 20%～30% 的探索，又不会大量消耗 API 配额。历史去重是永久的；若确实想重新推荐某仓库，手工从 `data/history.json` 删除对应条目并提交。

## 测试

```bash
pytest
```

测试覆盖历史去重、模型 JSON 和类别约束、HTML 转义与手机 viewport、SMTP 缺失配置、dry-run 不发信/不改历史、发送失败不写历史，以及 GitHub 空结果。

## 常见故障

- **GitHub API rate limit**：本地设置 `GITHUB_TOKEN`；Actions 内无需处理。也可减少 query 或短名单规模。
- **模型返回非法 JSON**：换用支持 JSON mode 的模型，确认 `MODEL_NAME` 正确；程序会拒绝不完整或越权选择，不会发送半成品。
- **模型 API 401/403**：检查 provider、key、model 和自定义 base URL 是否属于同一服务。日志不会显示 key。
- **QQ SMTP 认证失败**：确认使用 SMTP 授权码而非 QQ 密码，并检查 SMTP 服务是否开启。
- **dry-run 没有生成文件**：如果没有新候选，或模型判断所有候选都不合格，程序会正常结束但不生成空日报；查看日志说明。
- **history 无法自动 push**：检查仓库 Actions 的 Workflow permissions 是否允许读写，以及默认分支保护。邮件发送与 push 是两个步骤。
- **连续出现相似方向**：调整 `topics.yaml`，将某条过窄 query 替换为 scientific workflow、visualization 或跨领域主题。模型提示已降低知名项目权重，但候选池仍决定它能看到什么。

## 安全边界

`.env`、输出预览、缓存和虚拟环境已加入 `.gitignore`。代码不会接受命令行 secret，也不会把 secret 写入邮件、历史或日志。提交前仍建议运行 `git diff --cached`，确认没有误加入本地凭据。

