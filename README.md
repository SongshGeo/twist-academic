# twist-academic

在实验或脚本结束时，通过飞书群机器人 webhook 发一条通知。无第三方运行时依赖。

## 安装

```bash
pip install twist-academic
```

## 配置

在项目根目录创建 `.env`（安装后 `import twist_academic` 会自动加载当前工作目录下的 `.env`）：

```dotenv
TWIST_LARK_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/your-token
# 若机器人在飞书后台开启了签名校验：
# TWIST_LARK_SECRET=your_sign_secret
```

## 用法

```python
from twist_academic import notify

@notify
def train():
    ...

@notify(title="bert 微调")
def run_experiment():
    ...

# 直接发一条纯文本
notify("脚本已跑完，记得看结果。")
```

`@notify` 会在函数**正常结束或抛异常**后各发一条消息（含耗时、主机名；失败时带 traceback）。

## 集群 / 并行时避免刷屏

在 SLURM array、本地多进程等场景下，每个子任务若都 `@notify`，会产生大量重复消息。库会在以下情况**自动不发送**（`notify` / `maybe_notify` / `@notify` 均生效）：

| 条件 | 说明 |
|------|------|
| `SLURM_ARRAY_TASK_ID` 已设置 | SLURM array 的每个 task 默认静音；可用 SBATCH `--mail-type=END,FAIL` 收邮件 |
| `NO_NOTIFY=1`（或 `true` / `yes` / `on`） | 任意环境显式关闭通知，便于子进程或调试 |

```bash
# 子进程 / 单次调试不发飞书
export NO_NOTIFY=1
python worker.py
```

```python
from twist_academic import maybe_notify, notifications_suppressed

if not notifications_suppressed():
    notify("仅主进程汇总后发一条")

maybe_notify("与 notify(msg) 相同，受同一套静音规则约束")
```

## 测试

```bash
uv sync --dev
make test

# 向真实 webhook 发一条（需配置 TWIST_LARK_WEBHOOK）
pytest tests/test_notification.py -m integration
```

在 `pyproject.toml` 中已注册 `integration` marker。

## 开发

```bash
pre-commit run --all-files
uv build
```
