# PDF 完整性诊断（2026-07-01 GB150 截断事件固化）

> **触发场景**：用户/脚本说 PDF "OCR 失败" 或 "pdfinfo 报错"，但实际可能是 PDF 文件本身损坏，不是脚本 bug。

---

## 损坏 PDF 的典型症状

| 症状 | 含义 | 后果 |
|------|------|------|
| `pdfinfo` 报 "Couldn't find trailer dictionary" | 缺 trailer（xreftable 起点）| pdfinfo 无法解析 |
| `pdfinfo` 报 "Couldn't read xref table" | 缺 xref（交叉引用表）| 无法定位对象 |
| `pdfinfo` 报 "Catalog dictionary not located" | 缺 root catalog | 整个文件无法打开 |
| 文件**无 `%%EOF` 标记** | 缺文件结束标记 | 说明文件**被截断** |
| `head -c 8` 显示 `%PDF-1.x` 但 `tail -c 16` 是乱码 | 头部完整，尾部损坏 | 几乎确定是**上传截断** |
| 文件大小**远小于**声称大小 | 10 MB 的 PDF 实际只有 1 MB | **截断** |
| pdftotext 全文 0 字符 + 无 Pages 字段 | 元数据全丢 | 重建也无用 |

---

## 快速诊断流程（5 步）

```bash
# 1. 文件大小（与声称大小对比）
ls -la <file>.pdf

# 2. 头部检查
head -c 16 <file>.pdf | xxd    # 应为 "25 50 44 46 2d 31 2e" = "%PDF-1."

# 3. 尾部检查
tail -c 32 <file>.pdf | xxd    # 末尾应为 "%%EOF\r\n" = "25 25 45 4f 46"

# 4. 关键关键字
grep -c "%%EOF" <file>.pdf      # 应 ≥ 1
grep -c "trailer" <file>.pdf    # 应 ≥ 1
grep -c "xref" <file>.pdf      # 应 ≥ 1

# 5. pdfinfo 报错
pdfinfo <file>.pdf 2>&1        # 看 Pages: 行
```

**判定**：
- 头部 `25 50 44 46` + 缺 `%%EOF` + 缺 `trailer` + 缺 `xref` → **几乎确定是截断**
- `pdfinfo` 报 trailer/xref/catalog 错误 → 修复工具（pdftk / qpdf / gs）通常**无效**

---

## 修复尝试（按成功率排序）

| 工具 | 命令 | 适用 | 成功率 |
|------|------|------|--------|
| **qpdf** | `qpdf --decrypt --object-streams=disable <file>.pdf /tmp/repaired.pdf` | xref 缺失但 trailer 完整 | 中 |
| **pdftk** | `pdftk <file>.pdf output /tmp/repaired.pdf` | 简单损坏 | 中 |
| **Ghostscript** | `gs -o /tmp/repaired.pdf -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress <file>.pdf` | 任何损坏 | **低**（截断文件通常重建失败，输出 2KB stub） |
| **mutool** | `mutool clean <file>.pdf /tmp/repaired.pdf` | 对象流损坏 | 中 |

**实测（2026-07-01 GB150 事件）**：
- Ghostscript 修复后只输出 2 KB 假页（"Couldn't initialise file"）→ **无效**
- qpdf / pdftk 不可用（未安装）→ **无解**
- **唯一解决方案**：Sir 重新上传完整文件（21 MB 而不是 10 MB）

---

## 防御性检查（**新增 PDF 必做**）

**任何新放入 `knowledge/standards/` 的 PDF，先跑完整性检查**：

```bash
PDF="<new-file>.pdf"
# 1. 头部
head -c 8 "$PDF" | xxd | grep -q "50 44 46 2d" && echo "✅ 头部 OK" || echo "❌ 头部异常"
# 2. 末尾
tail -c 16 "$PDF" | xxd | grep -q "45 4f 46 0d 0a" && echo "✅ 末尾 OK" || echo "❌ 末尾异常"
# 3. EOF 标记
grep -q "%%EOF" "$PDF" && echo "✅ %%EOF 存在" || echo "❌ 缺 %%EOF"
# 4. pdfinfo
pdfinfo "$PDF" 2>&1 | grep -q "^Pages:" && echo "✅ Pages 元数据" || echo "❌ 元数据异常"
# 5. 大小合理性
SIZE=$(stat -c '%s' "$PDF")
[ $SIZE -gt 1000000 ] && echo "✅ 文件 > 1MB" || echo "❌ 文件太小（< 1MB）"
```

**任一失败**：让 Sir 重新上传，**不要**尝试 OCR（浪费时间，会产乱码）。

---

## 与 OCR 失败的区分

| 症状 | 真因 | 处理 |
|------|------|------|
| `pdfinfo` 正常 + pdftotext < 200 字符 | 扫描版 PDF | OCR 流程 |
| `pdfinfo` 报错 + 头部 OK + 缺 `%%EOF` | **截断 PDF** | **重新上传**（不是 OCR 问题）|
| pdftotext 0 字符 + pdfinfo 报 trailer/xref 缺失 | **结构性损坏** | 重新上传 |
| OCR 中途 OOM（pdftotext 转换图像时） | 大 PDF OOM bug | 用 `pdfinfo` 取页数 + 逐页处理 |

---

## 历史案例

### 2026-07-01：GB 150 PDF 截断事件

- **现象**：Sir 上传 `压力容器设计工程师培训教程-基础知识零部件.pdf` → `pdfinfo` 报 "Couldn't find trailer dictionary"
- **诊断**：文件**只有 10.3 MB**，原文件应是 ~21 MB（Sir 后来重传后大小 20.7 MB）
- **症状链**：
  1. 文件头 `%PDF-1.6` 正确
  2. 文件尾 32 字节是乱码（无 `%%EOF`）
  3. 无 `xref` 表 / `trailer` 字典
- **错误尝试**：Ghostscript 修复 → 输出 2 KB 假页，失败
- **正确解**：Sir 重新上传完整文件 → OCR 461 页成功（20.7 MB → 797 KB extracted 文本）

**教训**：发现 `pdfinfo` 报 trailer/xref 错误 + 缺 `%%EOF` → **第一时间要求 Sir 重新上传**，不要尝试修复（成功率 < 5%）。

---

## 不可保存的约束

- ❌ "pdftk / qpdf 永远能修复 PDF" → 错，截断文件基本无解
- ❌ "gs 一定能重建" → 错，对结构性损坏的 PDF 输出的是空 stub
- ✅ 唯一可靠方案：**Sir 重新上传**完整文件