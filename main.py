import asyncio
import aiohttp
from datetime import datetime
import logging
import json
import os

# 导入配置
from config import (
    BASE_URL,
    WEBHOOK_URL,
    PROXY_URL,
    USE_PROXY,
    INTERVAL,
    APP_NAME,
    WALLET_ADDRESSES,
    TASK_IDS
)

# 配置logging
def setup_logging():
    """配置日志格式和级别"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# 添加缓存文件路径
CACHE_FILE = "rank_cache.json"

def load_rank_cache():
    """加载排名缓存"""
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载缓存失败: {str(e)}")
        return {}

def save_rank_cache(cache_data):
    """保存排名缓存"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        logger.error(f"保存缓存失败: {str(e)}")

async def fetch_data_from_url(session, url):
    """获取API数据"""
    try:
        async with session.get(url, ssl=False) as response:
            logger.info(f"请求URL: {url}, 状态: {response.status}")
            if response.status == 200:
                data = await response.json()
                return data
            else:
                logger.error(f"获取数据失败: {response.status}")
                return None
    except Exception as e:
        logger.error(f"请求出错: {str(e)}")
        return None

async def check_wallet_addresses(data, task_id=None):
    """检查钱包地址
    
    Args:
        data: API返回的数据
        task_id: 任务ID,用于日志输出
        
    Returns:
        list: 匹配的对象列表
    """
    """检查钱包地址并比较排名变化"""
    found_objects = []
    rank_changes = []
    task_info = f"Task {task_id} - " if task_id else ""
    
    # 加载上次的排名缓存
    rank_cache = load_rank_cache()
    
    # 使用新函数处理钱包地址
    wallet_set = WALLET_ADDRESSES
    logger.info(f"处理后的钱包地址集合: {wallet_set}")

    if not data:
        logger.warning(f"{task_info}收到空数据")
        return found_objects, rank_changes
        
    if 'items' not in data:
        logger.warning(f"{task_info}数据中没有items字段")
        return found_objects, rank_changes
        
    total_items = len(data['items'])
    logger.info(f"{task_info}开始检查钱包地址,共 {total_items} 条数据")
    
    for item in data['items']:
        wallet_address = item.get('wallet', '').lower()
        if not wallet_address:
            continue
            
        if wallet_address in wallet_set:
            rank = item.get('rank', 'unknown')
            score = item.get('submission_phase_score', 'unknown')
            
            # 检查排名变化
            if wallet_address in rank_cache:
                old_rank = rank_cache[wallet_address].get('rank')
                old_score = rank_cache[wallet_address].get('score')
                
                if old_rank != rank or old_score != score:
                    rank_changes.append({
                        'wallet': wallet_address,
                        'old_rank': old_rank,
                        'new_rank': rank,
                        'old_score': old_score,
                        'new_score': score
                    })
            
            # 更新缓存
            rank_cache[wallet_address] = {
                'rank': rank,
                'score': score
            }
            
            found_objects.append(item)
    
    # 保存更新后的缓存
    save_rank_cache(rank_cache)
    
    match_count = len(found_objects)
    
    # 按score排序输出匹配结果统计
    if found_objects:
        found_objects.sort(key=lambda x: x.get('submission_phase_score', float('inf')))
        logger.info(f"{task_info}匹配结果统计:")
        for item in found_objects:
            rank = item.get('rank', 'unknown')
            score = item.get('submission_phase_score', 'unknown')
            logger.info(f"  - Rank {rank}: {item['wallet']} (得分: {score:.4f})")
    
    logger.info(f"{task_info}钱包地址检查完成: 共检查 {total_items} 个地址, 找到 {match_count} 个匹配项")

    return found_objects, rank_changes

