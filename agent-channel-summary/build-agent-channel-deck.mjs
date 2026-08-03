import { readFileSync, writeFileSync } from 'node:fs';

const target = '/Users/dds/data/ai/work/agent-channel-summary/AGENT消息通道分享.html';
let html = readFileSync(target, 'utf8');

const slides = String.raw`
<section class="slide accent" data-layout="SWISS-COVER-ASCII" data-animate="hero">
  <div class="canvas-card">
    <canvas class="ascii-bg" aria-hidden="true"></canvas>
    <div class="chrome-min">
      <div class="l">AGENT CHANNEL ADAPTER · FIELD NOTE</div>
      <div class="r">SS · 26.05.14 · 01 / 11</div>
    </div>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr auto;gap:2.6vh">
      <div data-anim="kicker" class="t-meta" style="color:rgba(255,255,255,.78);letter-spacing:.22em">MESSAGE CHANNEL ARCHITECTURE</div>
      <h1 data-anim="title" style="align-self:center;font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(8.4vw,15vh);line-height:.96;letter-spacing:-.025em;color:#fff">AGENT 如何对接<br/>不同的消息通道</h1>
      <div data-anim="bottom" style="display:grid;grid-template-rows:auto auto;gap:1.6vh;border-top:1px solid rgba(255,255,255,.22);padding-top:2vh">
        <div class="lead" style="max-width:56ch;color:rgba(255,255,255,.86);font-weight:300">平台差异交给通道层，AGENT 只处理统一消息模型。核心是消息抽象、会话队列和文件收发。</div>
        <div style="display:flex;justify-content:space-between;align-items:end">
          <div class="t-meta" style="color:rgba(255,255,255,.6)">飞书 · 钉钉 · 企业微信</div>
          <div class="t-meta" style="color:rgba(255,255,255,.6)">→ swipe / arrow keys</div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S03" data-animate="statement-rise">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">02 · CORE QUESTION</div>
      <div class="r">Problem Framing</div>
    </div>
    <div style="flex:1;padding:0;display:grid;grid-template-columns:4fr 8fr;gap:4vw;align-items:center">
      <div data-anim="left" style="display:flex;flex-direction:column;gap:2vh">
        <div class="t-meta">The hidden problem</div>
        <div style="height:2px;background:var(--accent);width:12vw"></div>
        <p class="lead" style="font-weight:300;color:var(--text-secondary)">用户在消息通道里发来的不只是文字，还可能是图片、视频、PDF 或其他文件。</p>
      </div>
      <h2 data-anim="right" style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(7vw,12.2vh);line-height:.98;letter-spacing:-.03em">文件在平台服务器，<br/>AGENT 在另一台服务器。</h2>
    </div>
  </div>
</section>

<section class="slide" data-layout="S08" data-animate="duo-mirror">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">03 · WRONG WAY / RIGHT WAY</div>
      <div class="r">Duo Compare</div>
    </div>
    <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
      <div class="t-meta">不要让平台细节进入 AGENT 层</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.6vw,9.8vh);line-height:1;letter-spacing:-.03em">直接适配，会让复杂度失控</h2>
    </div>
    <div class="duo-compare">
      <div class="col">
        <div class="col-tag"><span class="num">OLD</span> Direct Adapter</div>
        <div class="col-ttl">AGENT 直接接平台</div>
        <p class="col-desc">飞书、钉钉、企业微信各有消息结构。AGENT 直接适配每个平台，会混入大量平台字段和协议细节。</p>
        <ul class="col-list">
          <li>新增通道时要改 AGENT 逻辑。</li>
          <li>消息格式、文件标识、发送接口互相耦合。</li>
          <li>通道越多，维护成本越高。</li>
        </ul>
      </div>
      <span class="vrule"></span>
      <div class="col accent">
        <div class="col-tag"><span class="num">NEW</span> Channel Layer</div>
        <div class="col-ttl">中间增加通道层</div>
        <p class="col-desc">平台差异被收敛到消息通道层，AGENT 只面对统一消息模型和统一输出模型。</p>
        <ul class="col-list">
          <li>输入先标准化，再交给 AGENT。</li>
          <li>文件先下载或上传，再传递可用引用。</li>
          <li>平台扩展变成通道层扩展。</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S05" data-animate="sub-stack">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">04 · THREE-LAYER DESIGN</div>
      <div class="r">Architecture</div>
    </div>
    <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
      <div class="t-meta">三层设计</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.8vw,10.2vh);line-height:1;letter-spacing:-.03em">把消息通道拆成三件事</h2>
    </div>
    <div class="stack-row">
      <article class="stack-block b-grey" data-anim="up">
        <div class="layer-nb">01 · INPUT</div>
        <i data-lucide="inbox" class="lucide"></i>
        <h3 class="layer-ttl">消息接入层</h3>
        <p class="layer-desc">接收平台事件，把不同平台消息转换为统一结构；识别会话、发送者、消息类型和附件。</p>
        <div class="layer-tag">Normalize incoming messages</div>
      </article>
      <article class="stack-block b-accent" data-anim="up">
        <div class="layer-nb">02 · SCHEDULING</div>
        <i data-lucide="list-ordered" class="lucide"></i>
        <h3 class="layer-ttl">队列与并发</h3>
        <p class="layer-desc">同一会话串行排队，保证上下文稳定；不同会话可以并发，但必须受全局限流保护。</p>
        <div class="layer-tag">Session queue and rate limit</div>
      </article>
      <article class="stack-block b-ink" data-anim="up">
        <div class="layer-nb">03 · OUTPUT</div>
        <i data-lucide="send" class="lucide"></i>
        <h3 class="layer-ttl">消息输出层</h3>
        <p class="layer-desc">把 AGENT 的文字、工具结果、图片、表格和报告转换成平台可发送的消息。</p>
        <div class="layer-tag">Adapt outgoing results</div>
      </article>
    </div>
  </div>
</section>

<section class="slide" data-layout="S04" data-animate="six-cells">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">05 · MESSAGE INGRESS</div>
      <div class="r">Six Cells</div>
    </div>
    <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
      <div class="t-meta">消息接入层负责什么</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.4vw,9.5vh);line-height:1;letter-spacing:-.03em">先变成 AGENT 看得懂的消息</h2>
    </div>
    <div class="sub-grid-3-2">
      <article class="sub-card"><i data-lucide="messages-square"></i><span class="nb-corner">01</span><h3 class="ttl">统一消息结构</h3><p class="desc">不同平台的事件格式先转换为统一消息模型。</p></article>
      <article class="sub-card"><i data-lucide="user-round"></i><span class="nb-corner">02</span><h3 class="ttl">识别会话</h3><p class="desc">明确这条消息属于哪个用户、群组或上下文。</p></article>
      <article class="sub-card"><i data-lucide="type"></i><span class="nb-corner">03</span><h3 class="ttl">识别类型</h3><p class="desc">区分文字、图片、视频、PDF、表格和其他文件。</p></article>
      <article class="sub-card"><i data-lucide="download"></i><span class="nb-corner">04</span><h3 class="ttl">下载附件</h3><p class="desc">文件类消息不能只传平台 file key，要先拉到可访问位置。</p></article>
      <article class="sub-card"><i data-lucide="folder-open"></i><span class="nb-corner">05</span><h3 class="ttl">交付路径</h3><p class="desc">把本地路径或可访问 URL 交给 AGENT，让它能读取内容。</p></article>
      <article class="sub-card accent"><i data-lucide="shield-check"></i><span class="nb-corner">06</span><h3 class="ttl">隔离平台差异</h3><p class="desc">AGENT 不需要关心背后来自飞书、钉钉还是企业微信。</p></article>
    </div>
  </div>
</section>

<section class="slide" data-layout="S19" data-animate="four-cards">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">06 · FILE INPUT</div>
      <div class="r">Four Cards</div>
    </div>
    <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh;border-top:2px solid var(--accent);padding-top:2.6vh">
      <div class="t-meta">最容易被忽略的是文件处理</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.4vw,9.5vh);line-height:1;letter-spacing:-.03em">file key 不是文件本身</h2>
    </div>
    <div data-anim="up" style="flex:1;display:grid;grid-template-columns:repeat(4,1fr);gap:1.6vw;margin-top:7vh;align-items:stretch">
      <article class="card-fill" style="padding:3vh 1.6vw;display:flex;flex-direction:column;gap:1.4vh"><div class="t-meta">— 01 / WHERE</div><h3 class="h-md">平台文件服务</h3><p class="t-body-sm">用户上传图片、视频或 PDF 后，文件通常存放在平台自己的服务器上。</p></article>
      <article class="card-fill" style="padding:3vh 1.6vw;display:flex;flex-direction:column;gap:1.4vh"><div class="t-meta">— 02 / WHAT</div><h3 class="h-md">消息里只有标识</h3><p class="t-body-sm">消息事件里常见的是 file key、image key 或 media id，不是可直接读取的二进制内容。</p></article>
      <article class="card-fill" style="padding:3vh 1.6vw;display:flex;flex-direction:column;gap:1.4vh"><div class="t-meta">— 03 / HOW</div><h3 class="h-md">通道层下载</h3><p class="t-body-sm">接入层用平台 API 下载文件，并保存到 AGENT 可访问的位置。</p></article>
      <article class="card-accent" style="padding:3vh 1.6vw;display:flex;flex-direction:column;gap:1.4vh"><div class="t-meta">— 04 / RESULT</div><h3 class="h-md" style="color:var(--accent-on)">AGENT 才能处理</h3><p class="t-body-sm" style="color:rgba(255,255,255,.86)">最后把本地路径或 URL 交给 AGENT，它才能读取、分析或转换文件。</p></article>
    </div>
  </div>
</section>

<section class="slide" data-layout="S11" data-animate="timeline-walk">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">07 · SESSION QUEUE</div>
      <div class="r">Horizontal Timeline</div>
    </div>
    <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
      <div class="t-meta">消息通道不会阻止用户连续发消息</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.4vw,9.5vh);line-height:1;letter-spacing:-.03em">同一会话要串行，不同会话可并发</h2>
    </div>
    <div class="timeline-h" data-anim="up">
      <div class="tl-row" style="grid-template-columns:repeat(5,1fr)">
        <div class="th-node up"><span class="dot"></span><div class="label"><span class="yr">01</span><span class="name">用户连续发送</span><span class="desc">第二条、第三条消息可能立刻到达。</span></div></div>
        <div class="th-node down"><span class="dot"></span><div class="label"><span class="yr">02</span><span class="name">按会话入队</span><span class="desc">同一会话进入同一条任务队列。</span></div></div>
        <div class="th-node up accent"><span class="dot"></span><div class="label"><span class="yr">03</span><span class="name">前一条先完成</span><span class="desc">上下文稳定，处理结果更符合用户预期。</span></div></div>
        <div class="th-node down"><span class="dot"></span><div class="label"><span class="yr">04</span><span class="name">不同会话隔离</span><span class="desc">张三、李四、王五互不影响。</span></div></div>
        <div class="th-node up"><span class="dot"></span><div class="label"><span class="yr">05</span><span class="name">全局并发限流</span><span class="desc">超过最大并发后统一排队。</span></div></div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S16" data-animate="field-notes">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">08 · MESSAGE OUTPUT</div>
      <div class="r">Multi-card Brief</div>
    </div>
    <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
      <div class="t-meta">AGENT 的输出不止一种</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.4vw,9.5vh);line-height:1;letter-spacing:-.03em">输出层负责把结果发回平台</h2>
    </div>
    <div data-anim="up" style="flex:1;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:1.4vh 1.4vw;margin-top:6vh">
      <article class="card-fill" style="padding:2.4vh 1.5vw;display:flex;flex-direction:column"><div class="t-meta">TEXT</div><h3 class="t-h-prod" style="margin-top:1vh">普通文字回复</h3><p class="t-body-sm" style="margin-top:auto">转换为平台的 text / markdown / rich text 消息。</p></article>
      <article class="card-fill" style="padding:2.4vh 1.5vw;display:flex;flex-direction:column"><div class="t-meta">TOOL</div><h3 class="t-h-prod" style="margin-top:1vh">工具调用结果</h3><p class="t-body-sm" style="margin-top:auto">可以作为过程事件、结构化内容或最终回复展示。</p></article>
      <article class="card-fill" style="padding:2.4vh 1.5vw;display:flex;flex-direction:column"><div class="t-meta">THINKING</div><h3 class="t-h-prod" style="margin-top:1vh">思考与过程</h3><p class="t-body-sm" style="margin-top:auto">按产品策略决定是否展示、折叠或隐藏。</p></article>
      <article class="card-fill" style="padding:2.4vh 1.5vw;display:flex;flex-direction:column"><div class="t-meta">IMAGE</div><h3 class="t-h-prod" style="margin-top:1vh">图片产物</h3><p class="t-body-sm" style="margin-top:auto">例如生成图、截图、可视化结果。</p></article>
      <article class="card-fill" style="padding:2.4vh 1.5vw;display:flex;flex-direction:column"><div class="t-meta">FILE</div><h3 class="t-h-prod" style="margin-top:1vh">表格与报告</h3><p class="t-body-sm" style="margin-top:auto">通常先是 AGENT 服务器上的本地路径。</p></article>
      <article class="card-accent" style="padding:2.4vh 1.5vw;display:flex;flex-direction:column"><div class="t-meta">ADAPTER</div><h3 class="t-h-prod" style="margin-top:1vh;color:var(--accent-on)">通道层发送</h3><p class="t-body-sm" style="margin-top:auto;color:rgba(255,255,255,.86)">最终调用平台 API，把统一输出转成平台消息。</p></article>
    </div>
  </div>
</section>

<section class="slide" data-layout="S04" data-animate="six-cells">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">09 · FILE OUTPUT</div>
      <div class="r">Upload Before Send</div>
    </div>
    <div data-anim="head" style="display:flex;flex-direction:column;gap:1.4vh">
      <div class="t-meta">本地路径不能直接发给用户</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(5.4vw,9.5vh);line-height:1;letter-spacing:-.03em">文件发送要先上传，再发送</h2>
    </div>
    <div class="sub-grid-3-2">
      <article class="sub-card"><i data-lucide="file-plus-2"></i><span class="nb-corner">01</span><h3 class="ttl">AGENT 生成文件</h3><p class="desc">例如图片、表格、报告或其他中间产物。</p></article>
      <article class="sub-card"><i data-lucide="route"></i><span class="nb-corner">02</span><h3 class="ttl">得到本地路径</h3><p class="desc">这个路径只在 AGENT 所在服务器上有意义。</p></article>
      <article class="sub-card"><i data-lucide="upload-cloud"></i><span class="nb-corner">03</span><h3 class="ttl">上传平台文件服务</h3><p class="desc">通道层调用飞书、钉钉或企微的文件上传接口。</p></article>
      <article class="sub-card"><i data-lucide="key-round"></i><span class="nb-corner">04</span><h3 class="ttl">拿到平台标识</h3><p class="desc">获得 file key、media id 或平台定义的可发送引用。</p></article>
      <article class="sub-card"><i data-lucide="send-horizontal"></i><span class="nb-corner">05</span><h3 class="ttl">调用发送接口</h3><p class="desc">使用平台可识别的文件标识把内容发给用户。</p></article>
      <article class="sub-card accent"><i data-lucide="wrench"></i><span class="nb-corner">06</span><h3 class="ttl">也可封装工具</h3><p class="desc">提供 send_file、send_image，让 AGENT 决定发什么，工具负责怎么发。</p></article>
    </div>
  </div>
</section>

<section class="slide" data-layout="S17" data-animate="system-diagram">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">10 · FULL FLOW</div>
      <div class="r">System Diagram</div>
    </div>
    <div data-anim="head" style="display:grid;grid-template-columns:5fr 7fr;gap:4vw;align-items:start">
      <div style="display:flex;flex-direction:column;gap:1.4vh">
        <div class="t-meta">完整路径</div>
        <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(4.8vw,8.5vh);line-height:1.02;letter-spacing:-.03em">输入标准化，处理排队，输出再适配</h2>
      </div>
      <p class="lead" style="font-weight:300;color:var(--text-secondary)">通道层不是一个简单 webhook，而是夹在平台和 AGENT 之间的协议适配、文件搬运和任务调度系统。</p>
    </div>
    <div data-anim="up" style="flex:1;display:grid;grid-template-columns:4fr 8fr;gap:3vw;margin-top:6vh;align-items:stretch">
      <div style="display:grid;gap:1.2vh">
        <div class="card-fill" style="padding:2vh 1.4vw"><div class="t-meta">Ingress</div><p class="t-body-sm">平台事件进入后，先变成统一消息模型。</p></div>
        <div class="card-fill" style="padding:2vh 1.4vw"><div class="t-meta">Queue</div><p class="t-body-sm">同一会话排队，不同会话隔离并发。</p></div>
        <div class="card-fill" style="padding:2vh 1.4vw"><div class="t-meta">Egress</div><p class="t-body-sm">文字直接发送，文件先上传再发送。</p></div>
      </div>
      <div style="position:relative;background:var(--grey-1);padding:4vh 3vw;display:grid;grid-template-columns:repeat(7,1fr);gap:1vw;align-items:center">
        <div class="card-fill" style="background:var(--paper);padding:2vh 1vw"><i data-lucide="user" class="ico-md"></i><div class="t-body-emp" style="margin-top:1vh">用户</div></div>
        <div class="t-meta" style="display:flex;justify-content:center;color:var(--accent)">→</div>
        <div class="card-fill" style="background:var(--paper);padding:2vh 1vw"><i data-lucide="message-square" class="ico-md"></i><div class="t-body-emp" style="margin-top:1vh">平台</div><div class="t-helper">飞书 / 钉钉 / 企微</div></div>
        <div class="t-meta" style="display:flex;justify-content:center;color:var(--accent)">→</div>
        <div class="card-accent" style="padding:2vh 1vw"><i data-lucide="waypoints" class="ico-md"></i><div class="t-body-emp" style="margin-top:1vh;color:var(--accent-on)">通道层</div><div class="t-helper" style="color:rgba(255,255,255,.78)">接入 · 队列 · 输出</div></div>
        <div class="t-meta" style="display:flex;justify-content:center;color:var(--accent)">→</div>
        <div class="card-fill" style="background:var(--paper);padding:2vh 1vw"><i data-lucide="bot" class="ico-md"></i><div class="t-body-emp" style="margin-top:1vh">AGENT</div><div class="t-helper">统一模型</div></div>
        <div style="grid-column:1 / -1;border-top:1px solid var(--border-subtle);padding-top:2vh;margin-top:1vh;display:grid;grid-template-columns:1fr 1fr 1fr;gap:1vw">
          <div class="t-body-sm">平台文件服务 → 下载到 AGENT 可访问位置</div>
          <div class="t-body-sm">AGENT 生成文件 → 通道层记录路径</div>
          <div class="t-body-sm">上传平台文件服务 → file key / media id</div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="slide split" data-layout="SWISS-CLOSING-ASCII" data-animate="split-statement">
  <div class="canvas-card">
    <div class="split-half">
      <div class="half b-accent" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between;position:relative;overflow:hidden">
        <canvas class="ascii-bg" aria-hidden="true"></canvas>
        <div class="chrome-min" style="margin-bottom:0;position:relative;z-index:1">
          <div class="l">11 / 11</div>
          <div class="r">CLOSING</div>
        </div>
        <div data-anim="manifesto" style="display:flex;flex-direction:column;gap:2vh;position:relative;z-index:1">
          <div class="t-meta" style="color:rgba(255,255,255,.78);letter-spacing:.22em;margin-bottom:1.6vh">MANIFESTO</div>
          <h2 style="font-family:var(--sans),var(--sans-zh);font-size:min(7.4vw,13vh);line-height:.96;letter-spacing:-.025em;font-weight:200;color:#fff">掌握原理层，<br/>再去调 API。</h2>
          <div style="font-family:var(--sans),var(--sans-zh);font-size:max(13px,1vw);line-height:1.6;color:rgba(255,255,255,.82);font-weight:300;max-width:38ch;margin-top:1.4vh">消息抽象、文件搬运、会话队列和输出适配，是 AGENT 接入消息通道的核心骨架。</div>
        </div>
        <div data-anim="signature" style="display:flex;justify-content:space-between;align-items:end;border-top:1px solid rgba(255,255,255,.22);padding-top:2vh;position:relative;z-index:1">
          <div class="t-meta" style="color:rgba(255,255,255,.62)">AGENT CHANNEL SHARING</div>
          <div class="t-meta" style="color:rgba(255,255,255,.62)">2026.05.14</div>
        </div>
      </div>
      <div class="half" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between">
        <div class="chrome-min"><div class="l">TAKEAWAYS</div><div class="r">03 RULES</div></div>
        <div data-anim="rules" style="display:flex;flex-direction:column;gap:0">
          <div style="display:grid;grid-template-columns:auto 1fr;gap:2vw;align-items:start;padding:2.6vh 0;border-top:1px solid var(--border-subtle)">
            <div style="font-family:var(--sans);font-weight:200;font-size:min(4.4vw,7.8vh);line-height:.9;color:var(--text-primary)">01</div>
            <div><h3 style="font-family:var(--sans),var(--sans-zh);font-weight:400;font-size:max(18px,1.8vw);line-height:1.2;letter-spacing:-.015em;color:var(--text-primary);margin-bottom:1vh">AGENT 层保持平台无关</h3><p style="font-family:var(--sans),var(--sans-zh);font-size:max(12px,.92vw);line-height:1.6;color:var(--text-secondary);font-weight:300">平台字段、发送协议和文件标识尽量留在通道层。</p></div>
          </div>
          <div style="display:grid;grid-template-columns:auto 1fr;gap:2vw;align-items:start;padding:2.6vh 0;border-top:1px solid var(--border-subtle)">
            <div style="font-family:var(--sans);font-weight:200;font-size:min(4.4vw,7.8vh);line-height:.9;color:var(--text-primary)">02</div>
            <div><h3 style="font-family:var(--sans),var(--sans-zh);font-weight:400;font-size:max(18px,1.8vw);line-height:1.2;letter-spacing:-.015em;color:var(--text-primary);margin-bottom:1vh">文件输入输出要专门处理</h3><p style="font-family:var(--sans),var(--sans-zh);font-size:max(12px,.92vw);line-height:1.6;color:var(--text-secondary);font-weight:300">输入先下载，输出先上传；不要把平台 file key 或本地路径当成可直接使用的文件。</p></div>
          </div>
          <div style="display:grid;grid-template-columns:auto 1fr;gap:2vw;align-items:start;padding:2.6vh 0;border-top:1px solid var(--border-subtle);border-bottom:2px solid var(--accent)">
            <div style="font-family:var(--sans);font-weight:200;font-size:min(4.4vw,7.8vh);line-height:.9;color:var(--accent)">03</div>
            <div><h3 style="font-family:var(--sans),var(--sans-zh);font-weight:400;font-size:max(18px,1.8vw);line-height:1.2;letter-spacing:-.015em;color:var(--accent);margin-bottom:1vh">队列决定体验上限</h3><p style="font-family:var(--sans),var(--sans-zh);font-size:max(12px,.92vw);line-height:1.6;color:var(--text-secondary);font-weight:300">同一会话串行保证上下文，不同会话并发提升吞吐，全局限流保护系统。</p></div>
          </div>
        </div>
        <div data-anim="foot" class="t-meta" style="color:var(--text-helper);text-align:right">→ 完 · END OF FIELD NOTE</div>
      </div>
    </div>
  </div>
</section>
`;

html = html.replace('<title>[必填] 替换为 PPT 标题 · Deck Title</title>', '<title>AGENT 如何对接不同的消息通道 · Swiss Deck</title>');

const start = html.indexOf('<div id="deck">');
const end = html.indexOf('<div id="nav"></div>', start);
if (start === -1 || end === -1) {
  throw new Error('Could not find deck replacement boundaries.');
}

const before = html.slice(0, start);
const after = html.slice(end);
html = `${before}<div id="deck">\n${slides}\n</div>\n\n${after}`;

writeFileSync(target, html);
