---
name: douyin-comments
description: 使用 playwright-cli 打开抖音视频详情页，激活评论面板，提取当前可抓取的评论并保存到桌面文件。
---

# Skill: douyin-comments

用于抓取抖音 PC 页面视频详情中的评论内容，并将结果保存到桌面文件。

本技能适合以下目标：

- 获取某条抖音视频的前 N 条评论
- 尽可能多地抓取当前页面可访问到的评论
- 将评论保存到桌面文本文件
- 对已抓到的评论进行整理、总结或分类

## 触发条件

当用户出现以下任一意图时使用本技能：

- 获取抖音评论
- 抓取某条抖音视频评论
- 保存抖音评论到桌面
- 总结评论区说了什么
- 导出评论

如果用户提供的是这类链接，也优先考虑本技能：

- `https://www.douyin.com/jingxuan?modal_id=...`
- 含 `modal_id` 的抖音详情页链接

## 固定工作方式

- 必须使用 `playwright-cli`。
- 优先复用当前浏览器会话，不要频繁切换到别的页面。
- 如果评论区需要登录才能展开，优先复用用户现有登录态。
- 不要假设一定能拿到“全部评论”；必须先验证页面实际能否继续懒加载。
- 如果平台限制导致无法完整抓取，必须如实说明“当前能稳定抓到的数量”。

## 本次已验证的有效流程

以下流程已在当前环境中验证有效：

1. 打开抖音详情页：

```bash
playwright-cli goto "https://www.douyin.com/jingxuan?modal_id=<MODAL_ID>"
```

2. 确认页面是否进入详情层，而不是只停在精选首页。

优先检查：

- 页面标题是否变成具体视频标题
- 页面里是否出现 `评论`
- 页面里是否出现 `全部评论(数字)`

3. 如果评论面板已经存在，先检查评论相关 DOM：

```bash
playwright-cli --raw eval "(() => { const els = [...document.querySelectorAll('*')].filter(el => String(el.className||'').includes('comment')); return JSON.stringify(els.slice(0,30).map(el => ({cls:String(el.className), text:(el.innerText||'').slice(0,200)})), null, 2); })()"
```

4. 如果页面里已经有评论区标题，如：

- `评论`
- `全部评论(3142)`

说明评论面板已激活，可以继续提取。

5. 优先读取评论主容器文本，而不是依赖单条评论 DOM 完整结构。

本次实测可用的评论主容器特征：

- 类名含 `comment-mainContent`
- 容器可滚动，且 `scrollHeight > clientHeight`

示例：

```bash
playwright-cli --raw eval "(() => { const root = [...document.querySelectorAll('*')].find(el => String(el.className||'').includes('comment-mainContent') && el.clientHeight > 200); if (!root) return 'NO_ROOT'; return JSON.stringify({scrollTop: root.scrollTop, clientHeight: root.clientHeight, scrollHeight: root.scrollHeight, textLen: (root.innerText||'').length}); })()"
```

6. 提取可见评论时，不要直接按单个节点硬抓，应优先从 `innerText` 按固定模式解析。

本次验证出的可解析结构为：

```text
昵称
...
评论正文
时间前·地区
点赞数
分享
回复
```

因此可按以下逻辑识别评论：

- 第 1 行：昵称
- 第 2 行：固定为 `...`
- 第 3 行：正文
- 第 4 行：时间/地区，例如 `1天前·上海`
- 后面几行里出现纯数字时，视为点赞数

7. 解析时要跳过以下噪音文本：

- `大家都在搜：`
- `deepseek v4`
- `全部评论(...)`
- `留下你的精彩评论吧`
- `分享`
- `回复`
- `展开更多`
- `收起`
- `展开N条回复`
- 单独一行的 `...`

## 推荐提取脚本思路

本技能附带了一个可直接执行的脚本：

- `scripts/extract-comments.js`

用途：

- 自动打开抖音详情页
- 激活评论面板
- 多轮滚动评论容器
- 解析当前环境下可抓取的评论
- 将结果写入桌面文件

示例：

```bash
node "/Users/dds/data/ai/work/.claude/skills/douyin-comments/scripts/extract-comments.js" "https://www.douyin.com/jingxuan?modal_id=7632657462063140130"
```

自定义输出路径：

```bash
node "/Users/dds/data/ai/work/.claude/skills/douyin-comments/scripts/extract-comments.js" "https://www.douyin.com/jingxuan?modal_id=7632657462063140130" "/Users/dds/Desktop/comments.txt"
```

脚本执行完成后，会输出如下 JSON：

```json
{
  "count": 54,
  "outputPath": "/Users/dds/Desktop/douyin_comments_7632657462063140130.txt"
}
```

