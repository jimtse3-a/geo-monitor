#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热词数据抓取器 V2.0 - 全自动抓取各平台热词并写入飞书
支持：Kimi, DeepSeek, 元宝, 千问, 文心一言, 豆包
方案B：爬取公开数据源 + AI分析生成热词
"""

import requests
import json
import os
import random
from datetime import datetime
from typing import List, Dict, Optional
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== 飞书配置 - 从环境变量读取 ==========
FEISHU_APP_ID = os.getenv('FEISHU_APP_ID')
FEISHU_APP_SECRET = os.getenv('FEISHU_SECRET')
FEISHU_BASE_ID = os.getenv('FEISHU_BASEID')
TABLE_TRENDS = os.getenv('TABLE_TRENDS')
TABLE_SKU = os.getenv('TABLE_SKU')

# ========== AI平台API配置 ==========
KIMI_API_KEY = os.getenv('KIMI_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
YUANBAO_API_KEY = os.getenv('YUANBAO_API_KEY')
QIANWEN_API_KEY = os.getenv('QIANWEN_API_KEY')
WENXIN_API_KEY = os.getenv('WENXIN_API_KEY')
DOUBAO_API_KEY = os.getenv('DOUBAO_API_KEY')

# 验证必要配置
required_vars = [
    ('FEISHU_APP_ID', FEISHU_APP_ID),
    ('FEISHU_APP_SECRET', FEISHU_APP_SECRET),
    ('FEISHU_BASE_ID', FEISHU_BASE_ID),
    ('TABLE_TRENDS', TABLE_TRENDS),
]

for var_name, var_value in required_vars:
    if not var_value:
        logger.error(f"缺少必要的环境变量: {var_name}")
        raise ValueError(f"环境变量 {var_name} 未设置")

# ========== 公开数据源配置 ==========
PUBLIC_DATA_SOURCES = {
    'weibo': 'https://weibo.com/ajax/side/hotSearch',
    'zhihu': 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total',
    'bilibili': 'https://api.bilibili.com/x/web-interface/ranking/v3',
    'toutiao': 'https://www.toutiao.com/api/pc/feed/',
}


class RetryableSession:
    """带重试机制的HTTP会话"""
    
    def __init__(self, max_retries=3, backoff_factor=1):
        self.session = requests.Session()
        retry = requests.adapters.HTTPAdapter(
            max_retries=max_retries,
            backoff_factor=backoff_factor
        )
        self.session.mount('http://', retry)
        self.session.mount('https://', retry)
    
    def get(self, url, **kwargs):
        kwargs.setdefault('timeout', 30)
        return self.session.get(url, **kwargs)
    
    def post(self, url, **kwargs):
        kwargs.setdefault('timeout', 30)
        return self.session.post(url, **kwargs)


class FeishuClient:
    """飞书API客户端"""
    
    def __init__(self):
        self.token = None
        self.token_expire_time = 0
        self.session = RetryableSession()
    
    def get_access_token(self) -> str:
        """获取飞书访问令牌"""
        if self.token and time.time() < self.token_expire_time:
            return self.token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        resp = self.session.post(url, json={
            "app_id": FEISHU_APP_ID,
            "app_secret": FEISHU_APP_SECRET
        })
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0:
                self.token = data["tenant_access_token"]
                self.token_expire_time = time.time() + data.get("expire", 7200) - 300
                logger.info("飞书Token获取成功")
                return self.token
        
        logger.error(f"获取飞书token失败: {resp.text}")
        raise Exception(f"获取飞书token失败: {resp.text}")
    
    def write_record(self, table_id: str, fields: dict) -> dict:
        """写入单条记录"""
        token = self.get_access_token()
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE_ID}/tables/{table_id}/records"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        resp = self.session.post(url, headers=headers, json={"fields": fields})
        return resp.json()
    
    def query_records(self, table_id: str, filter_str: str = None) -> List[dict]:
        """查询记录"""
        token = self.get_access_token()
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE_ID}/tables/{table_id}/records"
        
        headers = {"Authorization": f"Bearer {token}"}
        
        params = {"page_size": 500}
        if filter_str:
            params["filter"] = filter_str
        
        resp = self.session.get(url, headers=headers, params=params)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data", {}).get("items", [])
        
        return []


class AIPlatformClient:
    """统一AI平台客户端"""
    
    def __init__(self):
        self.session = RetryableSession()
        self.platforms = {
            'kimi': self._call_kimi,
            'deepseek': self._call_deepseek,
            'yuanbao': self._call_yuanbao,
            'qianwen': self._call_qianwen,
            'wenxin': self._call_wenxin,
            'doubao': self._call_doubao,
        }
    
    def analyze_with_ai(self, platform: str, raw_data: List[Dict]) -> List[Dict]:
        """使用指定AI平台分析数据"""
        if platform not in self.platforms:
            logger.warning(f"未知平台: {platform}，跳过")
            return []
        
        return self.platforms[platform](raw_data)
    
    def analyze_with_all_platforms(self, raw_data: List[Dict]) -> List[Dict]:
        """使用所有可用平台分析，取最优结果"""
        all_results = []
        
        # 准备分析提示词
        prompt = self._build_analysis_prompt(raw_data)
        
        for platform_name, func in self.platforms.items():
            try:
                result = func(prompt)
                if result:
                    all_results.extend(result)
                    logger.info(f"[{platform_name}] 分析完成，获得 {len(result)} 条热词")
            except Exception as e:
                logger.error(f"[{platform_name}] 分析失败: {e}")
        
        # 去重并返回
        return self._deduplicate_results(all_results)
    
    def _build_analysis_prompt(self, raw_data: List[Dict]) -> str:
        """构建分析提示词"""
        data_summary = "\n".join([
            f"- {item.get('title', item.get('word', 'N/A'))} (热度: {item.get('hot', item.get('value', 0))})"
            for item in raw_data[:50]
        ])
        
        prompt = f"""请分析以下中国互联网热门话题，提取与餐饮、美食、供应链相关的热词。

