#!/usr/bin/env bash
# 便捷脚本：使用 uv run 运行 port-selector
# 用法: ./run.sh [参数]
# 示例: ./run.sh --start-port 3000 --end-port 4000

uv run port-selector "$@"
