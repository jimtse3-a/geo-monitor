#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GEO AI 搜索引擎监测工具 - 演示版
支持多平台、多品牌、多关键词监测

使用方法:
    python monitor.py                    # 运行完整监测
    python monitor.py --platforms kimi   # 只监测 Kimi
    python monitor.py --brands "星巴克"   # 监测指定品牌
    python monitor.py --demo             # 生成演示数据
"""

import os
import json
import sqlite3
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

# 模拟 API 调用（实际使用时替换为真实 API）
class MockAIClient:
    """模拟 AI 平台 API 响应"""
    
    PLATFORM_PERSONALITY = {
        "kimi": {
            "style": "理性分析",
            "mentions": ["星巴克", "瑞幸咖啡", "印暨咖啡"],
            "weights": [0.8, 0.6, 0.4]  # 品牌提及概率
        },
        "doubao": {
            "style": "亲和推荐",
            "mentions": ["喜茶", "奈雪的茶", "瑞幸咖啡"],
            "weights": [0.7, 0.5, 0.6]
        },
        "qianwen": {
            "style": "专业详细",
            "mentions": ["星巴克", "印暨咖啡", "瑞幸咖啡"],
            "weights": [0.75, 0.65, 0.55]
        },
        "deepseek": {
            "style": "深度思考",
            "mentions": ["印暨咖啡", "星巴克", "喜茶"],
            "weights": [0.9, 0.7, 0.5]
        },
        "wenxin": {
            "style": "传统稳重",
            "mentions": ["星巴克", "瑞幸咖啡", "奈雪的茶"],
            "weights": [0.85, 0.65, 0.45]
        },
        "hunyuan": {
            "style": "社交导向",
            "mentions": ["喜茶", "奈雪的茶", "瑞幸咖啡"],
            "weights": [0.8, 0.75, 0.5]
        },
        "zhipu": {
            "style": "技术驱动",
            "mentions": ["印暨咖啡", "星巴克", "瑞幸咖啡"],
            "weights": [0.7, 0.8, 0.6]
        }
    }
    
    @classmethod
    def query(cls, platform, keyword, brand):
        """模拟查询 AI 平台"""
        personality = cls.PLATFORM_PERSONALITY.get(platform, cls.PLATFORM_PERSONALITY["deepseek"])
        
        # 根据品牌权重决定是否提及
        if brand in personality["mentions"]:
            idx = personality["mentions"].index(brand)
            weight = personality["weights"][min(idx, len(personality["weights"])-1)]
        else:
            weight = 0.3  # 默认提及概率
        
        # 关键词匹配增加概率
        if brand in keyword or any(kw in keyword for kw in ["咖啡", "奶茶", "饮品"]):
            weight += 0.2
        
        is_mentioned = random.random() < weight
        
        if is_mentioned:
            rank = random.randint(1, 3)
            confidence = random.randint(70, 95)
            
            # 生成模拟回复
            responses = [
                f"{brand}在{keyword}方面表现出色，是很多消费者的首选。",
                f"如果你关注{keyword}，{brand}值得考虑，品质有保障。",
                f"{brand}在{keyword}领域有不错的口碑，用户满意度较高。",
            ]
            response = random.choice(responses)
        else:
            rank = 0
            confidence = random.randint(20, 50)
            other_brands = [b for b in personality["mentions"] if b != brand]
            response = f"在{keyword}方面，{random.choice(other_brands)}等品牌表现较好。"
        
        return {
            "platform": platform,
            "keyword": keyword,
            "brand": brand,
            "is_mentioned": is_mentioned,
            "rank": rank,
            "confidence": confidence,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }


# 数据库管理
class DatabaseManager:
    def __init__(self, db_file="monitor.db"):
        self.db_file = db_file
        self.init_db()
    
    def init_db(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # 监测记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitor_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                platform TEXT NOT NULL,
                keyword TEXT NOT NULL,
                is_mentioned INTEGER DEFAULT 0,
                rank INTEGER DEFAULT 0,
                confidence INTEGER DEFAULT 0,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 品牌配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brand_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                aliases TEXT,
                industry TEXT,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 每日统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                brand TEXT NOT NULL,
                platform TEXT NOT NULL,
                total_queries INTEGER DEFAULT 0,
                mentioned_count INTEGER DEFAULT 0,
                visibility_rate REAL DEFAULT 0,
                avg_rank REAL DEFAULT 0,
                avg_confidence REAL DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_record(self, record):
        """保存监测记录"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO monitor_records 
            (brand, platform, keyword, is_mentioned, rank, confidence, response)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            record["brand"],
            record["platform"],
            record["keyword"],
            1 if record["is_mentioned"] else 0,
            record["rank"],
            record["confidence"],
            record["response"]
        ))
        
        conn.commit()
        conn.close()
    
    def get_stats(self, brand=None, platform=None, days=7):
        """获取统计数据"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = """
            SELECT 
                brand,
                platform,
                COUNT(*) as total,
                SUM(is_mentioned) as mentioned,
                AVG(CASE WHEN is_mentioned=1 THEN rank END) as avg_rank,
                AVG(confidence) as avg_confidence
            FROM monitor_records
            WHERE created_at >= datetime('now', '-{} days')
        """.format(days)
        
        params = []
        if brand:
            query += " AND brand = ?"
            params.append(brand)
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        query += " GROUP BY brand, platform"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "brand": row[0],
                "platform": row[1],
                "total": row[2],
                "mentioned": row[3],
                "visibility_rate": (row[3] / row[2] * 100) if row[2] > 0 else 0,
                "avg_rank": row[4] or 0,
                "avg_confidence": row[5] or 0
            }
            for row in results
        ]
    
    def get_recent_records(self, limit=50):
        """获取最近的监测记录"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM monitor_records
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        columns = [description[0] for description in cursor.description]
        records = cursor.fetchall()
        conn.close()
        
        return [dict(zip(columns, row)) for row in records]


