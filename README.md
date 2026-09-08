# 小米运动步数修改脚本 (Xiaomi MiFit Step Modifier)

[![Python](https://img.shields.io/badge/Python-3.6%2B-brightgreen.svg)](https://www.python.org/)

一个用于自动修改小米运动（MiFit / Zepp Life）步数的 Python 脚本，支持多账号、随机步数、微信（Server酱）与 Telegram 推送通知。支持 **GitHub Actions**、**本地运行**、**阿里云函数计算** 三种方式。

**⚠️ 注意：本项目仅供学习和研究使用，修改步数可能违反小米运动的使用条款，造成的任何后果由用户自行承担。**

## 功能特点

- **自动修改步数**：在步数范围内随机生成步数并上传至 Zepp Life。
- **多账号支持**：账号 / 密码用 `#` 分隔，可批量修改。
- **微信 / Telegram 推送**：运行结果实时推送（可选）。
- **网络容错**：请求自动重试、双域名兜底、UTC 日期自动校正为东八区。

## 环境变量说明

| 变量名 | 描述 | 示例值 | 是否必填 |
|-------------------|------------------------------------|--------------------------|----------|
| `MI_USER` | 账号（手机号或邮箱），多账号用 `#` 分隔 | `user1#user2` | 是 |
| `MI_PASSWD` | 密码，多账号用 `#` 分隔（`MI_PASSWORD` 亦可） | `pass1#pass2` | 是 |
| `STEP_MIN` | 每日步数最小值（`MI_MIN_STEPS` 亦可） | `8000` | 否 |
| `STEP_MAX` | 每日步数最大值（`MI_MAX_STEPS` 亦可） | `20000` | 否 |
| `MI_SENDKEY` | Server酱 SendKey，微信推送 | `SCTxxxx` | 否 |
| `XM_TG_BOT_TOKEN` | Telegram Bot Token | `123456:ABCdef` | 否 |
| `XM_TG_USER_ID` | Telegram 用户 ID | `123456789` | 否 |

> 提示：请在 Zepp Life APP「我的 → 第三方接入」中绑定微信 / 支付宝后，步数才能同步过去。

## 方式一：GitHub Actions（推荐）

1. Fork / 使用本仓库，进入仓库 **Settings → Secrets and variables → Actions → New repository secret**，添加：
   - `MI_USER`：你的账号
   - `MI_PASSWD`：你的密码
   - `STEP_MIN` / `STEP_MAX`（可选）：步数范围
   - `MI_SENDKEY`（可选）：微信推送
2. 进入 **Actions** 页面，若首次提示启用 workflow，点击 *I understand my workflows, go ahead and enable them*。
3. 选择「修改小米运动步数」→ **Run workflow** 手动触发测试；之后每天北京时间 09:00 / 17:00 自动运行。

## 方式二：本地运行

```bash
pip install requests

# Windows (cmd)
set MI_USER=你的账号
set MI_PASSWD=你的密码
python my_mi_step.py

# Linux / macOS
export MI_USER=你的账号
export MI_PASSWD=你的密码
python my_mi_step.py
```

运行失败时脚本退出码为 1，便于定时任务判断。

## 方式三：阿里云函数计算

部署本文件为函数，入口函数填 `my_mi_step.main_handler`，通过定时触发器调用。账号可通过函数环境变量或触发事件 JSON 传入：

```json
{"user": "xx@qq.com", "password": "xxx", "minSteps": 17760, "maxSteps": 23659}
```

## 注意事项

- **合法使用**：仅供学习研究，禁止用于商业、欺诈或非法行为。
- **账号安全**：不要把账号密码硬编码进代码，务必使用环境变量 / GitHub Secrets。
- **接口限制**：请求过于频繁会触发 429 限流，脚本已内置重试与多账号间隔。
- **登录失败**：检查账号密码是否正确；建议使用邮箱注册的 Zepp Life 账号。

## 免责声明

本项目仅供学习交流使用，不对任何使用后果负责。小米运动的 API 属于小米公司所有，本项目不保证接口的长期可用性，且不与小米公司有任何关联。
