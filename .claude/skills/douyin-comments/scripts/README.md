# douyin-comments scripts

## extract-comments.js

用途：

- 打开抖音 `modal_id` 详情页
- 激活评论面板
- 尝试滚动并提取当前环境下可访问到的评论
- 保存为桌面文本文件

示例：

```bash
node extract-comments.js "https://www.douyin.com/jingxuan?modal_id=7632657462063140130"
```

自定义输出路径：

```bash
node extract-comments.js "https://www.douyin.com/jingxuan?modal_id=7632657462063140130" "/Users/dds/Desktop/comments.txt"
```

说明：

- 该脚本依赖 `playwright-cli`
- 输出结果是“当前环境下稳定提取到的评论”，不保证一定拿到全部评论
- 如果抖音限制接口或懒加载，输出数量可能小于页面显示的总评论数
