import { readFileSync, writeFileSync } from 'node:fs';

const target = '/Users/dds/data/ai/work/claude-code-context-architecture/index.html';
let html = readFileSync(target, 'utf8');

const slides = String.raw`
<section class="slide accent" data-layout="SWISS-COVER-ASCII" data-animate="hero">
  <div class="canvas-card">
    <canvas class="ascii-bg" aria-hidden="true"></canvas>
    <div class="chrome-min">
      <div class="l">CLAUDE CODE CONTEXT ARCHITECTURE</div>
      <div class="r">SS · 26.05.14 · 01 / 14</div>
    </div>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr auto;gap:2.6vh">
      <div data-anim="kicker" class="t-meta" style="color:rgba(255,255,255,.78);letter-spacing:.22em">CONTEXT ENGINEERING</div>
      <h1 data-anim="title" style="align-self:center;font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(8.2vw,14.5vh);line-height:.96;letter-spacing:-.025em;color:#fff">Claude Code<br/>上下文架构解析</h1>
      <div data-anim="bottom" style="display:grid;grid-template-rows:auto auto;gap:1.6vh;border-top:1px solid rgba(255,255,255,.22);padding-top:2vh">
        <div class="lead" style="max-width:58ch;color:rgba(255,255,255,.86);font-weight:300">AI 不是突然“失忆”，而是上下文窗口被撑爆。成熟系统靠四层防御，把每一条数据放到该去的位置。</div>
        <div style="display:flex;justify-content:space-between;align-items:end">
          <div class="t-meta" style="color:rgba(255,255,255,.6)">17 MIN VIDEO · TRANSCRIPT + SCREENSHOTS</div>
          <div class="t-meta" style="color:rgba(255,255,255,.6)">→ swipe / arrow keys</div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S03" data-animate="statement-rise">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">02 · WHY IT MATTERS</div>
      <div class="r">Problem Statement</div>
    </div>
    <div style="flex:1;padding:0;display:grid;grid-template-columns:4fr 8fr;gap:4vw;align-items:center">
      <div data-anim="left" style="display:flex;flex-direction:column;gap:2vh">
        <div class="t-meta">The symptom</div>
        <div style="height:2px;background:var(--accent);width:12vw"></div>
        <p class="lead" style="font-weight:300;color:var(--text-secondary)">跟 AI 做项目，聊着聊着它忘了刚改过的代码。这不一定是模型笨，而是上下文管理失控。</p>
      </div>
      <h2 data-anim="right" style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(7vw,12.2vh);line-height:.98;letter-spacing:-.03em">上下文不是篮子，<br/>是战略资源。</h2>
    </div>
  </div>
</section>

<section class="slide" data-layout="S22" data-animate="image-hero">
  <div class="canvas-card" style="padding:0;display:flex;flex-direction:column;overflow:hidden">
    <div data-anim="img" style="position:relative;flex:0 0 58%;overflow:hidden;background:var(--paper)">
      <img src="images/frame-01.jpg" data-image-slot="s22-hero-21x9" alt="视频目录截图" loading="eager" style="position:absolute;inset:0;width:100%;height:100%;object-fit:contain;object-position:center center;background:var(--paper)">
      <div class="chrome-min" style="position:absolute;top:0;left:0;right:0;color:var(--text-helper);padding:5.6vh 5vw 0">
        <div class="l">03 · MAP</div>
        <div class="r">Video Screenshot</div>
      </div>
      <div data-anim="title-block" style="position:absolute;left:5vw;top:11vh;background:var(--paper);padding:3.2vh 3.2vw;max-width:44vw">
        <div style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(4.9vw,8.5vh);line-height:1;letter-spacing:-.035em;color:var(--text-primary)">四层防御<br/>一层层兜底</div>
      </div>
    </div>
    <div data-anim="kpi" class="image-hero-body">
      <div style="max-width:48ch;font-family:var(--sans),var(--sans-zh);font-size:max(15px,1.24vw);line-height:1.55;font-weight:300;color:var(--text-primary)">视频把 Claude Code 的上下文管理拆成四层：微压缩、会话记忆压缩、完整压缩、自动触发。</div>
      <div class="image-hero-stats" style="gap:4vw">
        <div style="display:flex;flex-direction:column;gap:.6vh"><div style="height:1px;background:var(--ink)"></div><div class="t-meta">L1</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em">规则</div><p class="body-sm">低成本清理工具结果。</p></div>
        <div style="display:flex;flex-direction:column;gap:.6vh"><div style="height:1px;background:var(--ink)"></div><div class="t-meta">L2 / L3</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em">压缩</div><p class="body-sm">提取事实或完整降维。</p></div>
        <div style="display:flex;flex-direction:column;gap:.6vh"><div style="height:1px;background:var(--ink)"></div><div class="t-meta">L4</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em;color:var(--accent)">触发</div><p class="body-sm">自动检查、失败熔断。</p></div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S19" data-animate="four-cards">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">04 · FOUR LAYERS</div>
      <div class="r">Defense Stack</div>
    </div>
    <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh;border-top:2px solid var(--accent);padding-top:2.6vh">
      <div class="t-meta">机制总览</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.4vw,9.5vh);line-height:1;letter-spacing:-.03em">从便宜规则到重型压缩</h2>
    </div>
    <div data-anim="up" style="flex:1;display:grid;grid-template-columns:repeat(4,1fr);gap:1.6vw;margin-top:7vh;align-items:stretch">
      <article class="card-fill" style="padding:3vh 1.6vw;display:flex;flex-direction:column;gap:1.4vh"><div class="t-meta">— L1 / MICRO</div><h3 class="h-md">微压缩</h3><p class="t-body-sm">纯规则清理长工具输出，并保护 prompt cache 不失效。</p></article>
      <article class="card-fill" style="padding:3vh 1.6vw;display:flex;flex-direction:column;gap:1.4vh"><div class="t-meta">— L2 / MEMORY</div><h3 class="h-md">会话记忆</h3><p class="t-body-sm">后台 Agent 提取结构化事实，保留最近完整细节。</p></article>
      <article class="card-fill" style="padding:3vh 1.6vw;display:flex;flex-direction:column;gap:1.4vh"><div class="t-meta">— L3 / FULL</div><h3 class="h-md">完整压缩</h3><p class="t-body-sm">调用模型深度复盘，并在压缩后做上下文重建。</p></article>
      <article class="card-accent" style="padding:3vh 1.6vw;display:flex;flex-direction:column;gap:1.4vh"><div class="t-meta">— L4 / TRIGGER</div><h3 class="h-md" style="color:var(--accent-on)">自动触发</h3><p class="t-body-sm" style="color:rgba(255,255,255,.86)">超过阈值自动压缩，失败后熔断，避免无限烧 API。</p></article>
    </div>
  </div>
</section>

<section class="slide" data-layout="S22" data-animate="image-hero">
  <div class="canvas-card" style="padding:0;display:flex;flex-direction:column;overflow:hidden">
    <div data-anim="img" style="position:relative;flex:0 0 58%;overflow:hidden;background:var(--paper)">
      <img src="images/frame-02.jpg" data-image-slot="s22-hero-21x9" alt="微压缩截图" loading="eager" style="position:absolute;inset:0;width:100%;height:100%;object-fit:contain;object-position:center center;background:var(--paper)">
      <div class="chrome-min" style="position:absolute;top:0;left:0;right:0;color:var(--text-helper);padding:5.6vh 5vw 0"><div class="l">05 · L1 MICROCOMPACT</div><div class="r">Video Screenshot</div></div>
      <div data-anim="title-block" style="position:absolute;left:5vw;top:11vh;background:var(--paper);padding:3.2vh 3.2vw;max-width:42vw"><div style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(4.8vw,8.4vh);line-height:1;letter-spacing:-.035em;color:var(--text-primary)">微压缩：<br/>先动规则</div></div>
    </div>
    <div data-anim="kpi" class="image-hero-body">
      <div style="max-width:50ch;font-family:var(--sans),var(--sans-zh);font-size:max(15px,1.24vw);line-height:1.55;font-weight:300;color:var(--text-primary)">微压缩不调用模型，只清理白名单工具的长输出。真正的工程难点是既删除垃圾，又保住服务端 prompt cache。</div>
      <div class="image-hero-stats" style="gap:4vw">
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">COST</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em">≈0</div><p class="body-sm">规则执行，成本极低。</p></div>
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">CACHE</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em">保护</div><p class="body-sm">不破坏服务端前缀缓存。</p></div>
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">SCOPE</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em;color:var(--accent)">主线程</div><p class="body-sm">隔离子 Agent 结果。</p></div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S08" data-animate="duo-mirror">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">06 · MICROCOMPACT ROUTING</div><div class="r">Duo Compare</div></div>
    <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
      <div class="t-meta">一套双轨决策</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.4vw,9.5vh);line-height:1;letter-spacing:-.03em">缓存活着，别动本地前缀</h2>
    </div>
    <div class="duo-compare">
      <div class="col"><div class="col-tag"><span class="num">A</span> Cached Microcompact</div><div class="col-ttl">缓存仍然有效</div><p class="col-desc">通过专门 API 告诉服务端移除旧工具结果，本地聊天记录和缓存前缀保持不变。</p><ul class="col-list"><li>适合连续高频对话。</li><li>删掉旧结果但保留 prefix cache。</li><li>省钱，也更快。</li></ul></div>
      <span class="vrule"></span>
      <div class="col accent"><div class="col-tag"><span class="num">B</span> Hard Microcompact</div><div class="col-ttl">缓存已经过期</div><p class="col-desc">直接在本地改写历史，把冗长工具输出替换为简短占位符。</p><ul class="col-list"><li>适合用户离开一段时间后回来。</li><li>不再顾虑服务端缓存失效。</li><li>本地上下文立即变轻。</li></ul></div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S22" data-animate="image-hero">
  <div class="canvas-card" style="padding:0;display:flex;flex-direction:column;overflow:hidden">
    <div data-anim="img" style="position:relative;flex:0 0 58%;overflow:hidden;background:var(--paper)">
      <img src="images/frame-05.jpg" data-image-slot="s22-hero-21x9" alt="会话记忆截图" loading="eager" style="position:absolute;inset:0;width:100%;height:100%;object-fit:contain;object-position:center center;background:var(--paper)">
      <div class="chrome-min" style="position:absolute;top:0;left:0;right:0;color:var(--text-helper);padding:5.6vh 5vw 0"><div class="l">07 · L2 SESSION MEMORY</div><div class="r">Video Screenshot</div></div>
      <div data-anim="title-block" style="position:absolute;left:5vw;top:11vh;background:var(--paper);padding:3.2vh 3.2vw;max-width:46vw"><div style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(4.8vw,8.4vh);line-height:1;letter-spacing:-.035em;color:var(--text-primary)">不是摘要，<br/>是结构化事实</div></div>
    </div>
    <div data-anim="kpi" class="image-hero-body">
      <div style="max-width:50ch;font-family:var(--sans),var(--sans-zh);font-size:max(15px,1.24vw);line-height:1.55;font-weight:300;color:var(--text-primary)">第二层不把几十轮聊天粗暴压成几句话，而是由后台 Agent 提取项目事实、用户偏好和关键进度。</div>
      <div class="image-hero-stats" style="gap:4vw">
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">STORE</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em">Memory.md</div><p class="body-sm">长期事实文件。</p></div>
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">RECENT</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em">原文</div><p class="body-sm">最近几轮保留细节。</p></div>
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">GOAL</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em;color:var(--accent)">长期 + 眼前</div><p class="body-sm">宏观大局与当前动作都不丢。</p></div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S04" data-animate="six-cells">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">08 · BOUNDARY LOCK</div><div class="r">Six Cells</div></div>
    <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
      <div class="t-meta">会话记忆的结构边界</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.4vw,9.5vh);line-height:1;letter-spacing:-.03em">压缩不能按字符一刀切</h2>
    </div>
    <div class="sub-grid-3-2">
      <article class="sub-card"><i data-lucide="ruler"></i><span class="nb-corner">01</span><h3 class="ttl">三道刻度</h3><p class="desc">最少 token、最少消息数、最大 token 上限共同决定保留范围。</p></article>
      <article class="sub-card"><i data-lucide="rewind"></i><span class="nb-corner">02</span><h3 class="ttl">向前回溯</h3><p class="desc">从最后一条已总结消息开始，像倒带一样扩展最近上下文。</p></article>
      <article class="sub-card"><i data-lucide="link"></i><span class="nb-corner">03</span><h3 class="ttl">工具调用成对</h3><p class="desc">tool_use 与 tool_result 是咬合齿轮，不能拆散。</p></article>
      <article class="sub-card"><i data-lucide="message-square-more"></i><span class="nb-corner">04</span><h3 class="ttl">流式片段绑定</h3><p class="desc">同一个 message id 下的 thinking 和 tool_use 要绑定处理。</p></article>
      <article class="sub-card"><i data-lucide="ban"></i><span class="nb-corner">05</span><h3 class="ttl">避免 400 错误</h3><p class="desc">半截工具消息发给 API，结构不完整就会直接报错。</p></article>
      <article class="sub-card accent"><i data-lucide="scissors"></i><span class="nb-corner">06</span><h3 class="ttl">像外科手术</h3><p class="desc">上下文压缩的难点，是切在结构边界上。</p></article>
    </div>
  </div>
</section>

<section class="slide" data-layout="S22" data-animate="image-hero">
  <div class="canvas-card" style="padding:0;display:flex;flex-direction:column;overflow:hidden">
    <div data-anim="img" style="position:relative;flex:0 0 58%;overflow:hidden;background:var(--paper)">
      <img src="images/frame-08.jpg" data-image-slot="s22-hero-21x9" alt="完整压缩截图" loading="eager" style="position:absolute;inset:0;width:100%;height:100%;object-fit:contain;object-position:center center;background:var(--paper)">
      <div class="chrome-min" style="position:absolute;top:0;left:0;right:0;color:var(--text-helper);padding:5.6vh 5vw 0"><div class="l">09 · L3 FULL COMPACT</div><div class="r">Video Screenshot</div></div>
      <div data-anim="title-block" style="position:absolute;left:5vw;top:11vh;background:var(--paper);padding:3.2vh 3.2vw;max-width:44vw"><div style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(4.8vw,8.4vh);line-height:1;letter-spacing:-.035em;color:var(--text-primary)">完整压缩：<br/>先破后立</div></div>
    </div>
    <div data-anim="kpi" class="image-hero-body">
      <div style="max-width:52ch;font-family:var(--sans),var(--sans-zh);font-size:max(15px,1.24vw);line-height:1.55;font-weight:300;color:var(--text-primary)">第三层才调用模型深度复盘。它会让模型先思考，再只保留干净摘要；压缩完成后，还要重新注入关键上下文。</div>
      <div class="image-hero-stats" style="gap:4vw">
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">SCRATCHPAD</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em">临时思考</div><p class="body-sm">用完即丢，不进上下文。</p></div>
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">SUMMARY</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em">最终摘要</div><p class="body-sm">只保留可用结果。</p></div>
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">REBUILD</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em;color:var(--accent)">战后重建</div><p class="body-sm">重新抓回文件、计划、Skill、MCP。</p></div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S11" data-animate="timeline-walk">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">10 · AUTO TRIGGER</div><div class="r">Horizontal Timeline</div></div>
    <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
      <div class="t-meta">第四层是扣扳机的手</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.4vw,9.5vh);line-height:1;letter-spacing:-.03em">什么时候该压缩，由系统自动判断</h2>
    </div>
    <div class="timeline-h" data-anim="up">
      <div class="tl-row" style="grid-template-columns:repeat(5,1fr)">
        <div class="th-node up"><span class="dot"></span><div class="label"><span class="yr">01</span><span class="name">模型调用结束</span><span class="desc">每次返回后卡点检查。</span></div></div>
        <div class="th-node down"><span class="dot"></span><div class="label"><span class="yr">02</span><span class="name">计算 token</span><span class="desc">当前用量对比窗口上限。</span></div></div>
        <div class="th-node up accent"><span class="dot"></span><div class="label"><span class="yr">03</span><span class="name">安全缓冲</span><span class="desc">预留约 13K token 余量。</span></div></div>
        <div class="th-node down"><span class="dot"></span><div class="label"><span class="yr">04</span><span class="name">先轻后重</span><span class="desc">先会话记忆，再完整压缩。</span></div></div>
        <div class="th-node up"><span class="dot"></span><div class="label"><span class="yr">05</span><span class="name">失败熔断</span><span class="desc">连续失败后 break。</span></div></div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S22" data-animate="image-hero">
  <div class="canvas-card" style="padding:0;display:flex;flex-direction:column;overflow:hidden">
    <div data-anim="img" style="position:relative;flex:0 0 58%;overflow:hidden;background:var(--paper)">
      <img src="images/frame-11.jpg" data-image-slot="s22-hero-21x9" alt="自动触发截图" loading="eager" style="position:absolute;inset:0;width:100%;height:100%;object-fit:contain;object-position:center center;background:var(--paper)">
      <div class="chrome-min" style="position:absolute;top:0;left:0;right:0;color:var(--text-helper);padding:5.6vh 5vw 0"><div class="l">11 · CIRCUIT BREAKER</div><div class="r">Video Screenshot</div></div>
      <div data-anim="title-block" style="position:absolute;left:5vw;top:11vh;background:var(--paper);padding:3.2vh 3.2vw;max-width:44vw"><div style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(4.8vw,8.4vh);line-height:1;letter-spacing:-.035em;color:var(--text-primary)">系统熔断：<br/>停止空转</div></div>
    </div>
    <div data-anim="kpi" class="image-hero-body">
      <div style="max-width:52ch;font-family:var(--sans),var(--sans-zh);font-size:max(15px,1.24vw);line-height:1.55;font-weight:300;color:var(--text-primary)">视频提到一次生产事故：自动压缩失败后不断重试，导致大量 API 调用浪费。成熟系统必须有熔断器。</div>
      <div class="image-hero-stats" style="gap:4vw">
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">FAILURE</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em">3272</div><p class="body-sm">单会话连续失败。</p></div>
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">WASTE</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em">25万</div><p class="body-sm">无意义 API 调用。</p></div>
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">FIX</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em;color:var(--accent)">3 次</div><p class="body-sm">连续失败后停止重试。</p></div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S16" data-animate="field-notes">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">12 · SOURCE CONTROL</div><div class="r">Multi-card Brief</div></div>
    <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
      <div class="t-meta">四层之外，源头也要控流</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.4vw,9.5vh);line-height:1;letter-spacing:-.03em">别让垃圾一开始就进上下文</h2>
    </div>
    <div data-anim="up" style="flex:1;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:1.4vh 1.4vw;margin-top:6vh">
      <article class="card-fill" style="padding:2.4vh 1.5vw;display:flex;flex-direction:column"><div class="t-meta">POINTER</div><h3 class="t-h-prod" style="margin-top:1vh">数据指针替换</h3><p class="t-body-sm" style="margin-top:auto">大块工具结果放外部存储，上下文只放指针和短摘要。</p></article>
      <article class="card-fill" style="padding:2.4vh 1.5vw;display:flex;flex-direction:column"><div class="t-meta">SNAPSHOT</div><h3 class="t-h-prod" style="margin-top:1vh">延迟完整压缩</h3><p class="t-body-sm" style="margin-top:auto">能引用就不要复制整块内容，尽量拖延重型压缩。</p></article>
      <article class="card-fill" style="padding:2.4vh 1.5vw;display:flex;flex-direction:column"><div class="t-meta">TOOLS</div><h3 class="t-h-prod" style="margin-top:1vh">渐进式工具扩展</h3><p class="t-body-sm" style="margin-top:auto">初始只加载核心工具，需要时再通过 MCP 或远程发现扩展。</p></article>
      <article class="card-fill" style="padding:2.4vh 1.5vw;display:flex;flex-direction:column"><div class="t-meta">CHOICE</div><h3 class="t-h-prod" style="margin-top:1vh">降低选择困难</h3><p class="t-body-sm" style="margin-top:auto">不给模型一次塞 80 多个工具说明，减少选错和重试。</p></article>
      <article class="card-fill" style="padding:2.4vh 1.5vw;display:flex;flex-direction:column"><div class="t-meta">SCHEMA</div><h3 class="t-h-prod" style="margin-top:1vh">输入门禁</h3><p class="t-body-sm" style="margin-top:auto">用 schema 校验把无效调用挡在门外。</p></article>
      <article class="card-accent" style="padding:2.4vh 1.5vw;display:flex;flex-direction:column"><div class="t-meta">RESULT</div><h3 class="t-h-prod" style="margin-top:1vh;color:var(--accent-on)">减少污染</h3><p class="t-body-sm" style="margin-top:auto;color:rgba(255,255,255,.86)">少一次错误调用，就少一段错误日志进上下文。</p></article>
    </div>
  </div>
</section>

<section class="slide" data-layout="S22" data-animate="image-hero">
  <div class="canvas-card" style="padding:0;display:flex;flex-direction:column;overflow:hidden">
    <div data-anim="img" style="position:relative;flex:0 0 58%;overflow:hidden;background:var(--paper)">
      <img src="images/frame-13.jpg" data-image-slot="s22-hero-21x9" alt="渐进工具扩展截图" loading="eager" style="position:absolute;inset:0;width:100%;height:100%;object-fit:contain;object-position:center center;background:var(--paper)">
      <div class="chrome-min" style="position:absolute;top:0;left:0;right:0;color:var(--text-helper);padding:5.6vh 5vw 0"><div class="l">13 · PROGRESSIVE TOOLS</div><div class="r">Video Screenshot</div></div>
      <div data-anim="title-block" style="position:absolute;left:5vw;top:11vh;background:var(--paper);padding:3.2vh 3.2vw;max-width:44vw"><div style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(4.8vw,8.4vh);line-height:1;letter-spacing:-.035em;color:var(--text-primary)">工具越多，<br/>越要晚加载</div></div>
    </div>
    <div data-anim="kpi" class="image-hero-body">
      <div style="max-width:52ch;font-family:var(--sans),var(--sans-zh);font-size:max(15px,1.24vw);line-height:1.55;font-weight:300;color:var(--text-primary)">工具说明本身也会消耗上下文。按需发现、按需加载，既省 token，也能减少模型选错工具导致的污染。</div>
      <div class="image-hero-stats" style="gap:4vw">
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">START</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em">少量</div><p class="body-sm">Read / Edit / Bash / Grep。</p></div>
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">EXPAND</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em">按需</div><p class="body-sm">MCP / remote tools。</p></div>
        <div><div style="height:1px;background:var(--ink)"></div><div class="t-meta">GATE</div><div style="font-family:var(--sans);font-weight:200;font-size:min(4.2vw,7vh);line-height:.95;letter-spacing:-.04em;color:var(--accent)">Schema</div><p class="body-sm">参数不对，不进门。</p></div>
      </div>
    </div>
  </div>
</section>

<section class="slide split" data-layout="SWISS-CLOSING-ASCII" data-animate="split-statement">
  <div class="canvas-card">
    <div class="split-half">
      <div class="half b-accent" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between;position:relative;overflow:hidden">
        <canvas class="ascii-bg" aria-hidden="true"></canvas>
        <div class="chrome-min" style="margin-bottom:0;position:relative;z-index:1"><div class="l">14 / 14</div><div class="r">CLOSING</div></div>
        <div data-anim="manifesto" style="display:flex;flex-direction:column;gap:2vh;position:relative;z-index:1">
          <div class="t-meta" style="color:rgba(255,255,255,.78);letter-spacing:.22em;margin-bottom:1.6vh">MANIFESTO</div>
          <h2 style="font-family:var(--sans),var(--sans-zh);font-size:min(7vw,12.5vh);line-height:.96;letter-spacing:-.025em;font-weight:200;color:#fff">不要问还能不能装，<br/>要问该不该装。</h2>
          <div style="font-family:var(--sans),var(--sans-zh);font-size:max(13px,1vw);line-height:1.6;color:rgba(255,255,255,.82);font-weight:300;max-width:38ch;margin-top:1.4vh">上下文工程的核心，是对每一条数据进行主动调度、防守和取舍。</div>
        </div>
        <div data-anim="signature" style="display:flex;justify-content:space-between;align-items:end;border-top:1px solid rgba(255,255,255,.22);padding-top:2vh;position:relative;z-index:1"><div class="t-meta" style="color:rgba(255,255,255,.62)">CLAUDE CODE CONTEXT</div><div class="t-meta" style="color:rgba(255,255,255,.62)">2026.05.14</div></div>
      </div>
      <div class="half" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between">
        <div class="chrome-min"><div class="l">TAKEAWAYS</div><div class="r">03 RULES</div></div>
        <div data-anim="rules" style="display:flex;flex-direction:column;gap:0">
          <div style="display:grid;grid-template-columns:auto 1fr;gap:2vw;align-items:start;padding:2.6vh 0;border-top:1px solid var(--border-subtle)"><div style="font-family:var(--sans);font-weight:200;font-size:min(4.4vw,7.8vh);line-height:.9;color:var(--text-primary)">01</div><div><h3 style="font-family:var(--sans),var(--sans-zh);font-weight:400;font-size:max(18px,1.8vw);line-height:1.2;letter-spacing:-.015em;color:var(--text-primary);margin-bottom:1vh">先便宜，后昂贵</h3><p style="font-family:var(--sans),var(--sans-zh);font-size:max(12px,.92vw);line-height:1.6;color:var(--text-secondary);font-weight:300">规则清理优先，模型压缩作为兜底。</p></div></div>
          <div style="display:grid;grid-template-columns:auto 1fr;gap:2vw;align-items:start;padding:2.6vh 0;border-top:1px solid var(--border-subtle)"><div style="font-family:var(--sans);font-weight:200;font-size:min(4.4vw,7.8vh);line-height:.9;color:var(--text-primary)">02</div><div><h3 style="font-family:var(--sans),var(--sans-zh);font-weight:400;font-size:max(18px,1.8vw);line-height:1.2;letter-spacing:-.015em;color:var(--text-primary);margin-bottom:1vh">结构边界大于 token 数</h3><p style="font-family:var(--sans),var(--sans-zh);font-size:max(12px,.92vw);line-height:1.6;color:var(--text-secondary);font-weight:300">工具调用、流式片段、缓存前缀，都是不能随便切开的结构。</p></div></div>
          <div style="display:grid;grid-template-columns:auto 1fr;gap:2vw;align-items:start;padding:2.6vh 0;border-top:1px solid var(--border-subtle);border-bottom:2px solid var(--accent)"><div style="font-family:var(--sans);font-weight:200;font-size:min(4.4vw,7.8vh);line-height:.9;color:var(--accent)">03</div><div><h3 style="font-family:var(--sans),var(--sans-zh);font-weight:400;font-size:max(18px,1.8vw);line-height:1.2;letter-spacing:-.015em;color:var(--accent);margin-bottom:1vh">失败路径必须工程化</h3><p style="font-family:var(--sans),var(--sans-zh);font-size:max(12px,.92vw);line-height:1.6;color:var(--text-secondary);font-weight:300">自动触发、失败熔断、递归防御，是生产环境里真正值钱的设计。</p></div></div>
        </div>
        <div data-anim="foot" class="t-meta" style="color:var(--text-helper);text-align:right">→ 完 · END OF FIELD NOTE</div>
      </div>
    </div>
  </div>
</section>
`;

html = html.replace('<title>[必填] 替换为 PPT 标题 · Deck Title</title>', '<title>Claude Code 上下文架构解析 · Swiss Deck</title>');

const start = html.indexOf('<div id="deck">');
const end = html.indexOf('<div id="nav"></div>', start);
if (start === -1 || end === -1) {
  throw new Error('Could not find deck replacement boundaries.');
}

html = `${html.slice(0, start)}<div id="deck">\n${slides}\n</div>\n\n${html.slice(end)}`;
writeFileSync(target, html);
