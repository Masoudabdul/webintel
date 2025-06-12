"""
Advanced Multi-Engine Search System - Tavily-like Performance
Real-time, AI-optimized search with intelligent ranking
"""

import asyncio
import aiohttp
import time
import json
import hashlib
import logging
from typing import List, Dict, Any, Set, Optional
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup
from dataclasses import dataclass
import random
import re

# Setup logger
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Structured search result"""
    title: str
    url: str
    content: str
    snippet: str
    domain: str
    score: float
    raw_content: str = ""
    timestamp: float = 0.0

class AdvancedSearchEngine:
    """Advanced multi-engine search system with AI optimization"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.scraped_urls: Set[str] = set()
        self.content_cache: Dict[str, SearchResult] = {}
        
        # Core search engines (prioritize working ones)
        self.search_engines = [
            self._search_bing,      # Primary - working well
            self._search_duckduckgo, # Secondary
            self._search_google     # Tertiary - may be blocked
        ]
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
    
    async def __aenter__(self):
        """Create optimized session"""
        timeout = aiohttp.ClientTimeout(total=10, connect=3, sock_read=7)
        connector = aiohttp.TCPConnector(
            limit=100, limit_per_host=30, ttl_dns_cache=300, use_dns_cache=True,
            keepalive_timeout=30, enable_cleanup_closed=True
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout, connector=connector,
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'DNT': '1'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def advanced_search(self, query: str, max_results: int = 10,
                            search_depth: str = "advanced") -> Dict[str, Any]:
        """Advanced search with real web results"""
        start_time = time.time()

        # Step 1: Fast multi-engine search
        all_urls = await self._fast_multi_engine_search(query, max_results)

        # Step 2: Quick URL filtering
        filtered_urls = self._quick_url_filter(all_urls, max_results * 3)

        # Step 3: Fast content extraction
        search_results = await self._fast_content_extraction(filtered_urls, query)

        # Step 4: Quick ranking
        ranked_results = self._quick_ranking(search_results, query)

        # Step 5: Generate answer
        direct_answer = self._generate_quick_answer(ranked_results, query)

        processing_time = time.time() - start_time

        return {
            "query": query,
            "answer": direct_answer,
            "results": ranked_results[:max_results],
            "total_sources": len(ranked_results),
            "response_time": round(processing_time, 2),
            "search_engines_used": 3,  # Focus on working engines
            "urls_processed": len(filtered_urls),
            "confidence": self._calculate_confidence(ranked_results)
        }
    
    # REMOVED: Smart query generation that modifies user queries
    # WebIntel now searches EXACTLY what the user asks for

    async def _fast_multi_engine_search(self, query: str, max_results: int) -> List[str]:
        """Real web search using multiple engines - NO PREDEFINED URLs"""

        # Use working search engines in priority order (DuckDuckGo first since it's working)
        search_tasks = [
            self._search_duckduckgo(query, max_results), # Primary - working well
            self._search_bing(query, max_results),      # Secondary - may have issues
            self._search_google(query, max_results)     # Tertiary - may fail
        ]

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*search_tasks, return_exceptions=True),
                timeout=12  # Increased timeout for better results
            )
        except asyncio.TimeoutError:
            results = []

        # Collect ONLY real search results
        all_urls = []
        for i, result in enumerate(results):
            if isinstance(result, list):
                all_urls.extend(result)

        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in all_urls:
            if url not in seen and self._is_real_search_result(url):
                seen.add(url)
                unique_urls.append(url)

        # If no URLs found, try alternative search methods
        if not unique_urls:
            alternative_urls = await self._alternative_search(query, max_results)
            unique_urls.extend(alternative_urls)

        return unique_urls

    async def _alternative_search(self, query: str, max_results: int) -> List[str]:
        """Alternative search method - try exact query only"""

        # Only try the exact query with different engines
        alternative_urls = []

        # Try exact query with different engines one more time
        try:
            # Try DuckDuckGo again with longer timeout
            ddg_results = await self._search_duckduckgo(query, max_results)
            if ddg_results:
                alternative_urls.extend(ddg_results)
        except Exception:
            pass

        return alternative_urls[:max_results]

    def _is_real_search_result(self, url: str) -> bool:
        """Check if URL is a real search result (not predefined)"""
        if not url or not url.startswith('http'):
            return False

        # Exclude search engine URLs and ads
        bad_patterns = [
            'google.com/search', 'bing.com/search', 'duckduckgo.com',
            'yahoo.com/search', 'yandex.com/search',
            'googleadservices.com', 'googlesyndication.com',
            'doubleclick.net', 'googletagmanager.com'
        ]

        return not any(bad in url.lower() for bad in bad_patterns)

    def _quick_url_filter(self, urls: List[str], max_urls: int) -> List[str]:
        """Filter URLs to keep only real search results"""
        if not urls:
            return []  # NO FALLBACK URLs - only real results

        # Remove duplicates
        unique_urls = list(dict.fromkeys(urls))

        # Filter for real search results only
        filtered_urls = []
        for url in unique_urls:
            if self._is_real_search_result(url) and len(filtered_urls) < max_urls:
                filtered_urls.append(url)

        return filtered_urls[:max_urls]

    # REMOVED: No more fallback URLs - only real search results

    async def _fast_content_extraction(self, urls: List[str], query: str) -> List[SearchResult]:
        """Ultra-fast content extraction with guaranteed results"""
        if not urls:
            return []

        logger.info(f"Extracting content from {len(urls)} URLs")
        semaphore = asyncio.Semaphore(10)  # Reduced for stability

        async def extract_single(url):
            async with semaphore:
                try:
                    result = await self._extract_content_fast(url, query)
                    if result:
                        logger.info(f"Successfully extracted content from {url}")
                        return result
                    else:
                        logger.warning(f"No content extracted from {url}")
                        return None
                except Exception as e:
                    logger.error(f"Error extracting from {url}: {e}")
                    return None

        # Process URLs in batches for better success rate
        priority_urls = urls[:6]  # Process only top 6 URLs for speed
        tasks = [extract_single(url) for url in priority_urls]

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=8  # Increased timeout for better success
            )
        except asyncio.TimeoutError:
            logger.warning("Content extraction timed out")
            results = []

        search_results = []
        for result in results:
            if isinstance(result, SearchResult) and result.content and len(result.content) > 50:
                search_results.append(result)

        logger.info(f"Successfully extracted {len(search_results)} results")

        # ONLY return real extracted content - NO FALLBACKS
        if not search_results:
            logger.error(f"CRITICAL: No real content extracted from {len(urls)} URLs for query")
            logger.error("This means WebIntel failed to retrieve any real web content")
            return []

        logger.info(f"SUCCESS: Extracted {len(search_results)} real web results")
        return search_results[:15]  # Return top 15 results

    # REMOVED: All predefined content generation methods
    # WebIntel now ONLY returns real web content extracted from actual websites

    def _quick_ranking(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Quick ranking system"""
        if not results:
            return []

        # Sort by score
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)

        # Apply basic diversity
        diverse_results = []
        domain_count = {}

        for result in sorted_results:
            domain = result.domain
            if domain_count.get(domain, 0) < 2:  # Max 2 per domain
                diverse_results.append(result)
                domain_count[domain] = domain_count.get(domain, 0) + 1

        return diverse_results

    def _generate_quick_answer(self, results: List[SearchResult], query: str) -> str:
        """Generate quick direct answer - GUARANTEED to work"""
        if not results:
            return f"I searched for information about '{query}' but couldn't find specific results. Please try rephrasing your query or using different keywords."

        # Use top result for answer
        top_result = results[0]

        # Try to get meaningful content
        if top_result.snippet and len(top_result.snippet) > 50:
            return top_result.snippet
        elif top_result.content and len(top_result.content) > 100:
            # Extract first meaningful sentence
            sentences = top_result.content.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 50:
                    return sentence + "."

            # Fallback to first part of content
            return top_result.content[:200] + "..."

        # Generate comprehensive answer based on sources found
        domains = [r.domain for r in results[:3]]
        unique_domains = list(set(domains))

        answer = f"I found {len(results)} relevant sources about '{query}' "

        if unique_domains:
            if len(unique_domains) == 1:
                answer += f"from {unique_domains[0]}. "
            else:
                answer += f"from {len(unique_domains)} different sources including {', '.join(unique_domains[:2])}. "

        answer += "The sources contain detailed information related to your query. "
        answer += "Please check the links below to access the full content and get comprehensive information about your topic."

        return answer
    
    # REMOVED: Unused complex filtering methods - using simple approach now

    async def _search_google(self, query: str, max_results: int) -> List[str]:
        """Improved Google search with better URL extraction"""
        try:
            encoded_query = quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}&num={min(max_results, 20)}&hl=en&gl=us&safe=off"

            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            async with self.session.get(search_url, headers=headers, timeout=8) as response:
                if response.status == 200:
                    html = await response.text()
                    urls = self._extract_google_urls(html)
                    return urls
        except:
            pass
        return []  # No fallback URLs

    def _get_query_specific_urls(self, query: str) -> List[str]:
        """NO MORE PREDEFINED URLs - return empty list"""
        return []  # Only real search results

        # ALL PREDEFINED URLs REMOVED - ONLY REAL SEARCH RESULTS

    async def _search_bing(self, query: str, max_results: int) -> List[str]:
        """Advanced Bing search with better error handling"""
        try:
            encoded_query = quote_plus(query)
            search_url = f"https://www.bing.com/search?q={encoded_query}&count={min(max_results, 50)}"

            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive'
            }

            async with self.session.get(search_url, headers=headers, timeout=8) as response:
                if response.status == 200:
                    html = await response.text()
                    urls = self._extract_bing_urls(html)
                    return urls
        except Exception:
            pass
        return []

    async def _search_duckduckgo(self, query: str, max_results: int) -> List[str]:
        """Improved DuckDuckGo search"""
        try:
            encoded_query = quote_plus(query)
            search_url = f"https://duckduckgo.com/html/?q={encoded_query}&kl=us-en&s=0&dc={max_results}"

            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'DNT': '1',
                'Connection': 'keep-alive'
            }

            async with self.session.get(search_url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    urls = self._extract_duckduckgo_urls(html)
                    return urls
        except Exception:
            pass
        return []

    # REMOVED: Unused search engines (Yahoo, Yandex, Startpage, Searx, Brave)

    def _extract_google_urls(self, html: str) -> List[str]:
        """Extract URLs from Google search results"""
        soup = BeautifulSoup(html, 'lxml')
        urls = []

        selectors = [
            'div.g a[href^="http"]',
            'div.yuRUbf a[href^="http"]',
            'h3 a[href^="http"]',
            'div.tF2Cxc a[href^="http"]',
            'div[data-ved] a[href^="http"]'
        ]

        for selector in selectors:
            for link in soup.select(selector):
                href = link.get('href')
                if href and self._is_valid_result_url(href):
                    urls.append(href)

        return list(dict.fromkeys(urls))[:20]

    def _extract_bing_urls(self, html: str) -> List[str]:
        """Extract URLs from Bing search results with comprehensive approach"""
        soup = BeautifulSoup(html, 'lxml')
        urls = []

        # Find all links and analyze them
        all_links = soup.find_all('a', href=True)

        # Extract URLs from all links
        for link in all_links:
            href = link.get('href')
            if href:
                # Clean up Bing redirect URLs
                if href.startswith('/'):
                    continue
                elif 'bing.com/ck/a?' in href:
                    # Extract actual URL from Bing redirect
                    import re
                    match = re.search(r'u=a1(.*?)&', href)
                    if match:
                        import urllib.parse
                        actual_url = urllib.parse.unquote(match.group(1))
                        if actual_url.startswith('http'):
                            href = actual_url

                if self._is_valid_result_url(href):
                    urls.append(href)

        # Also try to extract from cite elements (Bing shows URLs there)
        cite_elements = soup.find_all('cite')
        for cite in cite_elements:
            cite_text = cite.get_text().strip()
            if cite_text and not cite_text.startswith('http'):
                cite_text = 'https://' + cite_text
            if cite_text and self._is_valid_result_url(cite_text):
                urls.append(cite_text)

        unique_urls = list(dict.fromkeys(urls))[:20]
        return unique_urls

    def _extract_duckduckgo_urls(self, html: str) -> List[str]:
        """Extract URLs from DuckDuckGo search results - optimized"""
        soup = BeautifulSoup(html, 'lxml')
        urls = []

        # Find all links
        all_links = soup.find_all('a', href=True)

        # Extract URLs from all links
        for link in all_links:
            href = link.get('href')
            if href:
                # Handle DuckDuckGo redirect URLs
                if href.startswith('/l/?uddg='):
                    # Extract actual URL from DuckDuckGo redirect
                    import urllib.parse
                    try:
                        decoded = urllib.parse.unquote(href)
                        if 'https://' in decoded:
                            actual_url = decoded.split('https://', 1)[1].split('&')[0]
                            href = 'https://' + actual_url
                    except:
                        continue
                elif href.startswith('/'):
                    continue

                if self._is_valid_result_url(href):
                    urls.append(href)

        # Remove duplicates while preserving order
        unique_urls = []
        seen = set()
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        return unique_urls[:20]

    # REMOVED: Unused URL extractors (Yahoo, Yandex, Startpage, Searx, Brave)

    def _is_meaningful_content(self, content: str, query: str) -> bool:
        """Check if content is meaningful and not just boilerplate"""
        if not content or len(content.strip()) < 150:
            return False

        # Check for common boilerplate patterns
        boilerplate_patterns = [
            'cookies', 'privacy policy', 'terms of service', 'subscribe',
            'newsletter', 'advertisement', 'loading...', 'javascript required',
            'enable javascript', 'page not found', '404', 'error'
        ]

        content_lower = content.lower()
        boilerplate_count = sum(1 for pattern in boilerplate_patterns if pattern in content_lower)

        # If too much boilerplate, reject
        if boilerplate_count > 3:
            return False

        # Check if content has some relation to query
        query_words = query.lower().split()
        content_words = content_lower.split()

        # At least one query word should appear in content
        query_matches = sum(1 for word in query_words if word in content_words)

        return query_matches > 0 or len(content.strip()) > 500  # Long content is usually meaningful

    def _is_valid_result_url(self, url: str) -> bool:
        """Check if URL is valid for results - more permissive"""
        if not url or len(url) < 10:
            return False

        # Must start with http
        if not url.startswith('http'):
            return False

        # Skip obvious bad patterns
        bad_patterns = [
            'google.com/search', 'bing.com/search', 'bing.com/ck/a',
            'duckduckgo.com/l/', 'yahoo.com/search', 'yandex.com/search',
            'javascript:', 'mailto:', '#', 'data:',
            'go.microsoft.com/fwlink', 'support.microsoft.com/topic',
            'microsoft.com/privacy', 'microsoft.com/servicesagreement',
            'facebook.com/tr', 'google-analytics.com', 'googletagmanager.com',
            'doubleclick.net', 'googlesyndication.com', 'googleadservices.com'
        ]

        # Check if URL contains any bad patterns
        url_lower = url.lower()
        for pattern in bad_patterns:
            if pattern in url_lower:
                return False

        # Must have a domain
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if not parsed.netloc or len(parsed.netloc) < 3:
                return False
        except:
            return False

        return True

    async def _parallel_content_extraction(self, urls: List[str], query: str) -> List[SearchResult]:
        """Extract content from URLs in parallel - AGGRESSIVE APPROACH"""
        semaphore = asyncio.Semaphore(25)  # Increased concurrency

        async def extract_single(url):
            async with semaphore:
                # Try multiple times for better success rate
                for attempt in range(2):
                    try:
                        result = await self._extract_content_fast(url, query)
                        if result and result.content and len(result.content.strip()) > 100:
                            return result
                    except Exception:
                        if attempt == 0:
                            await asyncio.sleep(0.5)  # Brief delay before retry
                        continue
                return None

        tasks = [extract_single(url) for url in urls]

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=15  # Increased timeout for better results
            )
        except asyncio.TimeoutError:
            logger.warning("Content extraction timed out")
            results = []

        search_results = []
        for result in results:
            if isinstance(result, SearchResult) and result.content and len(result.content.strip()) > 100:
                search_results.append(result)

        logger.info(f"Successfully extracted {len(search_results)} valid results from {len(urls)} URLs")
        return search_results

    async def _extract_content_fast(self, url: str, query: str) -> Optional[SearchResult]:
        """Fast content extraction with better error handling"""
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive'
            }

            async with self.session.get(url, headers=headers, timeout=8) as response:
                if response.status != 200:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None

                html = await response.text()
                if not html or len(html) < 200:
                    logger.warning(f"Empty or too short HTML for {url}")
                    return None

                soup = BeautifulSoup(html, 'lxml')

                # Remove unwanted elements more aggressively
                for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']):
                    element.decompose()

                title = self._extract_title_fast(soup)
                content = self._extract_content_fast_method(soup)

                # Be more strict about content quality
                if len(content.strip()) < 150:
                    logger.warning(f"Content too short for {url}: {len(content)} chars")
                    return None

                # Ensure content is meaningful (not just navigation/boilerplate)
                if not self._is_meaningful_content(content, query):
                    logger.warning(f"Content not meaningful for {url}")
                    return None

                snippet = self._generate_snippet(content, query)
                score = self._calculate_relevance_score(content, title, query, url)
                domain = urlparse(url).netloc

                return SearchResult(
                    title=title,
                    url=url,
                    content=content[:3000],  # Reduced for performance
                    snippet=snippet,
                    domain=domain,
                    score=score,
                    raw_content=content,
                    timestamp=time.time()
                )

        except Exception as e:
            logger.error(f"Content extraction failed for {url}: {e}")
            return None

    def _extract_title_fast(self, soup: BeautifulSoup) -> str:
        """Fast title extraction"""
        title_tag = soup.find('title')
        if title_tag:
            return self._clean_text(title_tag.get_text())[:100]

        h1_tag = soup.find('h1')
        if h1_tag:
            return self._clean_text(h1_tag.get_text())[:100]

        return "No title"

    def _extract_content_fast_method(self, soup: BeautifulSoup) -> str:
        """Fast content extraction with multiple fallbacks"""
        # Try main content selectors first
        main_selectors = [
            'main', 'article', '[role="main"]', '.content', '.main-content',
            '.post-content', '.entry-content', '.article-content', '.page-content'
        ]

        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content and len(main_content.get_text(strip=True)) > 100:
                text = self._clean_text(main_content.get_text(separator=' ', strip=True))
                if len(text) > 100:
                    return text

        # Try paragraph-based extraction
        paragraphs = soup.find_all('p')
        if paragraphs:
            combined_text = ' '.join([p.get_text(strip=True) for p in paragraphs[:10]])
            if len(combined_text) > 100:
                return self._clean_text(combined_text)

        # Try div-based extraction
        divs = soup.find_all('div')
        for div in divs[:5]:
            text = div.get_text(strip=True)
            if len(text) > 200:
                return self._clean_text(text)

        # Final fallback to body
        body = soup.find('body')
        if body:
            text = self._clean_text(body.get_text(separator=' ', strip=True))
            if len(text) > 50:
                return text

        return ""

    def _clean_text(self, text: str) -> str:
        """Clean text"""
        import re
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text

    def _generate_snippet(self, content: str, query: str) -> str:
        """Generate relevant snippet"""
        if not content:
            return ""

        sentences = content.split('.')
        query_terms = query.lower().split()

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 50:
                sentence_lower = sentence.lower()
                if any(term in sentence_lower for term in query_terms):
                    return sentence[:200] + "..." if len(sentence) > 200 else sentence

        return content[:200] + "..." if len(content) > 200 else content

    def _calculate_relevance_score(self, content: str, title: str, query: str, url: str) -> float:
        """Calculate relevance score"""
        score = 0.0
        query_terms = query.lower().split()
        content_lower = content.lower()
        title_lower = title.lower()

        # Title matches (40% weight)
        title_matches = sum(1 for term in query_terms if term in title_lower)
        score += (title_matches / len(query_terms)) * 0.4

        # Content matches (40% weight)
        content_matches = sum(1 for term in query_terms if term in content_lower)
        score += (content_matches / len(query_terms)) * 0.4

        # Domain authority (20% weight)
        domain_score = self._get_domain_authority(url)
        score += domain_score * 0.2

        return min(score, 1.0)

    def _get_domain_authority(self, url: str) -> float:
        """Get domain authority score"""
        try:
            domain = urlparse(url).netloc.lower()
        except:
            return 0.0

        high_authority = ['wikipedia.org', 'stackoverflow.com', 'github.com', '.edu', '.gov']
        medium_authority = ['medium.com', 'dev.to', 'w3schools.com', '.org']

        if any(auth in domain for auth in high_authority):
            return 1.0
        elif any(auth in domain for auth in medium_authority):
            return 0.7
        else:
            return 0.4

    def _ai_ranking_system(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """AI-powered ranking system"""
        if not results:
            return []

        # Sort by score
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)

        # Apply diversity filter
        diverse_results = self._apply_diversity_filter(sorted_results)

        return diverse_results

    def _apply_diversity_filter(self, results: List[SearchResult]) -> List[SearchResult]:
        """Apply diversity filter to avoid too many results from same domain"""
        diverse_results = []
        domain_count = {}

        for result in results:
            domain = result.domain
            if domain_count.get(domain, 0) < 3:  # Max 3 results per domain
                diverse_results.append(result)
                domain_count[domain] = domain_count.get(domain, 0) + 1

        return diverse_results

    def _generate_direct_answer(self, results: List[SearchResult], query: str) -> str:
        """Generate direct answer like Tavily"""
        if not results:
            return "No relevant information found for the query."

        # Take top 3 results for answer generation
        top_results = results[:3]

        # Combine key information
        key_info = []
        for result in top_results:
            if result.score > 0.5:  # Only high-relevance results
                key_info.append(result.snippet)

        if not key_info:
            return f"Based on search results, information about '{query}' is available from {len(results)} sources."

        # Generate concise answer
        combined_info = " ".join(key_info[:2])  # Top 2 snippets

        if len(combined_info) > 300:
            combined_info = combined_info[:297] + "..."

        return combined_info

    def _calculate_confidence(self, results: List[SearchResult]) -> str:
        """Calculate confidence level"""
        if not results:
            return "LOW"

        high_score_count = len([r for r in results if r.score > 0.7])
        medium_score_count = len([r for r in results if 0.4 <= r.score <= 0.7])

        if high_score_count >= 2:
            return "HIGH"
        elif high_score_count >= 1 or medium_score_count >= 3:
            return "MEDIUM"
        else:
            return "LOW"
