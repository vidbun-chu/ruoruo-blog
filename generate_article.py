#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
弱弱投资日记 - 每日投资分析文章生成器
Ruoruo Investment Diary - Daily Investment Analysis Generator

Fetches market data from Tencent API and generates structured HTML articles.
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

# ==================== Configuration ====================
BASE_DIR = Path(__file__).parent
ARTICLES_DIR = BASE_DIR / 'articles'
INDEX_FILE = ARTICLES_DIR / 'index.json'

# Market symbols to fetch
MARKET_SYMBOLS = {
    'sh000001': '上证指数',
    'sz399001': '深证成指',
    'sz399006': '创业板指',
    'sh000300': '沪深300',
    'sh000016': '上证50',
}

# Stock symbols to analyze (popular A-share stocks)
STOCK_SYMBOLS = {
    'sh600519': '贵州茅台',
    'sh601318': '中国平安',
    'sz000858': '五粮液',
    'sz300750': '宁德时代',
    'sh600036': '招商银行',
}


def fetch_market_data(symbol: str) -> dict:
    """Fetch market data from Tencent API."""
    url = f'https://qt.gtimg.cn/q={symbol}'
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gbk')
            return parse_tencent_data(data, symbol)
    except Exception as e:
        print(f'Failed to fetch {symbol}: {e}')
        return None


def parse_tencent_data(data: str, symbol: str) -> dict:
    """Parse Tencent API response."""
    # Format: v_sh000001="1~上证指数~000001~3367.05~..."
    import re
    match = re.search(r'v_[a-z]+\d+="(.+)"', data)
    if not match:
        return None
    
    parts = match.group(1).split('~')
    if len(parts) < 50:
        return None
    
    try:
        return {
            'symbol': symbol,
            'name': parts[1],
            'code': parts[2],
            'price': float(parts[3]) if parts[3] else 0,
            'yesterday_close': float(parts[4]) if parts[4] else 0,
            'open': float(parts[5]) if parts[5] else 0,
            'high': float(parts[33]) if parts[33] else 0,
            'low': float(parts[34]) if parts[34] else 0,
            'volume': float(parts[6]) if parts[6] else 0,
            'amount': float(parts[37]) if parts[37] else 0,
            'change': float(parts[31]) if parts[31] else 0,
            'change_percent': float(parts[32]) if parts[32] else 0,
            'time': parts[30] if len(parts) > 30 else '',
        }
    except (ValueError, IndexError) as e:
        print(f'Parse error for {symbol}: {e}')
        return None


def fetch_all_data() -> dict:
    """Fetch all market data."""
    data = {
        'indices': {},
        'stocks': {},
    }
    
    print('Fetching market indices...')
    for symbol, name in MARKET_SYMBOLS.items():
        result = fetch_market_data(symbol)
        if result:
            data['indices'][symbol] = result
            print(f'  ✓ {name}: {result["price"]:.2f} ({result["change_percent"]:+.2f}%)')
    
    print('\nFetching stock data...')
    for symbol, name in STOCK_SYMBOLS.items():
        result = fetch_market_data(symbol)
        if result:
            data['stocks'][symbol] = result
            print(f'  ✓ {name}: {result["price"]:.2f} ({result["change_percent"]:+.2f}%)')
    
    return data


