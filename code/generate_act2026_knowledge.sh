#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import os
import re
import json
import hashlib
from pathlib import Path
from collections import Counter

SRC_ROOT = Path('/Users/dds/go/src/git.inke.cn/opd/activitys/inke.activity.service/act/2026')
OUT_ROOT = Path('/Users/dds/data/ai/work/code/act2026-knowledge')
OUT_ROOT.mkdir(parents=True, exist_ok=True)

SKIP_DIRS = {'.git', '.idea', '.vscode', 'vendor', 'node_modules', 'tmp', 'logs', 'log'}
TEXT_EXTS = {'.go', '.md', '.yaml', '.yml', '.json', '.toml', '.ini', '.conf', '.sql', '.proto', '.thrift'}

def safe_read(path: Path, limit=240_000):
    try:
        data = path.read_bytes()[:limit]
    except Exception:
        return ''
    for enc in ('utf-8', 'gbk', 'gb2312', 'latin-1'):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            pass
    return data.decode('utf-8', 'ignore')

def redact(text: str):
    if not text:
        return text
    patterns = [
        (r'(?i)(password\s*=\s*)"?[^"\s,;]+"?', r'\1"***REDACTED***"'),
        (r'(?i)(passwd\s*=\s*)"?[^"\s,;]+"?', r'\1"***REDACTED***"'),
        (r'(?i)(pwd\s*=\s*)"?[^"\s,;]+"?', r'\1"***REDACTED***"'),
        (r'(?i)(-p)"?[^"\s]+"?', r'\1"***REDACTED***"'),
        (r'(?i)(redis-cli\b[^\n]*\s-a\s+)[^\s]+', r'\1***REDACTED***'),
        (r'(?i)((?:api[_-]?key|secret|token|access[_-]?key)\s*[:=]\s*)"?[^"\s,;]+"?', r'\1"***REDACTED***"'),
    ]
    out = text
    for pat, repl in patterns:
        out = re.sub(pat, repl, out)
    return out

def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() in TEXT_EXTS or name in {'README', 'Makefile'}:
                yield p

def mermaid_id(label: str):
    return 'n' + hashlib.md5(label.encode('utf-8')).hexdigest()[:8]

def esc(label: str):
    return label.replace('"', "'").replace('\n', ' ')

def add_edge(edges, a, b, label=''):
    if a and b and a != b:
        edges.add((a, b, label))

def first_heading(text: str):
    for line in text.splitlines():
        s = line.strip()
        if s.startswith('#'):
            return s.lstrip('#').strip()
    for line in text.splitlines():
        s = line.strip()
        if s:
            return s[:100]
    return ''

def detect_activity_type(name: str, text: str):
    s = f'{name}\n{text}'.lower()
    rules = [
        ('KA/SVIP 活动', ['ka_', 'svip', 'super']),
        ('游戏玩法', ['game', 'lucky', 'pets', 'forage', 'bump']),
        ('榜单冲榜', ['rank', '榜', '榜单', 'all_star', 'paiduibang']),
        ('任务/活跃', ['task', '任务', 'active']),
        ('节日/节点活动', ['chunjie', 'yuanxiao', 'duanwu', '618', '527', '51', 'laba']),
        ('用户侧活动', ['user']),
        ('图标/入口', ['icon']),
        ('奖励/抽奖', ['prize', 'draw', 'claim', 'reward', 'treasure']),
    ]
    hits = []
    for label, keys in rules:
        if any(k in s for k in keys):
            hits.append(label)
    return hits[:4] or ['活动业务模块']

