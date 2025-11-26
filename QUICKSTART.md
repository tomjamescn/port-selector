# Port Selector - 快速使用指南

## 最简单的使用方式

### 1. 交互式运行（推荐）

```bash
# 直接运行，程序会引导你输入配置
uv run port-selector
```

### 2. 使用默认值快速运行

```bash
# 在 8000-9000 范围内查找 5 个可用端口
uv run port-selector --non-interactive
```

### 3. 指定参数运行

```bash
# 查找端口范围 3000-4000 中的 10 个可用端口
uv run port-selector --start-port 3000 --end-port 4000 --count 10 --non-interactive
```

### 4. 使用便捷脚本

```bash
# 赋予执行权限（只需一次）
chmod +x run.sh

# 交互式运行
./run.sh

# 带参数运行
./run.sh --start-port 3000 --end-port 4000 --non-interactive
```

## 常用命令示例

```bash
# 在当前目录查找可用端口，自动排除 docker-compose 中的端口
uv run port-selector

# 扫描特定目录
uv run port-selector --scan-dir /path/to/your/project

# 查找更多端口
uv run port-selector --count 20 --non-interactive

# 查找 Node.js 常用端口范围
uv run port-selector --start-port 3000 --end-port 4000

# 查找数据库常用端口范围
uv run port-selector --start-port 5000 --end-port 6000
```

## 所有可用选项

```
--start-port INTEGER       起始端口（默认: 8000）
--end-port INTEGER         结束端口（默认: 9000）
--scan-dir PATH            扫描目录（默认: 当前目录）
--count INTEGER            查找端口数量（默认: 5）
--non-interactive          非交互模式
--help                     显示帮助信息
```

## 输出说明

工具会显示：
- ✓ 绿色：端口可用
- ⚠ 黄色：警告信息（如被 docker-compose 排除的端口）
- ℹ 蓝色：信息提示
- ✗ 红色：错误信息

## 工作流程

1. 扫描指定目录及子目录中的所有 docker-compose.yml/yaml 文件
2. 提取这些文件中定义的所有端口
3. 在指定范围内搜索可用端口（跳过 docker-compose 中的端口）
4. 使用 lsof 验证端口是否真的可用
5. 显示结果和进程信息（如果端口被占用）

## 故障排除

**Q: 提示找不到 uv 命令？**
```bash
# 安装 UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Q: 权限错误？**
```bash
# 使用 sudo 运行（检测 1-1023 特权端口时）
sudo uv run port-selector --start-port 80 --end-port 1024
```

**Q: 想要更详细的信息？**
工具已经显示了所有关键信息。如果需要手动验证：
```bash
# 手动检查端口 8080
lsof -i:8080
```
