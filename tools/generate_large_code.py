#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/generate_large_code.py

用途：在仓库中生成大量占位源码文件以达到指定行数或文件数（含中文注释），用于规模/压力测试或在开发中快速填充示例源代码。

说明：
- 生成的文件为可编译的 C/C++ 占位源文件（.c/.cpp）与对应头文件（.h），每个源文件包含一个简单的函数用于避免完全空文件。
- 支持两种生成策略：按文件数与每文件行数，或按目标总行数自动拆分。
- 生成的内容尽量具备正确的编码与最小编译可用性，适用于仓库占位、CI/存储压力测试或示例数据。
- 警告：请勿将生成的大量占位文件直接用于生产代码库；仅用于测试或临时占位。

示例用法：
  python3 tools/generate_large_code.py --out generated_placeholders --files 200 --lines 10000 --lang c
  python3 tools/generate_large_code.py --out generated_placeholders --total-lines 5000000 --lang c

Author: Copilot (代写)
"""

from __future__ import annotations
import argparse
import math
import os
from pathlib import Path
import sys
from typing import Tuple

# 模板：头文件
TEMPLATE_H = '''/*
 * {filename} - 自动生成的占位头文件（含中文注释）
 * 说明：此文件由 tools/generate_large_code.py 自动生成，仅用于规模/压力测试。
 */

#ifndef _PLACEHOLDER_{idx}_H_
#define _PLACEHOLDER_{idx}_H_

#ifdef __cplusplus
extern "C" {{
#endif

void placeholder_{idx}(void);

#ifdef __cplusplus
}}
#endif

#endif /* _PLACEHOLDER_{idx}_H_ */
'''

# 模板：C 源文件
TEMPLATE_C = '''/*
 * {filename} - 自动生成的占位 C 源码（含中文注释）
 * 说明：此文件由 tools/generate_large_code.py 自动生成，仅用于规模/压力测试。
 */

#include <stdio.h>
#include "{hdr_name}"

void placeholder_{idx}(void) {{
    /* 这是第 {idx} 个占位函数，用于产生行数并演示注释规范 */
    (void)printf("占位函数 {idx} 执行\n");
}}
'''

# 模板：C++ 源文件
TEMPLATE_CPP = '''/*
 * {filename} - 自动生成的占位 C++ 源码（含中文注释）
 * 说明：此文件由 tools/generate_large_code.py 自动生成，仅用于规模/压力测试。
 */

#include <iostream>
#include "{hdr_name}"

void placeholder_{idx}(void) {{
    /* 这是第 {idx} 个占位函数，用于产生行数并演示注释规范 */
    std::cout << "占位函数 {idx} 执行\n";
}}
'''

# 每个文件中用于填充的注释行模板
FILL_LINE = "/* 自动生成行：用于填充仓库行数以做压力测试（中文注释）。 */\n"

# 限制与安全检查
MAX_TOTAL_LINES = 20_000_000  # 为避免滥用，默认上限为 20M 行，可按需调整
MAX_FILES = 20000  # 最大文件数限制

def calc_files_and_lines(files: int, lines: int, total_lines: int) -> Tuple[int,int]:
    """计算最终要生成的文件数与每文件行数。

    优先级：如果指定 total_lines，则忽略 files/lines 的组合，按 total_lines 进行均匀分配。
    否则使用 files 与 lines 参数直接执行生成。
    """
    if total_lines > 0:
        if total_lines > MAX_TOTAL_LINES:
            raise ValueError(f"请求总行数太大（>{MAX_TOTAL_LINES}），请缩小规模或调整脚本上限。")
        # 先决定文件数（保持在合理上限），尝试使用 files if provided otherwise自动计算
        if files <= 0:
            # 以每文件默认 5000 行为基准计算文件数
            default_per_file = 5000
            files = max(1, min(MAX_FILES, math.ceil(total_lines / default_per_file)))
        # 计算每文件行数，向上取整
        lines = math.ceil(total_lines / files)
        return files, lines
    else:
        if files <= 0 or lines <= 0:
            raise ValueError("请通过 --files 与 --lines 指定生成规模，或使用 --total-lines 指定总行数。")
        if files > MAX_FILES:
            raise ValueError(f"请求文件数过多（>{MAX_FILES}），请减少文件数或调整脚本上限。")
        total = files * lines
        if total > MAX_TOTAL_LINES:
            raise ValueError(f"生成总行数将超过上限（{total} > {MAX_TOTAL_LINES}），请降低 files 或 lines。")
        return files, lines

def generate(target_dir: Path, files: int, lines_per_file: int, language: str) -> None:
    """在目标目录生成占位源码与头文件。

    每个文件会生成一个 .c/.cpp 源文件与一个 .h 头文件。
    每个源文件开头包含实际函数定义，后续用注释行填充以达到目标行数。
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"开始生成：目标目录={{target_dir}} files={{files}} lines_per_file={{lines_per_file}} lang={{language}}")

    for i in range(1, files + 1):
        idx = i
        if language == 'c':
            src_name = f"placeholder_{{idx}}.c"
        else:
            src_name = f"placeholder_{{idx}}.cpp"
        hdr_name = f"placeholder_{{idx}}.h"

        src_path = target_dir / src_name
        hdr_path = target_dir / hdr_name

        # 写头文件
        with hdr_path.open('w', encoding='utf-8') as hf:
            hf.write(TEMPLATE_H.format(filename=hdr_path.name, idx=idx))

        # 写源文件模板
        if language == 'c':
            base = TEMPLATE_C.format(filename=src_path.name, hdr_name=hdr_name, idx=idx)
        else:
            base = TEMPLATE_CPP.format(filename=src_path.name, hdr_name=hdr_name, idx=idx)

        base_lines = base.count('\n') + 1
        remaining = max(0, lines_per_file - base_lines)

        with src_path.open('w', encoding='utf-8') as sf:
            sf.write(base)
            # 为避免大量小写写入导致性能问题，批量写入注释块
            if remaining > 0:
                block = (FILL_LINE * 1000)
                full_blocks = remaining // 1000
                tail = remaining % 1000
                for _ in range(full_blocks):
                    sf.write(block)
                if tail:
                    sf.write(FILL_LINE * tail)

        if i % max(1, files//10) == 0 or i == files:
            print(f"已生成 {{i}}/{{files}} 文件")

    print("生成完成。")

def main(argv=None):
    p = argparse.ArgumentParser(description="生成大量占位源码以填充仓库行数（含中文注释）")
    p.add_argument("--out", "-o", default="generated_placeholders", help="输出目录（相对于仓库根）")
    p.add_argument("--files", "-f", type=int, default=0, help="要生成的文件数（可选）")
    p.add_argument("--lines", "-l", type=int, default=0, help="每个文件目标行数（近似，可选）")
    p.add_argument("--total-lines", "-t", type=int, default=0, help="目标总行数（可选，优先）")
    p.add_argument("--lang", choices=["c", "cpp"], default="c", help="生成语言: c 或 cpp")
    p.add_argument("--max-total-lines", type=int, default=MAX_TOTAL_LINES, help="调整允许的总行数上限（慎用）")
    args = p.parse_args(argv)

    # 调整上限（仅当显式传入时）
    global MAX_TOTAL_LINES
    if args.max_total_lines:
        MAX_TOTAL_LINES = args.max_total_lines

    try:
        files, lines = calc_files_and_lines(args.files, args.lines, args.total_lines)
    except ValueError as e:
        print(f"参数错误: {{e}}")
        sys.exit(2)

    # 限制判断
    if files <= 0 or lines <= 0:
        print("计算后文件数或每文件行数非法，请检查参数")
        sys.exit(2)

    out_dir = Path(args.out)

    # 保证生成目录位于仓库内（简单检查）
    repo_root = Path(__file__).resolve().parent.parent
    try:
        out_dir = (repo_root / args.out).resolve()
    except Exception:
        out_dir = repo_root / args.out

    if str(out_dir).find(str(repo_root)) != 0:
        print("为了安全，输出目录必须位于仓库根目录之下")
        sys.exit(2)

    # 避免误操作：如果目录已存在且非空，则要求确认（交互模式）
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"警告：输出目录 {{out_dir}} 已存在并非空。\n将继续写入，这可能覆盖已有自动生成文件。\n按 Ctrl-C 取消以中止。")

    generate(out_dir, files, lines, args.lang)
    print("提示：生成完成后请将生成目录加入 .gitignore 或根据需要提交到仓库。")


if __name__ == '__main__':
    main()
