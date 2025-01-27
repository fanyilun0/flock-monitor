# Flock-Monitor

一个用于监控 Flock 节点状态的自动化工具。

## 功能特点

- 🔄 自动监控多个钱包地址的排名和分数
- 📊 追踪排名变化并显示增量
- 📱 企业微信机器人通知
- 🌐 支持代理配置
- ⏰ 可配置检查间隔
- 🐳 支持 Docker 部署

## 安装

### 方法一: 本地部署

1. 克隆仓库:
    ```bash
    git clone https://github.com/yourusername/flock-monitor.git
    cd flock-monitor
    ```

2. 安装依赖:
    ```bash
    pip install -r requirements.txt
    ```

3. 创建并配置 `.env` 文件:
    ```
    # 企业微信机器人配置
    WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=
    WALLET_ADDRESSES=0x123...,0x456...
    ```

4. 编辑 `config.py` 文件，根据需要修改以下参数:
    - `PROXY_URL`: 代理服务器地址（可选）
    - `USE_PROXY`: 是否启用代理
    - `INTERVAL`: 检查间隔时间（秒）
    - `TIME_OFFSET`: 时区偏移（小时）
    - `ALWAYS_NOTIFY`: 是否始终发送通知
    - `SHOW_DETAIL`: 是否显示详细日志

### 方法二: Docker 部署

1. 创建并配置 `.env` 文件（同上）

2. 使用 Docker Compose 启动:
    ```bash
    docker-compose up -d
    ```

Docker 环境变量说明:
- `TZ`: 时区设置，默认为 Asia/Shanghai
- `PYTHONUNBUFFERED`: Python 输出不缓冲
- `IS_DOCKER`: Docker 环境标识
- `HTTP_PROXY/HTTPS_PROXY`: 代理服务器配置

## 使用方法

### 本地运行:
```bash
python main.py
```

### Docker 运行:
```bash
# 查看日志
docker logs -f flock-monitor

# 重启服务
docker-compose restart

# 停止服务
docker-compose down
```

## 通知示例

监控程序会通过企业微信机器人发送如下格式的通知:
```
🔍 【Flock Monitor - Model Task 17】
⏰ 时间: 2024-03-21 10:00:00
📊 发现的钱包地址:
👛 钱包地址: 0x123...
💯 分数: -1.173
🏆 排名: ✅ 20
🕒 完成时间: 2024-03-21T10:00:00Z
📈 排名变化:
👛 钱包地址: 0x123...
🔄 排名: 21 -> ✅ 20
📊 分数: -1.175 -> -1.173
```


## 配置说明

### 环境变量 (.env)

- `WALLET_ADDRESSES`: 钱包地址列表，多个地址用英文逗号分隔
- `WEBHOOK_URL`: 企业微信机器人的 webhook 地址

### 应用配置 (config.py)

- `PROXY_URL`: 代理服务器地址，默认为 http://localhost:7890
- `USE_PROXY`: 是否启用代理，默认为 False
- `INTERVAL`: 检查间隔时间（秒），默认为 10800（3小时）
- `TIME_OFFSET`: 时区偏移（小时），默认为 0
- `ALWAYS_NOTIFY`: 是否始终发送通知，默认为 True
- `SHOW_DETAIL`: 是否显示详细日志，默认为 True

## 注意事项

- 请妥善保管你的 token，不要泄露给他人
- 建议使用代理以提高连接稳定性
- 可以根据需要调整检查间隔时间
- 如遇到问题，请查看程序输出的日志信息
- Docker 部署时注意配置正确的时区和代理设置

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持多账号监控
- 添加 Docker 部署支持
- 企业微信机器人通知集成