def scan_project(project: Path):
    files = list(iter_files(project))
    go_files = [p for p in files if p.suffix == '.go']
    rel_files = [str(p.relative_to(project)) for p in files]
    ext_counter = Counter(p.suffix.lower() or p.name for p in files)
    readme_text = redact('\n\n'.join(safe_read(p, 100_000) for p in files if p.name.lower().startswith('readme')))

    per_file = {}
    all_go = ''
    for p in go_files:
        t = safe_read(p, 160_000)
        per_file[p] = t
        all_go += '\n' + t

    module_names = sorted(set(re.findall(r'ModuleName\s*=\s*"([^"]+)"', all_go)))
    key_consts = []
    for m in re.finditer(r'(Key[A-Za-z0-9_]+)\s*=\s*"([^"]+)"', all_go):
        if len(key_consts) < 60:
            key_consts.append((m.group(1), m.group(2)))

    handlers = []
    exported_funcs = []
    service_methods = []
    models = []
    for m in re.finditer(r'func\s+([a-z][A-Za-z0-9_]*)\s*\(c \*httpserver\.Context\)', all_go):
        if len(handlers) < 80:
            handlers.append(m.group(1))
    for m in re.finditer(r'func\s+(?:\([^)]*\)\s*)?([A-Z][A-Za-z0-9_]{2,})\s*\(', all_go):
        if len(exported_funcs) < 80:
            exported_funcs.append(m.group(1))
    for m in re.finditer(r'func\s+\(s \*service\)\s+([A-Za-z0-9_]+)\s*\(', all_go):
        if len(service_methods) < 80:
            service_methods.append(m.group(1))
    for m in re.finditer(r'type\s+([A-Z][A-Za-z0-9_]{2,})\s+struct', all_go):
        if len(models) < 80:
            models.append(m.group(1))

    signal_map = [
        ('活动基础信息', ['GetActBaseInfo', 'GetActInfoByte', 'ActServerTimeGet', 'GetServerTime', 'CheckIsInActTime']),
        ('用户初始化/身份', ['UserInit', 'GetUserInfo', 'UserInfo', 'GetUserLevel']),
        ('排行榜', ['Rank', 'GetMultiLoverRankList', 'GetStandardMyRank', 'ZSet', 'SetZSetScore', 'GetZSetScore']),
        ('奖励发放/领奖', ['Claim', 'Prize', 'Reward', 'SendGift', 'AddBag', 'claim']),
        ('任务系统', ['Task', 'ActiveTask', 'setUserActiveTask', 'task']),
        ('缓存/Redis', ['Redis', 'GetKey', 'Lock', 'Expire', 'SetCache', 'GetCache']),
        ('日志/埋点', ['ActLog', 'big_log', 'Datalog', 'Log']),
        ('HTTP 接口', ['httpserver.Context']),
        ('配置 JSON', ['json.Get', 'ToVal', 'conf']),
    ]
    signals = Counter()
    for label, keys in signal_map:
        for k in keys:
            c = all_go.count(k)
            if c:
                signals[label] += c

    file_roles = Counter()
    role_files = {k: [] for k in ['入口/路由', '接口处理', '服务逻辑', '任务逻辑', '模型结构', '配置/常量', '工具辅助']}
    for p, t in per_file.items():
        rel = str(p.relative_to(project))
        low = rel.lower() + '\n' + t.lower()
        roles = []
        if 'router' in low or 'route' in low or 'init()' in t:
            roles.append('入口/路由')
        if 'httpserver.context' in low or re.search(r'func\s+[a-z][A-Za-z0-9_]*\s*\(c \*httpserver\.Context\)', t):
            roles.append('接口处理')
        if 'type service struct' in low or 'func (s *service)' in low or rel.startswith('service'):
            roles.append('服务逻辑')
        if 'task' in low or 'cron' in low or 'active' in low:
            roles.append('任务逻辑')
        if 'model' in low or 'type ' in t and ' struct' in t:
            roles.append('模型结构')
        if 'const' in t or 'var ' in t or 'config' in low or 'conf' in low:
            roles.append('配置/常量')
        if 'utils' in low or 'helper' in low:
            roles.append('工具辅助')
        for r in sorted(set(roles)):
            file_roles[r] += 1
            if len(role_files[r]) < 10:
                role_files[r].append(rel)

    imports = Counter()
    internal_imports = Counter()
    import_re = re.compile(r'import\s*\((.*?)\)|import\s+"([^"]+)"', re.S)
    quoted_re = re.compile(r'"([^"]+)"')
    for m in import_re.finditer(all_go):
        vals = [m.group(2)] if m.group(2) else quoted_re.findall(m.group(1) or '')
        for imp in vals:
            if imp.startswith('git.inke.cn/opd/activitys/inke.activity.service'):
                parts = imp.split('/')
                internal_imports['/'.join(parts[:6]) if len(parts) >= 6 else imp] += 1
            elif imp.startswith('git.inke.cn/'):
                parts = imp.split('/')
                internal_imports['/'.join(parts[:5]) if len(parts) >= 5 else imp] += 1
            else:
                root = imp.split('/')[0]
                if root not in {'context', 'fmt', 'time', 'strings', 'strconv', 'encoding', 'net', 'errors', 'sync', 'sort', 'math'}:
                    imports[root] += 1

    routes = []
    for m in re.finditer(r'(?:GET|POST|PUT|DELETE|PATCH)\s+[`" ]([^`"\s]+)', all_go):
        if len(routes) < 40:
            routes.append(m.group(1))
    for m in re.finditer(r'\.Handle(?:Func)?\([^"`]*["`]([^"`]+)["`]', all_go):
        if len(routes) < 40:
            routes.append(m.group(1))

    month = project.parent.name
    return {
        'name': project.name,
        'month': month,
        'path': str(project),
        'file_count': len(files),
        'go_count': len(go_files),
        'ext_counter': ext_counter,
        'readme_heading': first_heading(readme_text),
        'readme_excerpt': '\n'.join([ln.strip() for ln in readme_text.splitlines() if ln.strip()][:16]),
        'activity_types': detect_activity_type(project.name, readme_text + all_go[:50_000]),
        'module_names': module_names,
        'key_consts': key_consts,
        'handlers': handlers,
        'exported_funcs': exported_funcs,
        'service_methods': service_methods,
        'models': models,
        'signals': signals,
        'file_roles': file_roles,
        'role_files': role_files,
        'imports': imports,
        'internal_imports': internal_imports,
        'routes': routes,
        'rel_files': rel_files[:120],
    }

