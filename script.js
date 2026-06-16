// ==================== 弱弱投资日记 - Main Script ====================

(function() {
    'use strict';

    // ==================== Configuration ====================
    const CONFIG = {
        articlesPerPage: 6,
        marketApiBase: 'https://qt.gtimg.cn/q=',
        indices: {
            'sh-index': 'sh000001',
            'sz-index': 'sz399001',
            'cy-index': 'sz399006'
        }
    };

    // ==================== State ====================
    let state = {
        articles: [],
        currentPage: 1,
        isLoading: false
    };

    // ==================== DOM Ready ====================
    document.addEventListener('DOMContentLoaded', function() {
        initMobileMenu();
        initBackToTop();
        initSmoothScroll();
        loadArticles();
        initMarketTicker();
    });

    // ==================== Mobile Menu ====================
    function initMobileMenu() {
        const btn = document.querySelector('.mobile-menu-btn');
        const nav = document.querySelector('.main-nav');
        
        if (btn && nav) {
            btn.addEventListener('click', function() {
                nav.classList.toggle('active');
                btn.classList.toggle('active');
            });

            // Close menu on link click
            nav.querySelectorAll('.nav-link').forEach(function(link) {
                link.addEventListener('click', function() {
                    nav.classList.remove('active');
                    btn.classList.remove('active');
                });
            });
        }
    }

    // ==================== Back to Top ====================
    function initBackToTop() {
        const btn = document.getElementById('backToTop');
        
        if (btn) {
            window.addEventListener('scroll', function() {
                if (window.scrollY > 300) {
                    btn.classList.add('visible');
                } else {
                    btn.classList.remove('visible');
                }
            });

            btn.addEventListener('click', function() {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        }
    }

    // ==================== Smooth Scroll ====================
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                
                if (targetId === '#') return;
                
                const target = document.querySelector(targetId);
                if (target) {
                    const headerHeight = document.querySelector('.site-header').offsetHeight;
                    const targetPosition = target.offsetTop - headerHeight - 20;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // ==================== Load Articles ====================
    function loadArticles() {
        // In production, this would fetch from articles/ directory
        // For now, we'll simulate with placeholder data
        const articlesGrid = document.getElementById('articlesGrid');
        
        if (!articlesGrid) return;

        // Check if we're on an article page
        if (window.location.pathname.includes('/articles/')) {
            loadArticleDetail();
            return;
        }

        // Try to load article list from articles directory
        fetchArticleList()
            .then(function(articles) {
                if (articles && articles.length > 0) {
                    state.articles = articles;
                    renderArticles();
                    updateStats();
                }
            })
            .catch(function() {
                // Show placeholder if no articles found
                console.log('No articles found, showing placeholder');
            });
    }

    // ==================== Fetch Article List ====================
    async function fetchArticleList() {
        // This would be implemented with a server-side endpoint
        // For GitHub Pages, we can use a static JSON file
        try {
            const response = await fetch('/ruoruo-blog/articles/index.json');
            if (response.ok) {
                return await response.json();
            }
        } catch (e) {
            // Fallback: try to parse from directory listing
        }
        
        // Return sample data for demo
        return getSampleArticles();
    }

    // ==================== Sample Articles ====================
    function getSampleArticles() {
        const today = new Date();
        const articles = [];
        
        for (let i = 0; i < 5; i++) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            
            const dateStr = date.toISOString().split('T')[0];
            const change = (Math.random() * 4 - 2).toFixed(2);
            const isUp = parseFloat(change) >= 0;
            
            articles.push({
                id: dateStr,
                date: dateStr,
                title: dateStr + ' A股市场分析：' + (isUp ? '市场企稳反弹' : '震荡调整延续'),
                excerpt: '今日市场整体呈现' + (isUp ? '反弹' : '调整') + '态势，主要指数' + (isUp ? '收涨' : '收跌') + '...',
                change: change,
                isUp: isUp,
                url: '/ruoruo-blog/articles/' + dateStr + '.html'
            });
        }
        
        return articles;
    }

    // ==================== Render Articles ====================
    function renderArticles() {
        const grid = document.getElementById('articlesGrid');
        if (!grid) return;

        const startIndex = (state.currentPage - 1) * CONFIG.articlesPerPage;
        const endIndex = startIndex + CONFIG.articlesPerPage;
        const articlesToShow = state.articles.slice(0, endIndex);

        grid.innerHTML = articlesToShow.map(function(article) {
            return createArticleCard(article);
        }).join('');

        // Show load more button if needed
        const loadMore = document.getElementById('loadMore');
        if (loadMore) {
            loadMore.style.display = endIndex < state.articles.length ? 'block' : 'none';
        }
    }

    // ==================== Create Article Card ====================
    function createArticleCard(article) {
        const changeClass = article.isUp ? 'up' : 'down';
        const changeSign = article.isUp ? '+' : '';
        const changeLabel = article.isUp ? '涨' : '跌';
        
        return '<article class="article-card">' +
            '<div class="article-meta">' +
                '<span class="article-date">' + article.date + '</span>' +
                '<span class="article-tag">市场分析</span>' +
            '</div>' +
            '<h3 class="article-title">' + article.title + '</h3>' +
            '<p class="article-excerpt">' + article.excerpt + '</p>' +
            '<div>' +
                '<a href="' + article.url + '" class="article-link">阅读全文 →</a>' +
                '<span class="article-change ' + changeClass + '">' + changeSign + article.change + '% ' + changeLabel + '</span>' +
            '</div>' +
        '</article>';
    }

    // ==================== Load More Articles ====================
    window.loadMoreArticles = function() {
        state.currentPage++;
        renderArticles();
    };

    // ==================== Update Stats ====================
    function updateStats() {
        const articleCount = document.getElementById('articleCount');
        const trackingDays = document.getElementById('trackingDays');
        
        if (articleCount) {
            animateNumber(articleCount, state.articles.length);
        }
        
        if (trackingDays) {
            animateNumber(trackingDays, state.articles.length);
        }
    }

    // ==================== Animate Number ====================
    function animateNumber(element, target) {
        let current = 0;
        const increment = target / 30;
        const timer = setInterval(function() {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 50);
    }

    // ==================== Market Ticker ====================
    function initMarketTicker() {
        updateMarketData();
        // Update every 30 seconds during market hours
        setInterval(updateMarketData, 30000);
    }

    // ==================== Update Market Data ====================
    async function updateMarketData() {
        const indices = CONFIG.indices;
        
        for (const [elementId, symbol] of Object.entries(indices)) {
            try {
                const data = await fetchMarketData(symbol);
                if (data) {
                    updateTickerItem(elementId, data);
                }
            } catch (e) {
                console.log('Failed to fetch data for ' + symbol);
            }
        }
    }

    // ==================== Fetch Market Data ====================
    async function fetchMarketData(symbol) {
        try {
            // Using a CORS proxy for GitHub Pages
            const proxyUrl = 'https://api.allorigins.win/raw?url=';
            const apiUrl = CONFIG.marketApiBase + symbol;
            
            const response = await fetch(proxyUrl + encodeURIComponent(apiUrl));
            if (!response.ok) return null;
            
            const text = await response.text();
            return parseMarketData(text, symbol);
        } catch (e) {
            return null;
        }
    }

    // ==================== Parse Market Data ====================
    function parseMarketData(text, symbol) {
        // Tencent API returns data in format: v_sh000001="1~上证指数~000001~3367.05~3364.83~3368.87~..."
        const match = text.match(/v_[a-z]+\d+="(.+)"/);
        if (!match) return null;
        
        const parts = match[1].split('~');
        if (parts.length < 5) return null;
        
        return {
            name: parts[1],
            price: parseFloat(parts[3]),
            change: parseFloat(parts[31]),
            changePercent: parseFloat(parts[32])
        };
    }

    // ==================== Update Ticker Item ====================
    function updateTickerItem(elementId, data) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const changeClass = data.changePercent >= 0 ? 'up' : 'down';
        const sign = data.changePercent >= 0 ? '+' : '';
        
        element.className = changeClass;
        element.textContent = data.price.toFixed(2) + ' ' + sign + data.changePercent.toFixed(2) + '%';
    }

    // ==================== Load Article Detail ====================
    function loadArticleDetail() {
        const path = window.location.pathname;
        const articleName = path.split('/').pop().replace('.html', '');
        
        // This would load the specific article content
        console.log('Loading article: ' + articleName);
    }

})();