当前脚本状态说明：

- 已经具备完整的评论提取与桌面落盘逻辑
- 已修正为“评论面板未激活时直接失败”，不会再输出 `0 条评论` 的假成功结果
- 但抖音页面的“评论面板激活”仍然不够稳定，因此脚本当前更适合作为半自动脚本使用：
  - 先由用户或人工交互把评论面板真正打开
  - 再执行脚本抓取和保存

优先使用页面内脚本配合 `playwright-cli --raw eval` 或 `playwright-cli run-code`：

1. 找评论容器
2. 读取 `innerText`
3. 分行切分
4. 按固定模式解析评论项
5. 以 `昵称 + 正文 + 时间地区` 作为去重键

核心判断规则：

```js
const isMeta = s => /^(\d+小时前|\d+天前|\d+分钟前|昨天|今天)/.test(s) || /·/.test(s)
```

## 懒加载滚动策略

### 优先方案

优先直接修改评论容器的 `scrollTop`：

```js
root.scrollTop = Math.min(root.scrollTop + root.clientHeight - 30, root.scrollHeight)
```

每轮滚动后等待：

- `800ms - 1500ms`

### 次优方案

如果 `scrollTop` 有变化但文本不增长，再尝试真实鼠标滚轮：

```bash
playwright-cli mousemove <x> <y>
playwright-cli mousewheel 0 620
```

其中 `<x> <y>` 应落在评论面板中部偏上位置。

### 停止条件

以下任一情况成立时可停止：

- `scrollTop` 连续多轮不再变化
- `scrollHeight` 连续多轮不再增长
- 提取到的评论数量连续多轮不再增长
- 页面主动回收评论容器

## 保存到桌面

默认桌面输出文件：

- `/Users/dds/Desktop/douyin_comments_<MODAL_ID>.txt`
- `/Users/dds/Desktop/抖音评论_<MODAL_ID>.txt`

建议同时写两份，避免用户因文件名不易识别而找不到。

文件内容格式固定如下：

```text
Douyin comments for modal_id=<MODAL_ID>
Source: <URL>
Extracted comments: <COUNT>

1. 昵称
评论: 正文
时间/地区: 1天前·上海
点赞: 8
```

## 总结输出规则

如果用户要求“总结评论区在说什么”，优先按以下维度归纳：

- 支持派
- 质疑体验派
- 质疑营销派
- 行业延伸讨论

不要只机械罗列评论，要总结主流情绪和分歧点。

## 本次任务中确认过的限制

以下限制必须写进认知里：

1. 登录态不是唯一问题。
2. 抖音评论区在 PC 页面里使用虚拟列表和懒加载。
3. 即使 DOM 中出现 `全部评论(3142)`，也不代表可以一次性读到 3142 条。
4. 自动化环境下，评论接口或相关后台请求可能返回 `444`。
5. 当出现 `444` 时，说明平台对当前抓取方式有限制，不应继续声称“可以拿到全部评论”。
6. 在这种情况下，应该诚实输出：

```text
当前环境下已尽量抓取，实际稳定提取到 N 条评论，并已保存到桌面。
```

## 常见失败场景与处理

### 1. 页面只有精选首页，没有详情层

- 重新 `goto` 带 `modal_id` 的链接
- 检查标题是否变成具体视频标题

### 2. 页面有详情层，但评论面板未展开

- 查找 `评论`
- 如果存在则点击
- 再检查是否出现 `全部评论(...)`

### 3. 评论区存在，但单条 DOM 不完整

- 不要强依赖单条节点结构
- 改用评论容器 `innerText` 按模式解析

### 4. 滚动不生效

- 先改 `scrollTop`
- 再尝试 `mousemove + mousewheel`
- 每轮滚动后留足等待时间

### 5. 评论容器被回收或页面跳走

- 重新回到详情页
- 重新点击评论
- 重新定位评论容器
- 保留之前已抓到的数据，不要覆盖丢失

### 6. 后台接口被拦截或返回 444

- 不再承诺“全部评论”
- 输出当前能稳定抓到的数量
- 将结果保存到桌面文件

## 推荐执行顺序

1. 打开详情页
2. 激活评论面板
3. 读取评论容器文本
4. 解析首批评论
5. 进行多轮滚动和去重收集
6. 如果评论数继续增长，则继续滚动
7. 如果增长停止或接口受限，则结束抓取
8. 保存到桌面
9. 如用户要求，再做评论总结

## 最终交付要求

- 如果成功抓取到评论，必须写入桌面文件
- 必须明确告诉用户保存路径
- 必须明确当前提取数量
- 如果不是“全部评论”，必须直说是“当前环境下稳定抓到的评论”