def analyze_market(data: dict) -> dict:
    """Generate market analysis based on data."""
    analysis = {
        'summary': '',
        'trend': 'neutral',
        'highlights': [],
        'risks': [],
    }
    
    indices = data.get('indices', {})
    if not indices:
        analysis['summary'] = '市场数据获取失败，无法进行分析。'
        return analysis
    
    # Analyze main index
    sh_index = indices.get('sh000001', {})
    if sh_index:
        change = sh_index.get('change_percent', 0)
        
        if change > 1:
            analysis['trend'] = 'bullish'
            analysis['summary'] = '今日A股市场强势上涨，主要指数大幅收涨，市场情绪明显回暖。'
        elif change > 0:
            analysis['trend'] = 'slightly_bullish'
            analysis['summary'] = '今日A股市场小幅上涨，市场整体呈现温和反弹态势。'
        elif change > -1:
            analysis['trend'] = 'slightly_bearish'
            analysis['summary'] = '今日A股市场小幅调整，市场整体呈现震荡整理态势。'
        else:
            analysis['trend'] = 'bearish'
            analysis['summary'] = '今日A股市场大幅下跌，市场情绪较为低迷，投资者需谨慎。'
        
        # Generate highlights based on individual stocks
        stocks = data.get('stocks', {})
        for symbol, stock_data in stocks.items():
            stock_change = stock_data.get('change_percent', 0)
            if abs(stock_change) > 3:
                direction = '大涨' if stock_change > 0 else '大跌'
                analysis['highlights'].append(
                    f'{stock_data["name"]}{direction}{abs(stock_change):.2f}%，值得关注。'
                )
        
        # Generate risk warnings
        if sh_index.get('high', 0) > 0 and sh_index.get('low', 0) > 0:
            volatility = (sh_index['high'] - sh_index['low']) / sh_index['low'] * 100
            if volatility > 2:
                analysis['risks'].append(f'日内波动率达{volatility:.2f}%，市场波动较大。')
    
    if not analysis['highlights']:
        analysis['highlights'].append('今日市场表现平稳，无明显异动个股。')
    
    if not analysis['risks']:
        analysis['risks'].append('当前市场风险可控，建议关注政策面变化。')
    
    return analysis


