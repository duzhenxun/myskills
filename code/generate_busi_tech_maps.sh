#!/usr/bin/env bash
set -euo pipefail

SRC_ROOT="/Users/dds/go/src/git.inke.cn/bpc/server/busi"
OUT_ROOT="/Users/dds/data/ai/work/code"

mkdir -p "$OUT_ROOT"

python3 - <<'PY'
import os
import re
import json
import hashlib
from pathlib import Path
from collections import Counter, defaultdict

SRC_ROOT = Path('/Users/dds/go/src/git.inke.cn/bpc/server/busi')
OUT_ROOT = Path('/Users/dds/data/ai/work/code')

SKIP_DIRS = {'.git', '.idea', '.vscode', 'vendor', 'node_modules', 'tmp', 'logs', 'log', 'graphify-out'}
TEXT_EXTS = {'.go', '.md', '.yaml', '.yml', '.json', '.toml', '.ini', '.conf', '.proto', '.thrift', '.sql'}

def safe_read(path: Path, limit=200_000):
    try:
        data = path.read_bytes()[:limit]
    except Exception:
        return ''
    for enc in ('utf-8', 'gbk', 'gb2312', 'latin-1'):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
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
            if p.suffix.lower() in TEXT_EXTS or name in {'README', 'Makefile', 'Dockerfile'}:
                yield p

def mermaid_id(label: str):
    h = hashlib.md5(label.encode('utf-8')).hexdigest()[:8]
    return 'n' + h

def esc(label: str):
    return label.replace('"', "'").replace('\n', ' ')

def add_edge(edges, a, b, label=''):
    if a and b and a != b:
        edges.add((a, b, label))

def first_heading(readme: str):
    for line in readme.splitlines():
        s = line.strip()
        if s.startswith('#'):
            return s.lstrip('#').strip()
    for line in readme.splitlines():
        s = line.strip()
        if s:
            return s[:80]
    return ''

def detect_domain(name: str, text: str):
    s = f'{name}\n{text}'.lower()
    rules = [
        ('礼物/打赏', ['gift', 'sendgift', 'props', 'bag', 'billboard', 'wall']),
        ('权益/特权', ['privilege', 'guard', 'fans_club', 'family', 'shopping', 'experiencecard']),
        ('基础服务', ['basic', 'serviceinfo', 'clientproxy', 'commonpush', 'survey', 'smartrobot']),
        ('增长/玩法', ['growth', 'play', 'lucky_bag', 'task']),
        ('权限/管理后台', ['authority', 'backend', 'management']),
        ('充值/计费支撑', ['charge', 'bill']),
    ]
    hits = []
    for domain, keys in rules:
        if any(k in s for k in keys):
            hits.append(domain)
    return hits[:3] or ['业务服务']