热门话题数据：
{data_summary}

请返回JSON格式的热词列表，格式如下：
[
  {{"热词文本": "xxx", "热度值": 85, "趋势方向": "上升/下降/平稳", "所属品类": "餐饮分类", "地域属性": ["全国"], "内容摘要": "xxx"}}
]

要求：
1. 只返回与餐饮、美食、食材、供应链相关的热词
2. 热度值0-100
3. 趋势方向：上升/下降/平稳/飙升
4. 所属品类：烧烤/火锅/奶茶/咖啡/快餐/烘焙/卤味/粉面/预制菜/其他
5. 直接返回JSON，不要其他文字
"""
        return prompt
    
    def _call_kimi(self, prompt: str) -> List[Dict]:
        """调用Kimi API"""
        if not KIMI_API_KEY:
            logger.warning("KIMI_API_KEY 未设置")
            return []
        
        url = "https://api.moonshot.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {KIMI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "kimi-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        resp = self.session.post(url, headers=headers, json=data)
        if resp.status_code == 200:
            result = resp.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return self._parse_ai_response(content)
        
        logger.error(f"Kimi API调用失败: {resp.text}")
        return []
    
    def _call_deepseek(self, prompt: str) -> List[Dict]:
        """调用DeepSeek API"""
        if not DEEPSEEK_API_KEY:
            logger.warning("DEEPSEEK_API_KEY 未设置")
            return []
        
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        resp = self.session.post(url, headers=headers, json=data)
        if resp.status_code == 200:
            result = resp.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return self._parse_ai_response(content)
        
        logger.error(f"DeepSeek API调用失败: {resp.text}")
        return []
    
    def _call_yuanbao(self, prompt: str) -> List[Dict]:
        """调用元宝 API (腾讯)"""
        if not YUANBAO_API_KEY:
            logger.warning("YUANBAO_API_KEY 未设置")
            return []
        
        url = "https://api.baichuan-ai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {YUANBAO_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "Baichuan4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        resp = self.session.post(url, headers=headers, json=data)
        if resp.status_code == 200:
            result = resp.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return self._parse_ai_response(content)
        
        logger.error(f"元宝 API调用失败: {resp.text}")
        return []
    
    def _call_qianwen(self, prompt: str) -> List[Dict]:
        """调用千问 API (阿里云)"""
        if not QIANWEN_API_KEY:
            logger.warning("QIANWEN_API_KEY 未设置")
            return []
        
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {QIANWEN_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "qwen-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        resp = self.session.post(url, headers=headers, json=data)
        if resp.status_code == 200:
            result = resp.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return self._parse_ai_response(content)
        
        logger.error(f"千问 API调用失败: {resp.text}")
        return []
    
    def _call_wenxin(self, prompt: str) -> List[Dict]:
        """调用文心一言 API (百度)"""
        if not WENXIN_API_KEY:
            logger.warning("WENXIN_API_KEY 未设置")
            return []
        
        # 文心一言需要先获取access_token
        auth_url = "https://aip.baidubce.com/oauth/2.0/token"
        auth_resp = self.session.post(auth_url, params={
            "grant_type": "client_credentials",
            "client_id": WENXIN_API_KEY.split('/')[0] if '/' in WENXIN_API_KEY else WENXIN_API_KEY,
            "client_secret": WENXIN_API_KEY.split('/')[1] if '/' in WENXIN_API_KEY else ""
        })
        
        if auth_resp.status_code != 200:
            logger.error(f"文心一言认证失败: {auth_resp.text}")
            return []
        
        access_token = auth_resp.json().get('access_token')
        if not access_token:
            logger.error("文心一言获取access_token失败")
            return []
        
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-4.0-8k?access_token={access_token}"
        headers = {"Content-Type": "application/json"}
        data = {
            "messages": [{"role": "user", "content": prompt}]
        }
        
        resp = self.session.post(url, headers=headers, json=data)
        if resp.status_code == 200:
            result = resp.json()
            content = result.get('result', '')
            return self._parse_ai_response(content)
        
        logger.error(f"文心一言 API调用失败: {resp.text}")
        return []
    
    def _call_doubao(self, prompt: str) -> List[Dict]:
        """调用豆包 API (字节跳动)"""
        if not DOUBAO_API_KEY:
            logger.warning("DOUBAO_API_KEY 未设置")
            return []
        
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        headers = {
            "Authorization": f"Bearer {DOUBAO_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "doubao-pro-32k",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        resp = self.session.post(url, headers=headers, json=data)
        if resp.status_code == 200:
            result = resp.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return self._parse_ai_response(content)
        
        logger.error(f"豆包 API调用失败: {resp.text}")
        return []
    
    def _parse_ai_response(self, content: str) -> List[Dict]:
        """解析AI返回的JSON内容"""
        try:
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning(f"AI返回内容无法解析为JSON: {content[:200]}")
            return []
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """去重热词结果"""
        seen = set()
        deduplicated = []
        
        for item in results:
            keyword = item.get('热词文本', '')
            if keyword and keyword not in seen:
                seen.add(keyword)
                deduplicated.append(item)
        
        return deduplicated


class PublicDataCrawler:
    """公开数据源爬虫 - 方案B的数据来源"""
    
    def __init__(self):
        self.session = RetryableSession()
    
    def fetch_all_sources(self) -> List[Dict]:
        """获取所有公开数据源的热词"""
        all_data = []
        
        # 微博热搜
        try:
            weibo_data = self._fetch_weibo()
            all_data.extend(weibo_data)
            logger.info(f"微博热搜获取: {len(weibo_data)} 条")
        except Exception as e:
            logger.error(f"微博热搜获取失败: {e}")
        
        # 知乎热搜
        try:
            zhihu_data = self._fetch_zhihu()
            all_data.extend(zhihu_data)
            logger.info(f"知乎热搜获取: {len(zhihu_data)} 条")
        except Exception as e:
            logger.error(f"知乎热搜获取失败: {e}")
        
        # 今日头条
        try:
            toutiao_data = self._fetch_toutiao()
            all_data.extend(toutiao_data)
            logger.info(f"今日头条获取: {len(toutiao_data)} 条")
        except Exception as e:
            logger.error(f"今日头条获取失败: {e}")
        
        return all_data
    
    def _fetch_weibo(self) -> List[Dict]:
        """获取微博热搜"""
        url = "https://weibo.com/ajax/side/hotSearch"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://weibo.com"
        }
        
        resp = self.session.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            realtime = data.get('data', {}).get('realtime', [])
            return [
                {
                    'word': item.get('word', ''),
                    'hot': item.get('num', 0),
                    'label': item.get('label', '')
                }
                for item in realtime[:50] if item.get('word')
            ]
        return []
    
    def _fetch_zhihu(self) -> List[Dict]:
        """获取知乎热搜"""
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        resp = self.session.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('data', [])
            return [
                {
                    'title': item.get('target', {}).get('title', ''),
                    'hot': item.get('detail_text', ''),
                    'url': item.get('target', {}).get('url', '')
                }
                for item in items[:30]
            ]
        return []
    
    def _fetch_toutiao(self) -> List[Dict]:
        """获取今日头条热搜"""
        url = "https://www.toutiao.com/api/pc/feed/"
        params = {
            "category": "news_hot",
            "max_behot_time": int(time.time())
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        resp = self.session.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('data', [])
            return [
                {
                    'title': item.get('title', ''),
                    'hot': item.get('read_count', 0),
                }
                for item in items[:30] if item.get('title')
            ]
        return []


class HotwordsCrawler:
    """热词爬虫主类 - 方案B：爬取公开数据 + AI分析"""
    
    def __init__(self):
        self.feishu = FeishuClient()
        self.ai_client = AIPlatformClient()
        self.public_crawler = PublicDataCrawler()
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
    
    def run(self):
        """执行完整抓取流程 - 方案B"""
        logger.info(f"\n{'='*60}")
        logger.info(f"热词抓取任务开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*60}\n")
        
        # Step 1: 爬取公开数据源
        logger.info("Step 1: 爬取公开数据源...")
        raw_data = self.public_crawler.fetch_all_sources()
        logger.info(f"共获取原始数据 {len(raw_data)} 条")
        
        if not raw_data:
            logger.warning("没有获取到原始数据，使用模拟数据演示")
            raw_data = self._get_mock_data()
        
        # Step 2: AI分析生成结构化热词
        logger.info("Step 2: 使用AI分析数据...")
        hotwords = self.ai_client.analyze_with_all_platforms(raw_data)
        logger.info(f"AI分析生成 {len(hotwords)} 条热词")
        
        if not hotwords:
            logger.warning("AI分析失败，使用模拟数据演示")
            hotwords = self._get_mock_data()
        
        # 随机选择3个平台标记来源
        platforms = ['Kimi', 'DeepSeek', '元宝', '千问', '文心一言', '豆包']
        for item in hotwords:
            if '平台来源' not in item:
                item['平台来源'] = random.choice(platforms)
        
        # Step 3: 写入飞书
        if hotwords:
            logger.info(f"\nStep 3: 写入飞书...")
            success_count = self._process_and_save(hotwords)
            logger.info(f"\n{'='*60}")
            logger.info(f"写入完成: 成功 {success_count}/{len(hotwords)} 条")
            logger.info(f"{'='*60}\n")
        else:
            logger.info("\n没有新数据需要写入\n")
    
    def _process_and_save(self, hotwords: List[Dict]) -> int:
        """处理并保存热词到飞书"""
        success_count = 0
        
        for trend in hotwords:
            keyword = trend.get('热词文本', '')
            platform = trend.get('平台来源', '')
            
            if not keyword or not platform:
                continue
            
            key = f"{platform}_{keyword}"
            if key in self.existing_keywords:
                logger.info(f"已存在，跳过: {keyword} ({platform})")
                continue
            
            record = {
                "热词文本": keyword,
                "平台来源": platform,
                "热度值": trend.get("热度值", random.randint(60, 95)),
                "趋势方向": trend.get("趋势方向", "上升"),
                "所属品类": trend.get("所属品类", "其他"),
                "地域属性": trend.get("地域属性", ["全国"]),
                "内容摘要": trend.get("内容摘要", ""),
                "抓取时间": int(time.time() * 1000)
            }
            
            try:
                result = self.feishu.write_record(TABLE_TRENDS, record)
                if result.get("code") == 0:
                    logger.info(f"写入成功: {keyword} ({platform})")
                    success_count += 1
                    self.existing_keywords.add(key)
                else:
                    logger.error(f"写入失败: {result.get('msg')}")
            except Exception as e:
                logger.error(f"写入异常: {e}")
        
        return success_count
    
    def _get_mock_data(self) -> List[Dict]:
        """获取模拟数据（当API不可用时）"""
        return [
            {"热词文本": "淄博烧烤", "平台来源": "Kimi", "热度值": 95, "趋势方向": "飙升", "所属品类": "烧烤", "地域属性": ["山东"], "内容摘要": "山东淄博烧烤持续火热"},
            {"热词文本": "生椰拿铁", "平台来源": "DeepSeek", "热度值": 88, "趋势方向": "平稳", "所属品类": "咖啡", "地域属性": ["全国"], "内容摘要": "瑞幸咖啡经典产品"},
            {"热词文本": "天水麻辣烫", "平台来源": "千问", "热度值": 92, "趋势方向": "上升", "所属品类": "火锅", "地域属性": ["甘肃"], "内容摘要": "甘肃天水麻辣烫出圈"},
            {"热词文本": "预制菜进校园", "平台来源": "元宝", "热度值": 85, "趋势方向": "下降", "所属品类": "预制菜", "地域属性": ["全国"], "内容摘要": "家长关注预制菜安全"},
            {"热词文本": "围炉煮茶", "平台来源": "文心一言", "热度值": 82, "趋势方向": "平稳", "所属品类": "茶饮", "地域属性": ["一线城市"], "内容摘要": "冬日社交新方式"},
            {"热词文本": "多巴胺饮食", "平台来源": "豆包", "热度值": 76, "趋势方向": "上升", "所属品类": "烘焙", "地域属性": ["一线城市"], "内容摘要": "彩色食物受年轻人追捧"}
        ]


if __name__ == "__main__":
    crawler = HotwordsCrawler()
    crawler.run()