def render(info):
    nodes = set()
    edges = set()
    def node(label):
        nodes.add(label)
        return label
    center = node(info['name'])
    add_edge(edges, center, node(info['month']), 'month')
    for t in info['activity_types']:
        add_edge(edges, center, node('类型: ' + t), 'type')
    if info['module_names']:
        for m in info['module_names'][:4]:
            add_edge(edges, center, node('ModuleName: ' + m), 'module')
    if info['handlers'] or info['routes']:
        h = node('HTTP 接口/Handler')
        add_edge(edges, center, h, 'exposes')
        for x in info['handlers'][:8]:
            add_edge(edges, h, node('handler: ' + x), '')
    if info['service_methods']:
        s = node('活动服务逻辑')
        add_edge(edges, center, s, 'core')
        for x in info['service_methods'][:8]:
            add_edge(edges, s, node('service: ' + x), '')
    if info['key_consts']:
        k = node('Redis/状态 Key')
        add_edge(edges, center, k, 'state')
        for name, val in info['key_consts'][:8]:
            add_edge(edges, k, node(name + ': ' + val[:40]), '')
    if info['signals']:
        sg = node('业务能力信号')
        add_edge(edges, center, sg, 'uses')
        for x, _ in info['signals'].most_common(8):
            add_edge(edges, sg, node(x), '')
    if info['models']:
        md = node('模型/响应结构')
        add_edge(edges, center, md, 'defines')
        for x in info['models'][:8]:
            add_edge(edges, md, node(x), '')
    if info['internal_imports']:
        dep = node('活动公共依赖')
        add_edge(edges, center, dep, 'imports')
        for x, _ in info['internal_imports'].most_common(8):
            add_edge(edges, dep, node(x), '')

    idmap = {label: mermaid_id(label) for label in nodes}
    mermaid = ['```mermaid', 'flowchart LR']
    for label in sorted(nodes):
        mermaid.append(f'  {idmap[label]}["{esc(label)}"]')
    for a, b, label in sorted(edges):
        if label:
            mermaid.append(f'  {idmap[a]} -- "{esc(label)}" --> {idmap[b]}')
        else:
            mermaid.append(f'  {idmap[a]} --> {idmap[b]}')
    mermaid.append('```')

    ext_lines = ', '.join(f'{k}({v})' for k, v in info['ext_counter'].most_common(8)) or '无文本文件'
    module_names = ', '.join(f'`{x}`' for x in info['module_names']) or '静态扫描未发现 `ModuleName` 常量'
    types = ', '.join(info['activity_types'])
    readme = info['readme_excerpt'] or '未发现 README 或 README 内容为空'
    routes = '\n'.join(f'- `{x}`' for x in info['routes'][:40]) or '- 未发现显式路由字符串，需结合活动总路由注册确认'
    handlers = '\n'.join(f'- `{x}`' for x in info['handlers'][:80]) or '- 未发现 `func xxx(c *httpserver.Context)` 形式 Handler'
    service_methods = '\n'.join(f'- `{x}`' for x in info['service_methods'][:80]) or '- 未发现 `(s *service)` 方法'
    key_consts = '\n'.join(f'- `{k}` = `{v}`' for k, v in info['key_consts'][:60]) or '- 未发现 `Key*` 常量'
    models = ', '.join(info['models'][:60]) or '未发现导出结构体'
    exported = ', '.join(info['exported_funcs'][:60]) or '未发现导出函数/方法'
    signals = '\n'.join(f'- {k}: {v} 处信号' for k, v in info['signals'].most_common()) or '- 未发现明显活动能力信号'
    roles = '\n'.join(f'- {k}: {v} 个文件，示例：' + ', '.join(f'`{x}`' for x in info['role_files'][k][:6]) for k, v in info['file_roles'].most_common()) or '- 文件较少，未形成明显分层'
    internal = '\n'.join(f'- `{k}`: {v}' for k, v in info['internal_imports'].most_common(20)) or '- 未发现明显内部依赖'
    imports = ', '.join(f'{k}({v})' for k, v in info['imports'].most_common(15)) or '主要为标准库/内部包'
    files = '\n'.join(f'- `{x}`' for x in info['rel_files'][:80]) or '- 无文件'

    return f'''# {info['name']} 活动项目知识库

## 一图知识图谱
{chr(10).join(mermaid)}

## 项目定位
- 源码路径：`{info['path']}`
- 所属月份：`{info['month']}`
- 活动类型判断：{types}
- ModuleName：{module_names}
- README 摘要：{info['readme_heading'] or '无标题'}

```text
{readme}
```

## 静态结构画像
- 文本/代码文件数：{info['file_count']}
- Go 文件数：{info['go_count']}
- 文件类型分布：{ext_lines}

## 入口与接口
### 路由线索
{routes}

### Handler 函数
{handlers}

## 核心业务逻辑
### service 方法
{service_methods}

### 业务能力信号
{signals}

## 状态与缓存 Key
{key_consts}

## 模型与导出 API
- 导出结构体：{models}
- 导出函数/方法：{exported}

## 文件分层
{roles}

## 内部依赖
{internal}

## 第三方 import 概览
- {imports}

## 文件清单摘录
{files}

## 阅读路径建议
- 先确认 `ModuleName` 与活动配置，活动时间、入口 URL、奖励配置通常通过 `act.Srv.GetActInfoByte` 或 `act.Srv.GetActBaseInfo` 获取。
- 再读 Handler 列表，按页面接口、榜单接口、任务接口、领奖接口拆分主流程。
- 重点跟踪 `Key*` 常量和 `act.Dao.GetKey`，它们通常对应 Redis 状态、榜单 ZSet、领奖锁和任务进度。
- 看到 `Claim`、`Prize`、`Reward`、`SendGift`、`AddBag` 相关代码时，优先核对幂等锁、活动时间校验和奖励次数限制。
'''

projects = []
for month in sorted([p for p in SRC_ROOT.iterdir() if p.is_dir()]):
    for project in sorted([p for p in month.iterdir() if p.is_dir()]):
        projects.append(project)

manifest = []
for project in projects:
    info = scan_project(project)
    out = OUT_ROOT / f'{project.name}-活动知识库.md'
    out.write_text(render(info), encoding='utf-8')
    manifest.append({
        'project': project.name,
        'month': project.parent.name,
        'path': str(project),
        'output': str(out),
        'files': info['file_count'],
        'go_files': info['go_count'],
        'module_names': info['module_names'],
        'activity_types': info['activity_types'],
    })

(OUT_ROOT / 'act2026-活动知识库生成清单.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'count': len(manifest), 'out': str(OUT_ROOT)}, ensure_ascii=False))
PY
