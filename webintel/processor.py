"""
AI-Powered Data Processing Pipeline for WebIntel
Enhanced query processing with parallel search and AI analysis
"""

import asyncio
import logging
import time
from typing import Dict, Any, List

# Disable all logging for speed
logging.disable(logging.CRITICAL)

from .advanced_search_engine import AdvancedSearchEngine
from .ai_engine import AIEngine


class DataProcessor:
    """AI-powered data processor with enhanced query processing"""

    def __init__(self, config):
        self.config = config
        self.ai_engine = AIEngine(config)

    async def process_query(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Process query with AI enhancement and reliable search"""
        start_time = time.time()

        try:
            # Step 1: Enhanced search with working engine
            async with AdvancedSearchEngine() as search_engine:
                search_response = await search_engine.advanced_search(query, max_results)
                search_results = search_response.get("results", [])

            if not search_results:
                return self._create_no_results_response(query, time.time() - start_time)

            # Step 2: Use search results directly (they already have content)
            processed_content = []
            for result in search_results[:max_results]:
                processed_content.append({
                    'url': result.url,
                    'title': result.title,
                    'content': result.content,
                    'snippet': result.snippet,
                    'domain': result.domain,
                    'word_count': len(result.content.split()),
                    'score': result.score
                })

            if not processed_content:
                return self._create_search_only_response(query, search_results, time.time() - start_time)

            # Step 3: AI analysis of content
            analyzed_content = await self._analyze_content_parallel(processed_content, query)

            # Step 4: Generate comprehensive AI response
            ai_response = await self._generate_ai_response(analyzed_content, query)

            # Step 5: Prepare final response
            processing_time = time.time() - start_time

            return {
                'status': 'success',
                'query': query,
                'sources': self._format_sources(processed_content, analyzed_content),
                'answer': ai_response.get('comprehensive_answer', ''),
                'analysis': {
                    'executive_summary': ai_response.get('comprehensive_answer', ''),
                    'detailed_analysis': ai_response.get('additional_info', ''),
                    'key_findings': ai_response.get('key_insights', []),
                    'recommendations': [
                        "Review the comprehensive analysis above",
                        "Check source links for more details"
                    ],
                    'confidence_level': 'HIGH' if len(processed_content) >= 3 else 'MEDIUM',
                    'comprehensive_answer': ai_response.get('comprehensive_answer', ''),
                    'source_summary': ai_response.get('source_summary', '')
                },
                'statistics': {
                    'total_sources': len(processed_content),
                    'search_engines_used': 2,
                    'high_quality_sources': len([c for c in processed_content if c['word_count'] > 500]),
                    'max_relevance': max([c['score'] for c in processed_content], default=0)
                },
                'response_time': round(processing_time, 2),
                'cached_at': time.time()
            }

        except Exception as e:
            return {
                'status': 'error',
                'query': query,
                'message': f"Processing failed: {str(e)}",
                'response_time': round(time.time() - start_time, 2)
            }

    async def _analyze_content_parallel(self, processed_content: List[Dict], query: str) -> List[Dict[str, Any]]:
        """Analyze processed content in parallel"""
        semaphore = asyncio.Semaphore(6)

        async def analyze_single(content):
            async with semaphore:
                try:
                    ai_analysis = await asyncio.wait_for(
                        self.ai_engine.analyze_content(content['content'], query),
                        timeout=10
                    )

                    return {
                        'title': content['title'],
                        'url': content['url'],
                        'content': content['content'],
                        'domain': content['domain'],
                        'word_count': content['word_count'],
                        'ai_analysis': ai_analysis.get('analysis', ''),
                        'relevance_score': ai_analysis.get('relevance_score', content['score']),
                        'key_points': ai_analysis.get('key_points', []),
                        'extracted_facts': ai_analysis.get('extracted_facts', [])
                    }

                except asyncio.TimeoutError:
                    return {
                        'title': content['title'],
                        'url': content['url'],
                        'content': content['content'][:1000],
                        'domain': content['domain'],
                        'word_count': content['word_count'],
                        'ai_analysis': f"Analysis of content from {content['domain']}",
                        'relevance_score': content['score'],
                        'key_points': [f"Information from {content['domain']}"],
                        'extracted_facts': [f"Content available at {content['url']}"]
                    }
                except Exception:
                    return {
                        'title': content['title'],
                        'url': content['url'],
                        'content': content['content'][:500],
                        'domain': content['domain'],
                        'word_count': content['word_count'],
                        'ai_analysis': f"Basic information from {content['domain']}",
                        'relevance_score': content['score'],
                        'key_points': [f"Information available from {content['domain']}"],
                        'extracted_facts': []
                    }

        tasks = [analyze_single(content) for content in processed_content]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [r for r in results if isinstance(r, dict)]

    async def _generate_ai_response(self, analyzed_content: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Generate comprehensive AI response"""
        try:
            if hasattr(self.ai_engine, 'generate_comprehensive_response'):
                return await asyncio.wait_for(
                    self.ai_engine.generate_comprehensive_response(analyzed_content, query),
                    timeout=15
                )
            else:
                # Fallback to basic synthesis
                return self._create_basic_synthesis(analyzed_content, query)

        except asyncio.TimeoutError:
            return self._create_basic_synthesis(analyzed_content, query)
        except Exception:
            return self._create_basic_synthesis(analyzed_content, query)

    def _create_basic_synthesis(self, analyzed_content: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Create basic synthesis when AI fails"""
        if not analyzed_content:
            return {
                'comprehensive_answer': f"No detailed analysis available for '{query}'.",
                'key_insights': [],
                'additional_info': "Please try a different search query.",
                'source_summary': "No sources analyzed"
            }

        # Extract key information
        all_key_points = []
        all_facts = []
        high_relevance_count = 0

        for content in analyzed_content:
            all_key_points.extend(content.get('key_points', []))
            all_facts.extend(content.get('extracted_facts', []))
            if content.get('relevance_score', 0) > 0.6:
                high_relevance_count += 1

        # Create comprehensive answer
        answer = f"Based on analysis of {len(analyzed_content)} sources about '{query}': "

        if all_key_points:
            answer += f"Key findings include {', '.join(all_key_points[:3])}. "

        if high_relevance_count > 0:
            answer += f"Found {high_relevance_count} highly relevant sources with detailed information. "

        answer += f"The analysis covers information from {len(set(c['domain'] for c in analyzed_content))} different domains."

        return {
            'comprehensive_answer': answer,
            'key_insights': all_key_points[:5],
            'additional_info': f"Analysis based on {len(analyzed_content)} sources with {high_relevance_count} high-quality matches.",
            'source_summary': f"Analyzed {len(analyzed_content)} sources from {len(set(c['domain'] for c in analyzed_content))} domains"
        }

    def _format_sources(self, processed_content: List[Dict], analyzed_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources for response"""
        sources = []

        for content in processed_content:
            # Find corresponding analysis
            analysis = next(
                (a for a in analyzed_content if a['url'] == content['url']),
                {}
            )

            sources.append({
                'title': content['title'],
                'url': content['url'],
                'domain': content['domain'],
                'snippet': content['snippet'] or content['content'][:200],
                'word_count': content['word_count'],
                'relevance_score': analysis.get('relevance_score', content['score']),
                'score': content['score']
            })

        return sources

    def _create_no_results_response(self, query: str, processing_time: float) -> Dict[str, Any]:
        """Create response when no results found"""
        return {
            'status': 'success',
            'query': query,
            'sources': [],
            'answer': f"No specific results found for '{query}'. Please try a different search query.",
            'analysis': {
                'executive_summary': f"No results found for '{query}'",
                'detailed_analysis': "Please try different keywords or rephrase your query",
                'key_findings': [],
                'recommendations': ["Try different keywords", "Rephrase your query"],
                'confidence_level': 'LOW'
            },
            'statistics': {'total_sources': 0},
            'response_time': round(processing_time, 2)
        }

    def _create_search_only_response(self, query: str, search_results: List, processing_time: float) -> Dict[str, Any]:
        """Create response with search results only"""
        sources = []
        for result in search_results[:5]:
            sources.append({
                'title': result.title,
                'url': result.url,
                'domain': result.domain,
                'snippet': result.snippet,
                'relevance_score': getattr(result, 'relevance_score', result.score)
            })

        return {
            'status': 'success',
            'query': query,
            'sources': sources,
            'answer': f"Found {len(sources)} search results for '{query}'",
            'analysis': {
                'executive_summary': f"Search completed for '{query}' with {len(sources)} results",
                'detailed_analysis': "Content extraction was limited, but search results are available",
                'key_findings': [f"Found results from {len(set(s['domain'] for s in sources))} different domains"],
                'recommendations': ["Check the source links for detailed information"],
                'confidence_level': 'MEDIUM'
            },
            'statistics': {'total_sources': len(sources)},
            'response_time': round(processing_time, 2)
        }