def build_model_message(task_id, found_objects, rank_changes):
    """构建包含排名变化的Model消息"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message_lines = [
        f"🔍 【{APP_NAME} - Model Task {task_id}】",
        f"⏰ 时间: {timestamp}\n",
        "📊 发现的钱包地址:\n"
    ]
    
    for obj in found_objects:
        wallet = obj.get('wallet', '未知地址')
        score = obj.get('submission_phase_score', '无')
        rank = obj.get('rank', '无')
        finalized_at = obj.get('finalized_at', '无')
        
        # 根据排名添加不同的标记
        rank_indicator = ""
        if isinstance(rank, (int, float)):
            rank_indicator = "⚠️ " if rank > 20 else "✅ "
        
        message_lines.extend([
            f"👛 钱包地址: {wallet}",
            f"💯 分数: {score}",
            f"🏆 排名: {rank_indicator}{rank}",
            f"🕒 完成时间: {finalized_at}\n",
        ])
    
    if rank_changes:
        message_lines.append("\n📈 排名变化:")
        for change in rank_changes:
            # 根据新排名添加不同的标记
            new_rank_indicator = ""
            if isinstance(change['new_rank'], (int, float)):
                new_rank_indicator = "⚠️ " if change['new_rank'] > 20 else "✅ "
            
            message_lines.extend([
                f"👛 钱包地址: {change['wallet']}",
                f"🔄 排名: {change['old_rank']} -> {new_rank_indicator}{change['new_rank']}",
                f"📊 分数: {change['old_score']} -> {change['new_score']}\n"
            ])
    
    return "\n".join(message_lines)

def build_validator_message(task_id, found_objects):
    """构建Validator消息"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message_lines = [
        f"🔍 【{APP_NAME} - Validator Task {task_id}】",
        f"⏰ 时间: {timestamp}\n",
        "📊 发现的钱包地址:\n"
    ]
    
    for obj in found_objects:
        wallet = obj.get('wallet', '未知地址')
        score = obj.get('score', '无')
        hardworking_score = obj.get('hardworking_score', '无')
        rank = obj.get('rank', '无')
        updated_at = obj.get('updated_at', '无')
        
        message_lines.extend([
            f"👛 钱包地址: {wallet}",
            f"💯 总分: {score}",
            f"📈 勤奋度: {hardworking_score}",
            f"🏆 排名: {rank}",
            f"🕒 更新时间: {updated_at}\n"
        ])
    
    return "\n".join(message_lines)

async def send_message_async(webhook_url, message_content, use_proxy, proxy_url):
    """发送消息到webhook"""
    headers = {'Content-Type': 'application/json'}
    payload = {
        "msgtype": "text",
        "text": {
            "content": message_content
        }
    }
    
    proxy = proxy_url if use_proxy else None
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(webhook_url, json=payload, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    logger.info("消息发送成功!")
                else:
                    logger.error(f"发送消息失败: {response.status}")
        except Exception as e:
            logger.error(f"发送消息出错: {str(e)}")

async def monitor_stations(interval, webhook_url, use_proxy, proxy_url):
    """主监控函数"""
    iteration = 1
    
    while True:
        try:
            logger.info(f"\n开始第 {iteration} 轮检查...")
            
            async with aiohttp.ClientSession() as session:
                for task_id in TASK_IDS:
                    # 检查 models
                    model_url = f"{BASE_URL}/models?task_id={task_id}&page=1&size=50"
                    model_data = await fetch_data_from_url(session, model_url)
                    if model_data:
                        found_model_objects, rank_changes = await check_wallet_addresses(model_data, task_id)
                        logger.info(f"Found model objects: {found_model_objects}")
                        logger.info(f"Rank changes: {rank_changes}")
                        if found_model_objects or rank_changes:  # 确保有数据需要发送
                            message = build_model_message(task_id, found_model_objects, rank_changes)
                            await send_message_async(webhook_url, message, use_proxy, proxy_url)
                    
                    # 检查 validators
                    # validator_url = f"{BASE_URL}/validators?task_id={task_id}&page=1&size=50"
                    # validator_data = await fetch_data_from_url(session, validator_url)
                    # if validator_data:
                    #     found_validator_objects = await check_wallet_addresses(validator_data)
                    #     if found_validator_objects:
                    #         message = build_validator_message(task_id, found_validator_objects)
                    #         await send_message_async(webhook_url, message, use_proxy, proxy_url)
                    
                    # await asyncio.sleep(5)  # 请求间隔
            
            logger.info(f"第 {iteration} 轮检查完成\n")
            iteration += 1
            
        except Exception as e:
            logger.error(f"监控过程出错: {str(e)}")
            await asyncio.sleep(5)
            continue
            
        await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(monitor_stations(
        interval=INTERVAL,
        webhook_url=WEBHOOK_URL,
        use_proxy=USE_PROXY,
        proxy_url=PROXY_URL
    ))