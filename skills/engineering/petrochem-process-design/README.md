# petrochem-process-design 资源目录

本目录为石油化工小试/中试工艺设计技能的知识资源库。

## 目录结构

```
petrochem-process-design/
├── SKILL.md                    # 技能主文件（已存在）
├── references/                 # 参考文档、规范标准
│   └── （存放 GB/SH/AQ 等规范 PDF 或说明文档）
├── templates/                  # 模板文件
│   └── （PFD/P&ID 模板、计算书模板、HAZOP 分析表等）
├── scripts/                    # 辅助脚本
│   └── （物料衡算、热量计算、设备选型等计算脚本）
├── assets/                     # 静态资源
│   └── （图标、示意图、流程图素材等）
└── knowledge/                  # 知识库
    ├── standards/              # 标准规范
    │   └── （GB 50160、SH/T 3010、GB/T 50493 等）
    └── examples/               # 案例库
        └── （典型装置设计案例、放大经验等）
```

## 使用建议

| 目录 | 用途 | 推荐格式 |
|------|------|----------|
| `references/` | 行业规范、技术手册 | PDF、MD |
| `templates/` | 可复用模板 | MD、XLSX、DOCX |
| `scripts/` | 计算工具脚本 | Python (.py) |
| `assets/` | 图片、示意图 | PNG、SVG |
| `knowledge/standards/` | 国家标准、行业标准 | PDF |
| `knowledge/examples/` | 设计案例、经验总结 | MD、PDF |

## 上传文件后

上传文件后，建议更新 `SKILL.md` 中的相关引用，或在 `references/` 中添加索引文件说明文档内容。