def generate_article_html(date_str: str, data: dict, analysis: dict) -> str:
    """Generate HTML article content."""
    trend_class = {
        'bullish': 'trend-bullish',
        'slightly_bullish': 'trend-slightly-bullish',
        'slightly_bearish': 'trend-slightly-bearish',
        'bearish': 'trend-bearish',
    }.get(analysis['trend'], 'trend-neutral')
    
    trend_label = {
        'bullish': '强势上涨',
        'slightly_bullish': '小幅上涨',
        'slightly_bearish': '小幅调整',
        'bearish': '大幅下跌',
    }.get(analysis['trend'], '震荡整理')
    
    # Build index table rows
    index_rows = ''
    for symbol, idx_data in data.get('indices', {}).items():
        change_class = 'up' if idx_data['change_percent'] >= 0 else 'down'
        sign = '+' if idx_data['change_percent'] >= 0 else ''
        index_rows += f'''
        <tr>
            <td>{idx_data['name']}</td>
            <td>{idx_data['price']:.2f}</td>
            <td class="{change_class}">{sign}{idx_data['change']:.2f}</td>
            <td class="{change_class}">{sign}{idx_data['change_percent']:.2f}%</td>
            <td>{idx_data['volume'] / 10000:.0f}万手</td>
        </tr>'''
    
    # Build stock table rows
    stock_rows = ''
    for symbol, stock_data in data.get('stocks', {}).items():
        change_class = 'up' if stock_data['change_percent'] >= 0 else 'down'
        sign = '+' if stock_data['change_percent'] >= 0 else ''
        stock_rows += f'''
        <tr>
            <td>{stock_data['name']}</td>
            <td>{stock_data['price']:.2f}</td>
            <td class="{change_class}">{sign}{stock_data['change']:.2f}</td>
            <td class="{change_class}">{sign}{stock_data['change_percent']:.2f}%</td>
        </tr>'''
    
    # Build highlights list
    highlights_list = ''.join(f'<li>{h}</li>' for h in analysis['highlights'])
    
    # Build risks list
    risks_list = ''.join(f'<li>{r}</li>' for r in analysis['risks'])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="弱弱投资日记 - {date_str} A股市场分析">
    <meta name="keywords" content="A股分析,投资日记,{date_str}市场分析,股票行情">
    <meta name="author" content="弱弱投资">
    <meta property="og:title" content="{date_str} A股市场分析 - 弱弱投资日记">
    <meta property="og:description" content="{analysis['summary']}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://vidbun-chu.github.io/ruoruo-blog/articles/{date_str}.html">
    <meta property="article:published_time" content="{date_str}">
    <title>{date_str} A股市场分析 - 弱弱投资日记</title>
    <link rel="stylesheet" href="../style.css">
    <style>
        .trend-indicator {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 16px;
        }}
        .trend-bullish {{ background: rgba(233,69,96,0.15); color: #e94560; }}
        .trend-slightly-bullish {{ background: rgba(233,69,96,0.1); color: #e94560; }}
        .trend-slightly-bearish {{ background: rgba(0,212,170,0.1); color: #00d4aa; }}
        .trend-bearish {{ background: rgba(0,212,170,0.15); color: #00d4aa; }}
        .up {{ color: #e94560; }}
        .down {{ color: #00d4aa; }}
        .data-section {{ margin: 24px 0; }}
        .data-section h2 {{ font-size: 1.3rem; color: #e0e0e0; margin-bottom: 16px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #2a2a40; }}
        th {{ color: #a0a0b0; font-weight: 500; font-size: 0.85rem; }}
        td {{ font-family: "SF Mono","Consolas",monospace; font-size: 0.9rem; }}
        .analysis-section {{ margin: 24px 0; }}
        .analysis-section ul {{ padding-left: 20px; }}
        .analysis-section li {{ margin: 8px 0; color: #a0a0b0; }}
    </style>
</head>
<body>
    <header class="site-header">
        <div class="container">
            <div class="header-content">
                <div class="logo-section">
                    <h1 class="site-title">弱弱投资日记</h1>
                    <p class="site-subtitle">Ruoruo Investment Diary</p>
                </div>
                <nav class="main-nav">
                    <a href="/ruoruo-blog/" class="nav-link">首页</a>
                    <a href="/ruoruo-blog/#articles" class="nav-link">文章</a>
                </nav>
            </div>
        </div>
    </header>
    
    <main class="container article-detail">
        <a href="/ruoruo-blog/" class="article-back">← 返回首页</a>
        
        <div class="article-detail-header">
            <h1>{date_str} A股市场分析</h1>
            <div class="article-detail-meta">
                <span>📅 {date_str}</span>
                <span>📊 市场分析</span>
                <span>🤖 自动生成</span>
            </div>
            <div class="{trend_class} trend-indicator">{trend_label}</div>
        </div>
        
        <div class="article-detail-body">
            <p>{analysis['summary']}</p>
            
            <div class="data-section">
                <h2>📈 主要指数</h2>
                <div class="market-data">
                    <table>
                        <thead>
                            <tr>
                                <th>指数名称</th>
                                <th>收盘价</th>
                                <th>涨跌</th>
                                <th>涨跌幅</th>
                                <th>成交量</th>
                            </tr>
                        </thead>
                        <tbody>{index_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="data-section">
                <h2>📊 重点个股</h2>
                <div class="market-data">
                    <table>
                        <thead>
                            <tr>
                                <th>股票名称</th>
                                <th>收盘价</th>
                                <th>涨跌</th>
                                <th>涨跌幅</th>
                            </tr>
                        </thead>
                        <tbody>{stock_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="analysis-section">
                <h2>🔍 市场亮点</h2>
                <ul>{highlights_list}
                </ul>
            </div>
            
            <div class="analysis-section">
                <h2>⚠️ 风险提示</h2>
                <ul>{risks_list}
                </ul>
            </div>
            
            <blockquote>
                <p>免责声明：本文由程序自动生成，仅供学习交流，不构成任何投资建议。投资有风险，入市需谨慎。</p>
            </blockquote>
        </div>
    </main>
    
    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <p class="footer-brand">弱弱投资日记</p>
                <p class="footer-copy">© 2024-2026 弱弱投资日记. All rights reserved.</p>
            </div>
        </div>
    </footer>
    
    <script src="../script.js"></script>
</body>
</html>'''
    
    return html


def update_index(date_str: str, title: str, excerpt: str, change: float):
    """Update the articles index JSON file."""
    index = []
    
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                index = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            index = []
    
    # Check if article already exists
    existing = [a for a in index if a['date'] == date_str]
    if existing:
        # Update existing entry
        existing[0].update({
            'title': title,
            'excerpt': excerpt,
            'change': change,
            'isUp': change >= 0,
            'url': f'/ruoruo-blog/articles/{date_str}.html'
        })
    else:
        # Add new entry
        index.insert(0, {
            'id': date_str,
            'date': date_str,
            'title': title,
            'excerpt': excerpt,
            'change': change,
            'isUp': change >= 0,
            'url': f'/ruoruo-blog/articles/{date_str}.html'
        })
    
    # Sort by date descending
    index.sort(key=lambda x: x['date'], reverse=True)
    
    # Write to file
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f'Updated index: {INDEX_FILE}')


def update_rss(date_str: str, title: str, description: str):
    """Update RSS feed."""
    rss_file = BASE_DIR / 'feed.xml'
    
    # Simple RSS feed generation
    items = []
    
    # Read existing items if file exists
    if rss_file.exists():
        import re
        with open(rss_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract existing items
            items = re.findall(r'<item>.*?</item>', content, re.DOTALL)
    
    # Add new item
    new_item = f'''    <item>
      <title>{title}</title>
      <link>https://vidbun-chu.github.io/ruoruo-blog/articles/{date_str}.html</link>
      <description>{description}</description>
      <pubDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0800')}</pubDate>
      <guid>https://vidbun-chu.github.io/ruoruo-blog/articles/{date_str}.html</guid>
    </item>'''
    
    # Remove existing item for same date if exists
    items = [i for i in items if date_str not in i]
    items.insert(0, new_item)
    
    # Keep only last 20 items
    items = items[:20]
    
    rss_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>弱弱投资日记</title>
    <link>https://vidbun-chu.github.io/ruoruo-blog/</link>
    <description>每日A股市场分析、投资策略与财经观察</description>
    <language>zh-cn</language>
    <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0800')}</lastBuildDate>
    <atom:link href="https://vidbun-chu.github.io/ruoruo-blog/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>'''
    
    with open(rss_file, 'w', encoding='utf-8') as f:
        f.write(rss_content)
    
    print(f'Updated RSS feed: {rss_file}')


def main():
    """Main entry point."""
    print('=' * 60)
    print('弱弱投资日记 - 每日投资分析文章生成器')
    print('=' * 60)
    print()
    
    # Ensure directories exist
    ARTICLES_DIR.mkdir(exist_ok=True)
    
    # Get today's date
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    
    print(f'Generating article for {date_str}...')
    print()
    
    # Fetch market data
    data = fetch_all_data()
    
    if not data['indices']:
        print('ERROR: Failed to fetch market data. Exiting.')
        return 1
    
    print()
    print('Analyzing market data...')
    analysis = analyze_market(data)
    
    print(f'Trend: {analysis["trend"]}')
    print(f'Summary: {analysis["summary"]}')
    print()
    
    # Generate article HTML
    print('Generating article HTML...')
    html = generate_article_html(date_str, data, analysis)
    
    # Save article
    article_file = ARTICLES_DIR / f'{date_str}.html'
    with open(article_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'Saved article: {article_file}')
    
    # Update index
    sh_data = data['indices'].get('sh000001', {})
    update_index(
        date_str=date_str,
        title=f'{date_str} A股市场分析：{"市场企稳反弹" if analysis["trend"] in ["bullish", "slightly_bullish"] else "震荡调整延续"}',
        excerpt=analysis['summary'],
        change=sh_data.get('change_percent', 0)
    )
    
    # Update RSS
    update_rss(date_str, f'{date_str} A股市场分析', analysis['summary'])
    
    print()
    print('=' * 60)
    print('✅ Article generation complete!')
    print('=' * 60)
    
    return 0


if __name__ == '__main__':
    exit(main())
