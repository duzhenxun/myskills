# 职位系统

一个基于本地 JSON 的轻量职位后台，用来查看 `boss_ai_jobs_ai_engineer_all_2026-05-29.json` 里的岗位数据。

## 功能

- 职位列表浏览
- 搜索职位 / 公司 / 技能 / 地区 / 描述
- 按详情状态筛选
- 按薪资排序
- 点击职位弹出详情，查看描述、福利、招聘者、地址和原始链接
- 如果职位缺少描述，点开时会自动现场补抓，并回写本地 `jobs.json`

## 启动

因为页面现在支持点开职位时现场补详情，所以需要运行项目自带的本地服务：

```bash
cd /Users/dds/data/ai/work/job-system
python3 server.py
```

然后在浏览器打开：

```text
http://localhost:8000
```

## 数据文件

- 页面读取：`/Users/dds/data/ai/work/job-system/data/jobs.json`

如果你后续更新了岗位 JSON，只要覆盖这个文件并刷新页面即可。