def scan_project(project: Path):
    files = list(iter_files(project))
    rel_files = [str(p.relative_to(project)) for p in files]
    ext_counter = Counter(p.suffix.lower() or p.name for p in files)
    top_dirs = Counter(str(Path(r).parts[0]) for r in rel_files if len(Path(r).parts) > 1)

    readmes = [p for p in files if p.name.lower().startswith('readme')]
    readme_text = redact('\n\n'.join(safe_read(p, 80_000) for p in readmes))
    all_go_files = [p for p in files if p.suffix == '.go']
    all_go_text = ''
    per_file_text = {}
    for p in all_go_files:
        t = safe_read(p, 80_000)
        per_file_text[p] = t
        all_go_text += '\n' + t

    imports = Counter()
    local_imports = Counter()
    import_re = re.compile(r'import\s*\((.*?)\)|import\s+"([^"]+)"', re.S)
    quoted_re = re.compile(r'"([^"]+)"')
    for m in import_re.finditer(all_go_text):
        block, single = m.group(1), m.group(2)
        vals = [single] if single else quoted_re.findall(block or '')
        for imp in vals:
            root = imp.split('/')[0]
            if imp.startswith('git.inke.cn/'):
                parts = imp.split('/')
                local_imports['/'.join(parts[:5]) if len(parts) >= 5 else imp] += 1
            elif root not in {'context', 'fmt', 'time', 'strings', 'strconv', 'encoding', 'net', 'errors', 'sync', 'sort', 'math'}:
                imports[root] += 1

    handler_files = []
    service_files = []
    dao_files = []
    model_files = []
    task_files = []
    rpc_files = []
    external = Counter()
    endpoints = []
    structs = []
    funcs = []
    for p, t in per_file_text.items():
        rel = str(p.relative_to(project))
        low = rel.lower() + '\n' + t.lower()
        if '/http/' in '/' + rel.lower() or 'httpserver' in low or 'gin.' in low:
            handler_files.append(rel)
        if '/service/' in '/' + rel.lower() or re.search(r'type\s+Service\s+struct', t):
            service_files.append(rel)
        if any(x in '/' + rel.lower() for x in ['/dao/', '/repo/', '/repository/', '/db/', '/mysql/']):
            dao_files.append(rel)
        if '/model/' in '/' + rel.lower() or '/entity/' in '/' + rel.lower():
            model_files.append(rel)
        if any(x in low for x in ['cron', 'ticker', 'timer', 'job', 'task']):
            task_files.append(rel)
        if any(x in low for x in ['thrift', 'grpc', 'rpc']):
            rpc_files.append(rel)
        for key, label in [
            ('redis', 'Redis'), ('mysql', 'MySQL'), ('mongo', 'MongoDB'), ('kafka', 'Kafka'),
            ('pulsar', 'Pulsar'), ('elastic', 'Elasticsearch'), ('clickhouse', 'ClickHouse'),
            ('http', 'HTTP/外部接口'), ('thrift', 'Thrift/RPC'), ('grpc', 'gRPC'),
            ('daenerys', 'Daenerys 框架'), ('gorm', 'GORM'), ('xorm', 'XORM')
        ]:
            if key in low:
                external[label] += 1
        for mm in re.finditer(r'(?:GET|POST|PUT|DELETE|PATCH)\s+[`" ]([^`"\s]+)', t):
            if len(endpoints) < 20:
                endpoints.append(mm.group(1))
        for mm in re.finditer(r'func\s+(?:\([^)]*\)\s*)?([A-Z][A-Za-z0-9_]{2,})\s*\(', t):
            if len(funcs) < 40:
                funcs.append(mm.group(1))
        for mm in re.finditer(r'type\s+([A-Z][A-Za-z0-9_]{2,})\s+struct', t):
            if len(structs) < 40:
                structs.append(mm.group(1))

    ci = any(p.name == '.gitlab-ci.yml' for p in project.iterdir() if p.is_file())
    lint = any(p.name == '.golangci.yml' for p in project.iterdir() if p.is_file())
    tests = [str(p.relative_to(project)) for p in project.rglob('*_test.go') if all(x not in p.parts for x in SKIP_DIRS)]
    api_docs = [str(p.relative_to(project)) for p in files if p.suffix.lower() in {'.proto', '.thrift'}]

    return {
        'name': project.name,
        'path': str(project),
        'file_count': len(files),
        'go_count': len(all_go_files),
        'ext_counter': ext_counter,
        'top_dirs': top_dirs,
        'readme_heading': first_heading(readme_text),
        'readme_excerpt': '\n'.join([ln.strip() for ln in readme_text.splitlines() if ln.strip()][:12]),
        'domains': detect_domain(project.name, readme_text),
        'imports': imports,
        'local_imports': local_imports,
        'handler_files': sorted(set(handler_files))[:20],
        'service_files': sorted(set(service_files))[:20],
        'dao_files': sorted(set(dao_files))[:20],
        'model_files': sorted(set(model_files))[:20],
        'task_files': sorted(set(task_files))[:20],
        'rpc_files': sorted(set(rpc_files))[:20],
        'external': external,
        'endpoints': endpoints,
        'structs': structs,
        'funcs': funcs,
        'ci': ci,
        'lint': lint,
        'tests': tests[:20],
        'api_docs': api_docs[:20],
    }