# GEO 监测器主类
class GEOMonitor:
    PLATFORMS = {
        "kimi": "Kimi",
        "doubao": "豆包",
        "qianwen": "千问",
        "deepseek": "DeepSeek",
        "wenxin": "文心一言",
        "hunyuan": "腾讯混元",
        "zhipu": "智谱"
    }
    
    DEFAULT_BRANDS = [
        {
            "name": "印暨咖啡",
            "aliases": ["印暨", "ing咖啡"],
            "industry": "咖啡",
            "keywords": [
                "咖啡推荐", "广州咖啡", "下午茶",
                "适合办公的咖啡馆", "约会咖啡店",
                "印暨咖啡怎么样", "广州印暨咖啡",
                "印暨咖啡和星巴克哪个好"
            ]
        },
        {
            "name": "瑞幸咖啡",
            "aliases": ["瑞幸", "luckin"],
            "industry": "咖啡",
            "keywords": [
                "平价咖啡", "外卖咖啡", "办公室咖啡",
                "瑞幸新品", "生椰拿铁", "咖啡优惠券"
            ]
        },
        {
            "name": "星巴克",
            "aliases": ["Starbucks"],
            "industry": "咖啡",
            "keywords": [
                "高端咖啡", "商务咖啡", "第三空间",
                "星巴克推荐", "星冰乐", "咖啡环境"
            ]
        },
        {
            "name": "喜茶",
            "aliases": ["HEYTEA"],
            "industry": "茶饮",
            "keywords": [
                "奶茶推荐", "新式茶饮", "水果茶",
                "喜茶新品", "网红奶茶", "下午茶"
            ]
        },
        {
            "name": "奈雪的茶",
            "aliases": ["奈雪", " Nayuki"],
            "industry": "茶饮",
            "keywords": [
                "欧包奶茶", "下午茶", "奶茶推荐",
                "奈雪新品", "烘焙茶饮", "网红店"
            ]
        }
    ]
    
    def __init__(self, db_file="monitor.db"):
        self.db = DatabaseManager(db_file)
    
    def monitor(self, brands=None, platforms=None, keywords=None):
        """
        执行监测
        
        Args:
            brands: 品牌列表，如 ["印暨咖啡", "星巴克"]
            platforms: 平台列表，如 ["kimi", "doubao"]
            keywords: 关键词列表，如 ["咖啡推荐"]
        """
        if not brands:
            brands = self.DEFAULT_BRANDS
        else:
            brands = [b for b in self.DEFAULT_BRANDS if b["name"] in brands]
        
        if not platforms:
            platforms = list(self.PLATFORMS.keys())
        
        print(f"开始监测 {len(brands)} 个品牌，{len(platforms)} 个平台...")
        print("=" * 60)
        
        results = []
        
        for brand in brands:
            brand_name = brand["name"]
            brand_keywords = keywords if keywords else brand["keywords"]
            
            print(f"\n监测品牌: {brand_name}")
            print("-" * 60)
            
            for platform_id in platforms:
                platform_name = self.PLATFORMS[platform_id]
                print(f"  平台: {platform_name}")
                
                for keyword in brand_keywords:
                    # 模拟 API 调用
                    result = MockAIClient.query(platform_id, keyword, brand_name)
                    
                    # 保存到数据库
                    self.db.save_record(result)
                    results.append(result)
                    
                    # 打印结果
                    status = "✓ 提及" if result["is_mentioned"] else "✗ 未提及"
                    rank_info = f" 排名:{result['rank']}" if result["is_mentioned"] else ""
                    print(f"    {keyword:20s} -> {status}{rank_info}")
                    
                    # 模拟延迟
                    time.sleep(0.1)
        
        print("\n" + "=" * 60)
        print(f"监测完成！共记录 {len(results)} 条数据")
        
        return results
    
    def generate_report(self, output_dir="."):
        """生成 HTML 报告"""
        stats = self.db.get_stats()
        recent_records = self.db.get_recent_records(100)
        
        # 生成报告 HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>GEO 监测报告 - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }}
                .metrics {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                .card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .number {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                }}
                table {{
                    width: 100%;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #eee;
                }}
                th {{
                    background: #f8f9fa;
                    font-weight: 600;
                }}
                .mentioned {{ color: #10b981; font-weight: bold; }}
                .not-mentioned {{ color: #ef4444; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>GEO AI 搜索引擎监测报告</h1>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="metrics">
                <div class="card">
                    <div class="number">{len(stats)}</div>
                    <div>监测组合数</div>
                </div>
        """
        
        # 添加统计数据
        for stat in stats[:4]:
            html_content += f"""
                <div class="card">
                    <div class="number">{stat['visibility_rate']:.1f}%</div>
                    <div>{stat['brand']} @ {stat['platform']}</div>
                </div>
            """
        
        html_content += """
            </div>
            
            <h2>详细记录</h2>
            <table>
                <tr>
                    <th>时间</th>
                    <th>品牌</th>
                    <th>平台</th>
                    <th>关键词</th>
                    <th>状态</th>
                    <th>排名</th>
                    <th>置信度</th>
                </tr>
        """
        
        for record in recent_records[:50]:
            status_class = "mentioned" if record["is_mentioned"] else "not-mentioned"
            status_text = "✓ 提及" if record["is_mentioned"] else "✗ 未提及"
            
            html_content += f"""
                <tr>
                    <td>{record["created_at"]}</td>
                    <td>{record["brand"]}</td>
                    <td>{record["platform"]}</td>
                    <td>{record["keyword"]}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{record["rank"] if record["rank"] > 0 else "-"}</td>
                    <td>{record["confidence"]}%</td>
                </tr>
            """
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        # 保存报告
        report_file = os.path.join(output_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"\n✅ 报告已生成: {report_file}")
        return report_file
    
    def generate_demo_data(self, days=7):
        """生成演示数据"""
        print(f"生成过去 {days} 天的演示数据...")
        
        brands = self.DEFAULT_BRANDS
        platforms = list(self.PLATFORMS.keys())
        
        total_records = 0
        
        for day in range(days):
            date = datetime.now() - timedelta(days=day)
            
            for brand in brands:
                for platform_id in platforms:
                    # 每天每个品牌平台组合生成 5-15 条记录
                    num_records = random.randint(5, 15)
                    
                    for _ in range(num_records):
                        keyword = random.choice(brand["keywords"])
                        result = MockAIClient.query(platform_id, keyword, brand["name"])
                        
                        # 修改时间戳
                        result["timestamp"] = (date - timedelta(hours=random.randint(0, 23))).isoformat()
                        
                        # 手动插入带指定时间的记录
                        conn = sqlite3.connect(self.db.db_file)
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO monitor_records 
                            (brand, platform, keyword, is_mentioned, rank, confidence, response, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            result["brand"],
                            result["platform"],
                            result["keyword"],
                            1 if result["is_mentioned"] else 0,
                            result["rank"],
                            result["confidence"],
                            result["response"],
                            result["timestamp"]
                        ))
                        conn.commit()
                        conn.close()
                        
                        total_records += 1
        
        print(f"✅ 已生成 {total_records} 条演示数据")
        return total_records


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GEO AI 搜索引擎监测工具")
    parser.add_argument("--platforms", "-p", nargs="+", 
                       choices=["kimi", "doubao", "qianwen", "deepseek", "wenxin", "hunyuan", "zhipu"],
                       help="选择监测平台")
    parser.add_argument("--brands", "-b", nargs="+",
                       choices=["印暨咖啡", "瑞幸咖啡", "星巴克", "喜茶", "奈雪的茶"],
                       help="选择监测品牌")
    parser.add_argument("--keywords", "-k", nargs="+",
                       help="自定义关键词")
    parser.add_argument("--demo", "-d", action="store_true",
                       help="生成演示数据")
    parser.add_argument("--days", type=int, default=7,
                       help="演示数据天数（默认7天）")
    parser.add_argument("--report", "-r", action="store_true",
                       help="生成报告")
    
    args = parser.parse_args()
    
    # 初始化监测器
    monitor = GEOMonitor()
    
    if args.demo:
        # 生成演示数据
        monitor.generate_demo_data(args.days)
        print("\n演示数据已生成！")
        print("提示: 运行 `python monitor.py --report` 生成报告")
        
    elif args.report:
        # 只生成报告
        monitor.generate_report()
        
    else:
        # 执行监测
        results = monitor.monitor(
            brands=args.brands,
            platforms=args.platforms,
            keywords=args.keywords
        )
        
        # 生成报告
        monitor.generate_report()


if __name__ == "__main__":
    main()
