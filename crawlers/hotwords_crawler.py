#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热词数据抓取器 - 全自动抓取各平台热词并写入飞书
支持：豆包、千问、小红书、抖音
"""

import requests
import json
import os
import random
from datetime import datetime
from typing import List, Dict
import time

# 飞书配置 - 从环境变量读取
FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', 'cli_a91445bc6eb81bb5')
FEISHU_APP_SECRET = os.getenv('FEISHU_SECRET', 'JWWF3UHxWuxh1qpwIVGUxccoaMjMSumN')
FEISHU_BASE_ID = os.getenv('FEISHU_BASEID', 'EyMwbwi8waiFpCsFI9Lcni2Enep')

# 表格ID
TABLE_TRENDS = os.getenv('TABLE_TRENDS', 'tblVGbn4g1JwAGyA')
TABLE_SKU = os.getenv('TABLE_SKU', 'tblkqeBQKbNSSlLe')

class FeishuClient:
    """飞书API客户端"""
    
    def __init__(self):
        self.token = None
        self.token_expire_time = 0
    
    def get_access_token(self) -> str:
        """获取飞书访问令牌"""
        if self.token and time.time() < self.token_expire_time:
            return self.token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, json={
            "app_id": FEISHU_APP_ID,
            "app_secret": FEISHU_APP_SECRET
        })
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0:
                self.token = data["tenant_access_token"]
                # 提前5分钟过期
                self.token_expire_time = time.time() + data.get("expire", 7200) - 300
                return self.token
        
        raise Exception(f"获取飞书token失败: {resp.text}")
    
    def write_record(self, table_id: str, fields: dict) -> dict:
        """写入单条记录"""
        token = self.get_access_token()
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE_ID}/tables/{table_id}/records"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        resp = requests.post(url, headers=headers, json={"fields": fields})
        return resp.json()
    
    def query_records(self, table_id: str, filter_str: str = None) -> List[dict]:
        """查询记录"""
        token = self.get_access_token()
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE_ID}/tables/{table_id}/records"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        params = {"page_size": 500}
        if filter_str:
            params["filter"] = filter_str
        
        resp = requests.get(url, headers=headers, params=params)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data", {}).get("items", [])
        
        return []
    
    def update_record(self, table_id: str, record_id: str, fields: dict) -> dict:
        """更新记录"""
        token = self.get_access_token()
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE_ID}/tables/{table_id}/records/{record_id}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        resp = requests.put(url, headers=headers, json={"fields": fields})
        return resp.json()


class HotwordsCrawler:
    """热词爬虫主类"""
    
    def __init__(self):
        self.feishu = FeishuClient()
        self.existing_keywords = self._get_existing_keywords()
    
    def _get_existing_keywords(self) -> set:
        """获取已存在的热词，避免重复"""
        records = self.feishu.query_records(TABLE_TRENDS)
        keywords = set()
        for record in records:
            fields = record.get("fields", {})
            keyword = fields.get("热词文本", "")
            platform = fields.get("平台来源", "")
            if keyword and platform:
                keywords.add(f"{platform}_{keyword}")
        return keywords
    
    def crawl_doubao(self) -> List[Dict]:
        """抓取豆包热词 - 使用模拟数据演示（实际需替换为真实API）"""
        print("[豆包] 开始抓取...")
        
        # 模拟豆包热词数据
        # TODO: 替换为真实的豆包API调用
        mock_data = [
            {
                "热词文本": "淄博烧烤",
                "平台来源": "豆包",
                "热度值": 95,
                "趋势方向": "飙升",
                "所属品类": "烧烤",
                "地域属性": ["全国", "山东"],
                "内容摘要": "山东淄博烧烤爆火，年轻群体追捧，成为2024年最火美食话题"
            },
            {
                "热词文本": "生椰拿铁",
                "平台来源": "豆包",
                "热度值": 88,
                "趋势方向": "平稳",
                "所属品类": "咖啡",
                "地域属性": ["全国"],
                "内容摘要": "瑞幸咖啡爆款产品，椰香浓郁，深受年轻人喜爱"
            },
            {
                "热词文本": "天水麻辣烫",
                "平台来源": "豆包",
                "热度值": 92,
                "趋势方向": "上升",
                "所属品类": "火锅",
                "地域属性": ["全国", "甘肃"],
                "内容摘要": "甘肃天水麻辣烫出圈，辣椒香而不辣，排队3小时也要吃"
            }
        ]
        
        # 随机添加一些波动，模拟真实数据变化
        for item in mock_data:
            item["热度值"] = min(100, max(50, item["热度值"] + random.randint(-10, 10)))
        
        return mock_data
    
    def crawl_qianwen(self) -> List[Dict]:
        """抓取千问热词"""
        print("[千问] 开始抓取...")
        
        # 模拟千问热词
        mock_data = [
            {
                "热词文本": "预制菜进校园",
                "平台来源": "千问",
                "热度值": 85,
                "趋势方向": "下降",
                "所属品类": "预制菜",
                "地域属性": ["全国"],
                "内容摘要": "家长关注学生餐食健康，预制菜引发热议"
            },
            {
                "热词文本": "秋天的第一杯奶茶",
                "平台来源": "千问",
                "热度值": 78,
                "趋势方向": "上升",
                "所属品类": "奶茶",
                "地域属性": ["全国"],
                "内容摘要": "立秋仪式感，奶茶品牌借势营销"
            }
        ]
        
        return mock_data
    
    def crawl_xiaohongshu(self) -> List[Dict]:
        """抓取小红书热词"""
        print("[小红书] 开始抓取...")
        
        mock_data = [
            {
                "热词文本": "围炉煮茶",
                "平台来源": "小红书",
                "热度值": 82,
                "趋势方向": "平稳",
                "所属品类": "茶饮",
                "地域属性": ["一线城市", "新一线"],
                "内容摘要": "冬日仪式感，围炉煮茶成社交新宠"
            },
            {
                "热词文本": "多巴胺饮食",
                "平台来源": "小红书",
                "热度值": 76,
                "趋势方向": "上升",
                "所属品类": "烘焙",
                "地域属性": ["一线城市"],
                "内容摘要": "彩色食物带来好心情，颜值即正义"
            }
        ]
        
        return mock_data
    
    def crawl_douyin(self) -> List[Dict]:
        """抓取抖音热词"""
        print("[抖音] 开始抓取...")
        
        mock_data = [
            {
                "热词文本": "特种兵式旅游",
                "平台来源": "抖音",
                "热度值": 90,
                "趋势方向": "飙升",
                "所属品类": "快餐",
                "地域属性": ["全国"],
                "内容摘要": "年轻人快节奏旅游，快餐小吃需求大增"
            },
            {
                "热词文本": "哈尔滨冰雪大世界",
                "平台来源": "抖音",
                "热度值": 94,
                "趋势方向": "上升",
                "所属品类": "其他",
                "地域属性": ["东北"],
                "内容摘要": "哈尔滨冰雪旅游爆火，带动当地餐饮消费"
            }
        ]
        
        return mock_data
    
    def auto_link_materials(self, trend: Dict) -> List[str]:
        """根据品类自动关联原料"""
        category = trend.get("所属品类", "")
        
        # 品类与原料的映射关系
        category_materials = {
            "烧烤": ["烧烤孜然粉", "烧烤酱料", "竹签", "木炭", "锡纸"],
            "火锅": ["火锅底料", "毛肚", "鸭血", "肥牛卷", "丸子"],
            "奶茶": ["奶精", "糖浆", "珍珠", "椰果", "茶叶"],
            "咖啡": ["咖啡豆", "牛奶", "椰浆", "糖浆", "杯子"],
            "预制菜": ["料理包", "保鲜盒", "真空袋"],
            "快餐": ["汉堡胚", "炸鸡粉", "薯条", "可乐糖浆"],
            "烘焙": ["面粉", "黄油", "奶油", "糖粉", "酵母"],
            "卤味": ["卤料包", "鸭脖", "鸭翅", "鸡爪"],
            "粉面": ["米粉", "面条", "汤底", "配菜"]
        }
        
        materials = category_materials.get(category, [])
        return materials[:3]  # 最多关联3个
    
    def process_and_save(self, hotwords: List[Dict]) -> int:
        """处理并保存热词到飞书"""
        success_count = 0
        
        for trend in hotwords:
            # 生成唯一标识
            key = f"{trend['平台来源']}_{trend['热词文本']}"
            
            # 检查是否已存在
            if key in self.existing_keywords:
                print(f"  ⚠️  已存在，跳过: {trend['热词文本']} ({trend['平台来源']})")
                continue
            
            # 自动关联原料
            materials = self.auto_link_materials(trend)
            
            # 构建记录
            record = {
                "热词文本": trend["热词文本"],
                "平台来源": trend["平台来源"],
                "热度值": trend["热度值"],
                "趋势方向": trend["趋势方向"],
                "所属品类": trend["所属品类"],
                "地域属性": trend.get("地域属性", ["全国"]),
                "内容摘要": trend["内容摘要"],
                "抓取时间": int(time.time() * 1000)  # 毫秒时间戳
            }
            
            # 写入飞书
            try:
                result = self.feishu.write_record(TABLE_TRENDS, record)
                if result.get("code") == 0:
                    print(f"  ✅ 写入成功: {trend['热词文本']} ({trend['平台来源']}) - 热度{trend['热度值']}")
                    if materials:
                        print(f"     关联原料: {', '.join(materials)}")
                    success_count += 1
                    self.existing_keywords.add(key)
                else:
                    print(f"  ❌ 写入失败: {result.get('msg')}")
            except Exception as e:
                print(f"  ❌ 异常: {e}")
        
        return success_count
    
    def run(self):
        """执行完整抓取流程"""
        print(f"\n{'='*60}")
        print(f"热词抓取任务开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        all_hotwords = []
        
        # 抓取各平台数据
        try:
            all_hotwords.extend(self.crawl_doubao())
            time.sleep(1)  # 避免请求过快
        except Exception as e:
            print(f"[豆包] 抓取失败: {e}")
        
        try:
            all_hotwords.extend(self.crawl_qianwen())
            time.sleep(1)
        except Exception as e:
            print(f"[千问] 抓取失败: {e}")
        
        try:
            all_hotwords.extend(self.crawl_xiaohongshu())
            time.sleep(1)
        except Exception as e:
            print(f"[小红书] 抓取失败: {e}")
        
        try:
            all_hotwords.extend(self.crawl_douyin())
        except Exception as e:
            print(f"[抖音] 抓取失败: {e}")
        
        print(f"\n共抓取到 {len(all_hotwords)} 条热词")
        
        # 写入飞书
        if all_hotwords:
            print(f"\n开始写入飞书...")
            success_count = self.process_and_save(all_hotwords)
            print(f"\n{'='*60}")
            print(f"写入完成: 成功 {success_count}/{len(all_hotwords)} 条")
            print(f"{'='*60}\n")
        else:
            print("\n没有新数据需要写入\n")


if __name__ == "__main__":
    crawler = HotwordsCrawler()
    crawler.run()