def render(info):
    name = info['name']
    nodes = set()
    edges = set()
    def node(label):
        nodes.add(label)
        return label
    center = node(name)
    for d in info['domains']:
        add_edge(edges, center, node('领域: ' + d), 'domain')
    if info['handler_files']:
        add_edge(edges, center, node('接入层 HTTP/API'), 'exposes')
        for f in info['handler_files'][:5]: add_edge(edges, '接入层 HTTP/API', node(f), '')
    if info['rpc_files']:
        add_edge(edges, center, node('RPC/IDL 调用'), 'uses')
        for f in info['rpc_files'][:5]: add_edge(edges, 'RPC/IDL 调用', node(f), '')
    if info['service_files']:
        add_edge(edges, center, node('业务服务层'), 'core')
        for f in info['service_files'][:7]: add_edge(edges, '业务服务层', node(f), '')
    if info['dao_files']:
        add_edge(edges, center, node('数据访问层'), 'persists')
        for f in info['dao_files'][:7]: add_edge(edges, '数据访问层', node(f), '')
    if info['model_files']:
        add_edge(edges, center, node('模型/DTO'), 'defines')
        for f in info['model_files'][:5]: add_edge(edges, '模型/DTO', node(f), '')
    if info['task_files']:
        add_edge(edges, center, node('任务/定时处理'), 'schedules')
        for f in info['task_files'][:5]: add_edge(edges, '任务/定时处理', node(f), '')
    if info['external']:
        ext = node('外部依赖')
        add_edge(edges, center, ext, 'depends')
        for k, _ in info['external'].most_common(10): add_edge(edges, ext, node(k), '')
    if info['local_imports']:
        li = node('公司内部包')
        add_edge(edges, center, li, 'imports')
        for k, _ in info['local_imports'].most_common(8): add_edge(edges, li, node(k), '')
    if info['ci'] or info['lint'] or info['tests']:
        q = node('工程质量')
        add_edge(edges, center, q, 'quality')
        if info['ci']: add_edge(edges, q, node('GitLab CI'), '')
        if info['lint']: add_edge(edges, q, node('golangci-lint'), '')
        if info['tests']: add_edge(edges, q, node(f"测试文件 {len(info['tests'])} 个"), '')

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
    top_lines = ', '.join(f'{k}({v})' for k, v in info['top_dirs'].most_common(10)) or '根目录为主'
    imports = ', '.join(f'{k}({v})' for k, v in info['imports'].most_common(10)) or '主要为标准库/内部包'
    local_imports = '\n'.join(f'- `{k}`: {v}' for k, v in info['local_imports'].most_common(12)) or '- 未发现显著公司内部 import'
    external = '\n'.join(f'- {k}: {v} 处信号' for k, v in info['external'].most_common(12)) or '- 未发现明显中间件信号'
    endpoints = '\n'.join(f'- `{x}`' for x in info['endpoints'][:20]) or '- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认'
    structs = ', '.join(info['structs'][:30]) or '未提取到导出结构体'
    funcs = ', '.join(info['funcs'][:30]) or '未提取到导出函数/方法'
    tests = '\n'.join(f'- `{x}`' for x in info['tests']) or '- 未发现 `_test.go`'
    api_docs = '\n'.join(f'- `{x}`' for x in info['api_docs']) or '- 未发现 proto/thrift 文件'
    dirs = '\n'.join(f'- `{k}`: {v} 个文本/代码文件' for k, v in info['top_dirs'].most_common(12)) or '- 根目录为主'
    readme = info['readme_excerpt'] or '未发现 README 或 README 内容为空'

    return f'''# {name} 技术图谱

## 一图技术图谱
{chr(10).join(mermaid)}

## 项目定位
- 源码路径：`{info['path']}`
- 领域判断：{', '.join(info['domains'])}
- README 摘要：{info['readme_heading'] or '无标题'}

```text
{readme}
```

## 静态结构画像
- 文本/代码文件数：{info['file_count']}
- Go 文件数：{info['go_count']}
- 文件类型分布：{ext_lines}
- 顶层目录分布：{top_lines}

## 关键目录
{dirs}

## 代码分层
- 接入层文件：{len(info['handler_files'])} 个
- 服务层文件：{len(info['service_files'])} 个
- 数据访问文件：{len(info['dao_files'])} 个
- 模型文件：{len(info['model_files'])} 个
- 任务/定时相关文件：{len(info['task_files'])} 个
- RPC/IDL 相关文件：{len(info['rpc_files'])} 个

## API/路由线索
{endpoints}

## 核心类型与方法线索
- 导出结构体：{structs}
- 导出函数/方法：{funcs}

## 外部依赖线索
{external}

## 内部依赖线索
{local_imports}

## 第三方 import 概览
- {imports}

## IDL/协议文件
{api_docs}

## 工程质量与交付
- GitLab CI：{'有' if info['ci'] else '未发现'}
- golangci-lint：{'有' if info['lint'] else '未发现'}
- 测试文件：
{tests}

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
'''

projects = sorted([p for p in SRC_ROOT.iterdir() if p.is_dir()])
manifest = []
for project in projects:
    info = scan_project(project)
    out = OUT_ROOT / f'{project.name}-技术图谱.md'
    out.write_text(render(info), encoding='utf-8')
    manifest.append({'project': project.name, 'path': str(project), 'output': str(out), 'files': info['file_count'], 'go_files': info['go_count'], 'domains': info['domains']})

(OUT_ROOT / 'busi-技术图谱生成清单.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'count': len(manifest), 'out': str(OUT_ROOT)}, ensure_ascii=False))
PY
