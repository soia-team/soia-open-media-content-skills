# imagegen provider 选择与派发

`render_engine: imagegen` 时按此顺序取 provider；manifest 必须记录实际用到的 provider 与真实输出尺寸。

## 顺序

1. **宿主内置 imagegen 工具**：有就直接用。
2. **codex 内置 gpt-image-2**：宿主没有 imagegen 时，经 `soia-dev-agent-cli-dispatch` 派发 codex 出图；**不要跳过这层直接降级 html_render**。
3. **降级 `html_render`**：以上都不可用才降级，降级原因写进 manifest（例如「宿主无 imagegen，codex 不可用」）。

## codex gpt-image-2 派发

按 `soia-dev-agent-cli-dispatch` 的 codex 规范执行；要点：

- prompt 先写入 `${TMPDIR:-/tmp}/soia-dev-agent-cli-dispatch/<task-id>/prompt.txt`，再以 `$(cat …)` 传入。
- 产物落在工作区之外（例如 `~/Downloads` 下的交付目录）时**必须用去沙箱模式**，否则写入被拒、文件只能落到临时目录：

```bash
codex exec --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check \
  "$(cat "${TMPDIR:-/tmp}/soia-dev-agent-cli-dispatch/<task-id>/prompt.txt")"
```

- 去沙箱模式需要客户明确授权（系统级或本次任务级），不是默认状态。
- 长执行进程禁止由 codex 启动（codex exec 会话结束会杀死其子进程）；出图本身是短任务，不受此限。

## gpt-image-2 尺寸约束（实测 + 二进制内置校验）

- 宽高须为 **16 的倍数**；长边 ≤ **3840px**；长短边比 ≤ **3:1**；总像素 **655,360–8,294,400**。
- 3:4 的 1080×1440 与 2160×2880 均合法。
- **实际返回尺寸可能与请求不符**（实测请求 2160×2880 曾返回 1086×1448 再被放大、也曾原生返回 1080×1440）。必须回读真实像素记入 manifest，不能用请求值冒充；放大稿要标注 `upscaled_from`。

## 能力边界（2026-08-07 实测更新）

gpt-image-2 对**中文密集排版**的能力已可用于生产：实测一张含三列四行表格、
版本号（20 / 22 / 22.19 / 20.19.0）、彩色胶囊标签的信息卡，文字与数字全部逐字正确。
旧结论「imagegen 只出素材、中文密集排版必须 HTML」针对的是上一代模型，**不再作为路由依据**。

仍然不变的是验收：一次正确不等于每次正确，`view_image` 逐图核对文字、数字、
比例与禁项照旧执行；命令行、URL、版本号等高风险字段核对失败时，该图重生或改走
`hybrid_exact_text`，不得带病通过。
