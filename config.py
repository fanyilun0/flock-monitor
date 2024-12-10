import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# API配置
BASE_URL = "https://fed-ledger-prod.flock.io/api/v1/stats"

# 钱包地址配置
WALLET_ADDRESSES = set(
    os.getenv('WALLET_ADDRESSES').split(',')
)

# Task ID配置
TASK_IDS = [17]  # 可以包含多个 task_id

# Webhook配置 
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# 应用名称
APP_NAME = 'Flock Monitor'

# 代理配置
PROXY_URL = 'http://localhost:7890'
USE_PROXY = False
ALWAYS_NOTIFY = True

# 时间配置
INTERVAL = 1800  # 10分钟检查一次
TIME_OFFSET = 6


