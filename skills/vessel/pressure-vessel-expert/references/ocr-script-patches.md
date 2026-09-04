# OCR 脚本补丁记录（process_pdf 系列）

> 维护人：J.A.R.V.I.S. | 2026-06-30 立
> 适用于 `vessel/pressure-vessel-expert/scripts/` 与 `vessel/storage-tank-expert/scripts/` 下 4 个脚本

---

## 补丁 1：`process_pdf_batch.py` OOM 修复（关键）

**症状**：扫描版大 PDF（>150 页，>20MB）跑 `--ocr` 时，进程被 OOM Killer 杀掉。

**根因**：`extract_with_ocr()` 函数第 73 行用 `convert_from_path(path, dpi=dpi)`（**无页数限制**）来取总页数。这一行会一次性把整本 PDF 的所有页都解码为 PIL Image 列表。对于 461 页 / 80MB 的 GB150 PDF，单次调用会加载约 5-6 GB 内存（461 页 × 11.6 MB/页 @ 200 DPI A4），直接 OOM。

**修复**：改用 `pdfinfo` CLI 子进程取总页数（只读 metadata，几 KB 内存）。

```python
# ❌ 错误: 一次性加载所有页只为取页数
total = len(convert_from_path(str(pdf_path), dpi=dpi))

# ✅ 正确: pdfinfo 子进程, 只读 metadata
result = subprocess.run(['pdfinfo', str(pdf_path)], capture_output=True, text=True)
total = 0
for line in result.stdout.split('\n'):
    if line.startswith('Pages:'):
        total = int(line.split(':', 1)[1].strip())
        break
if total == 0:
    raise RuntimeError(f"无法从 pdfinfo 获取总页数: {pdf_path}")
```

**触发条件**：任何 `--ocr` 模式 + PDF 页数 > 150 / 文件 > 20MB。

**验证**：461 页 GB150 PDF 跑 200 DPI OCR 全本（30-60 分钟），峰值 RSS 稳定在 ~150-200 MB（vs 修复前 5-6 GB 直接 OOM）。

---

## 补丁 2：`process_pdf.py` 索引格式兼容（重要）

**症状**：`process_pdf.py --search "<关键词>"` 在条目数 > 1 的索引上崩溃：

```
KeyError: 'txt_path'
```

**根因**：`cmd_search()` 函数硬编码 `info["txt_path"]`，但历史索引条目分两种格式：

- **新格式**（`process_pdf_batch.py` 写入）：`{"txt_path": "...", "extracted_txt": "...", ...}`
- **旧格式**（早期人工或迁移脚本写入）：`{"file": "...txt", "size": ..., "lines": ..., "chars": ..., "encoding": "utf-8"}`

老条目（34 条历史标准）缺 `txt_path`，search 必崩。

**修复**：3 级 fallback 兼容新旧两种格式：

```python
txt_path_str = info.get("txt_path")
if not txt_path_str:
    if info.get("extracted_txt"):
        txt_path_str = str(EXTRACTED_DIR / info["extracted_txt"])
    elif info.get("file", "").endswith(".txt"):
        txt_path_str = str(EXTRACTED_DIR / info["file"])
    elif pdf_name.endswith(".txt"):
        txt_path_str = str(EXTRACTED_DIR / pdf_name)
if not txt_path_str:
    continue
```

**触发条件**：当索引同时含新旧两种格式条目，且 search 跨条目运行。

**未来规则**：新写脚本时，所有 `info[...]` 字段访问都应 `info.get("...", default)` + 三级 fallback，**不要硬编码单一字段名**。

---

## 补丁 3：环境依赖（一次记录）

**问题**：首次跑 OCR 失败 `ModuleNotFoundError: No module named 'pytesseract'`。

**修复**（在 `/home/hermes-admin/venv` 安装）：
```bash
uv pip install --python /home/hermes-admin/venv/bin/python pytesseract pdf2image
```

**系统依赖**（tesseract 二进制 + 中文简体语言包）：
- `tesseract` (apt: `tesseract-ocr tesseract-ocr-chi-sim`)
- `pdftoppm` (poppler-utils)
- `pdfinfo` (poppler-utils)

⚠️ 若是新机器或新 venv，**先装这三个系统包**再装 Python wrapper，否则跑 OCR 必失败。

---

## OCR 任务最佳实践

**前置**：
1. 探页数：`pdfinfo` → 461 页
2. 探文件类型：先 `pdftotext -l 3` 看字符数（>200 = 文字型，可直接提取；<200 = 扫描版，必须 OCR）
3. 备份旧 extracted：`.OBSOLETE-<date>` 后缀保留作史鉴

**跑**：
- 单本：`process_pdf_batch.py --file "<pdf>" --ocr --dpi 200`
- 全本：`process_pdf_batch.py --all --ocr --dpi 200`（按 `--ocr --dpi 200` 是默认安全档；>150 页推荐 120 DPI + 50 页一批）
- 后台跑：terminal `background=true, notify_on_complete=true`，避免阻塞会话

**质量校验**：
```bash
# 抽查特定页内容
awk '/第 50 页/,/第 51 页/' extracted/<file>.txt

# 关键术语命中数（必须 > 0 才算 OCR 成功）
grep -c "开孔补强" extracted/<file>.txt  # 应 > 10
```

**索引更新**：`process_pdf_batch.py` 自动写 `index.json`，无需手工。
