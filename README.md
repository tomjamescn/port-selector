# Port Selector

一个交互式命令行工具，帮助你快速找到可用的端口。

## 功能特性

- 🔍 **智能扫描**: 递归扫描目录中的 docker-compose 文件，识别已使用的端口
- ✅ **端口验证**: 使用 `lsof` 命令验证端口是否真的空闲
- 🎯 **交互式界面**: 友好的命令行交互，引导你完成配置
- ⚡ **快速查找**: 在指定范围内快速找到可用端口
- 📊 **详细报告**: 清晰展示端口状态和进程信息

## 快速开始

### 方法一：使用 UV 直接运行（推荐，无需安装）

```bash
# 克隆项目
git clone <repository-url>
cd port-selector

# 方式1: 使用 uv run（推荐）
uv run port-selector

# 方式2: 使用 uvx
uvx --from . port-selector

# 方式3: 使用便捷脚本
chmod +x run.sh
./run.sh

# 非交互模式
uv run port-selector --non-interactive

# 指定参数
uv run port-selector --start-port 3000 --end-port 4000 --scan-dir . --count 10

# 使用脚本指定参数
./run.sh --start-port 3000 --end-port 4000 --non-interactive
```

> 💡 **提示**: 查看 [QUICKSTART.md](QUICKSTART.md) 获取更多使用示例和常用命令

### 方法二：安装后使用

```bash
# 使用 UV 安装
uv pip install -e .

# 或使用 pip
pip install -e .

# 然后直接运行
port-selector
```

## 使用方法

### 交互式模式（推荐）

直接运行命令，程序会引导你完成配置：

```bash
# 使用 uv run
uv run port-selector

# 或已安装
port-selector
```

程序会询问：
1. 起始端口（默认: 8000）
2. 结束端口（默认: 9000）
3. 要扫描的目录（默认: 当前目录）
4. 需要找到多少个可用端口（默认: 5）

### 非交互式模式

使用命令行参数直接指定配置：

```bash
# 在 8000-9000 范围内查找 5 个可用端口
uv run port-selector --start-port 8000 --end-port 9000 --scan-dir . --count 5

# 非交互模式（使用默认值）
uv run port-selector --non-interactive

# 指定特定范围
uv run port-selector --start-port 3000 --end-port 4000 --scan-dir /path/to/project
```

### 命令行选项

```
Options:
  --start-port INTEGER       起始端口（交互模式会提示）
  --end-port INTEGER         结束端口（交互模式会提示）
  --scan-dir PATH            扫描 docker-compose 文件的目录
  --count INTEGER            要查找的可用端口数量（默认: 5）
  --non-interactive          非交互模式，使用默认值
  --help                     显示帮助信息
```

## 工作原理

1. **扫描 Docker Compose 文件**
   - 递归扫描指定目录及其子目录
   - 查找 `docker-compose.yml` 和 `docker-compose.yaml` 文件
   - 解析文件中的端口映射和暴露端口

2. **排除已使用的端口**
   - 将 Docker Compose 中定义的端口标记为不可用
   - 在指定范围内搜索时跳过这些端口

3. **验证端口可用性**
   - 使用 `lsof -i:PORT` 命令检查端口是否被占用
   - 如果 lsof 不可用，尝试绑定端口进行验证
   - 显示占用端口的进程名称和 PID

4. **展示结果**
   - 清晰地展示所有找到的可用端口
   - 标记每个端口的状态（可用/已占用）
   - 提供第一个可用端口的快速参考

## 示例输出

```
============================================================
  Port Selector - Find Available Ports
============================================================

--- Configuration ---
ℹ Port range: 8000 - 9000
ℹ Scan directory: /home/user/myproject
ℹ Ports to find: 5

--- Step 1: Scanning docker-compose files ---
✓ Found 3 ports in docker-compose files
⚠ Excluded ports in range 8000-9000:
  - 8080
  - 8081
  - 8090

--- Step 2: Finding available ports ---
ℹ Checking port availability...

--- Step 3: Available Ports ---
✓ Found 5 available port(s):

  Port 8000: AVAILABLE ✓
  Port 8001: AVAILABLE ✓
  Port 8002: AVAILABLE ✓
  Port 8003: AVAILABLE ✓
  Port 8004: AVAILABLE ✓

--- Summary ---
✓ Total available ports: 5
ℹ First available port: 8000
```

## 依赖项

- Python >= 3.8
- PyYAML >= 6.0
- Click >= 8.0

可选依赖：
- `lsof` 命令（Linux/macOS，用于更准确的端口检测）

## 开发

```bash
# 克隆项目
git clone <repository-url>
cd port-selector

# 安装开发依赖
uv pip install -e .

# 运行测试（如果有）
pytest

# 格式化代码
black src/
```

## License

MIT License - 详见 LICENSE 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 常见问题

**Q: 为什么有些端口显示可用但实际无法使用？**

A: 某些端口可能被防火墙限制，或者需要特殊权限（如 1-1023 的特权端口）。

**Q: 工具找不到 docker-compose 文件？**

A: 确保文件名为 `docker-compose.yml` 或 `docker-compose.yaml`，并且你有读取权限。

**Q: lsof 命令不可用怎么办？**

A: 工具会自动降级到使用 socket 绑定方式检测端口，功能仍然可用。

**Q: 可以用于 Windows 吗？**

A: 端口检测功能可以在 Windows 上使用（通过 socket），但 lsof 命令仅适用于 Linux/macOS。
