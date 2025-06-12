"""
Google Gemini 2.0 Flash AI Engine for WebIntel
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

# Disable all logging
logging.disable(logging.CRITICAL)
from .config import Config
from .utils import clean_text

logger = logging.getLogger(__name__)

class AIEngine:
    """Google Gemini 2.0 Flash AI Engine"""

    def __init__(self, config: Config):
        self.config = config
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Gemini model"""
        try:
            if not self.config.gemini.api_key:
                raise ValueError("Gemini API key is required")

            genai.configure(api_key=self.config.gemini.api_key)
            
            # Ultra-fast generation settings
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=2048,  # Reduced for speed
                temperature=0.3,  # Lower for faster, more focused responses
                top_p=0.8,
                top_k=20,  # Reduced for speed
            )
            
            # Initialize model
            self.model = genai.GenerativeModel(
                model_name=self.config.gemini.model_name,
                generation_config=generation_config,
            )

            logger.info(f"Initialized Gemini model: {self.config.gemini.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def analyze_content(self, content: str, query: str) -> Dict[str, Any]:
        """Analyze web content using Gemini AI"""
        try:
            prompt = self._build_analysis_prompt(content, query)
            
            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            if not response.text:
                logger.warning("Empty response from Gemini")
                return {"analysis": "No analysis available", "relevance_score": 0.0}
            
            # Parse structured response
            return self._parse_analysis_response(response.text)
            
        except Exception as e:
            logger.error(f"Error analyzing content with Gemini: {e}")
            return {"analysis": f"Analysis failed: {str(e)}", "relevance_score": 0.0}
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def synthesize_information(self, analyzed_contents: List[Dict[str, Any]], 
                                   query: str) -> Dict[str, Any]:
        """Synthesize information from multiple sources"""
        try:
            prompt = self._build_synthesis_prompt(analyzed_contents, query)
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            if not response.text:
                logger.warning("Empty synthesis response from Gemini")
                return {"summary": "No synthesis available", "key_points": []}
            
            return self._parse_synthesis_response(response.text)
            
        except Exception as e:
            logger.error(f"Error synthesizing information: {e}")
            return {"summary": f"Synthesis failed: {str(e)}", "key_points": []}

    async def synthesize_information_enhanced(self, analyzed_contents: List[Dict[str, Any]],
                                            original_query: str, enhanced_query: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced synthesis with query context"""
        try:
            prompt = self._build_enhanced_synthesis_prompt(analyzed_contents, original_query, enhanced_query)

            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )

            if not response.text:
                logger.warning("Empty enhanced synthesis response from Gemini")
                return {"summary": "No synthesis available", "key_points": []}

            return self._parse_synthesis_response(response.text)

        except Exception as e:
            logger.error(f"Error in enhanced synthesis: {e}")
            return {"summary": f"Enhanced synthesis failed: {str(e)}", "key_points": []}

    def _build_enhanced_synthesis_prompt(self, analyzed_contents: List[Dict[str, Any]],
                                       original_query: str, enhanced_query: Dict[str, Any]) -> str:
        """Build enhanced synthesis prompt with query context"""
        sources_text = ""
        for i, content in enumerate(analyzed_contents[:12], 1):  # Increased limit
            sources_text += f"\nSOURCE {i} (Relevance: {content.get('relevance_score', 0.0):.2f}):\n"
            sources_text += f"URL: {content.get('url', 'Unknown')}\n"
            sources_text += f"Domain: {content.get('domain', 'Unknown')}\n"
            sources_text += f"Title: {content.get('title', 'No title')}\n"
            sources_text += f"Analysis: {content.get('analysis', 'No analysis')}\n"
            sources_text += f"Key Points: {', '.join(content.get('key_points', []))}\n"
            sources_text += f"Facts: {', '.join(content.get('extracted_facts', []))}\n"
            sources_text += "---\n"

        query_context = f"""
ORIGINAL QUERY: {original_query}
ENHANCED QUERY: {enhanced_query.get('primary_query', original_query)}
QUERY TYPE: {enhanced_query.get('query_type', 'general')}
SEARCH KEYWORDS: {', '.join(enhanced_query.get('search_keywords', []))}
ALTERNATIVE QUERIES: {', '.join(enhanced_query.get('alternative_queries', []))}
"""

        prompt = f"""
You are an expert research synthesizer and information analyst. Based on the analyzed web content from multiple sources,
provide a comprehensive and actionable synthesis for the user's query.

{query_context}

ANALYZED SOURCES ({len(analyzed_contents)} total):
{sources_text}

Please provide a comprehensive synthesis in the following format:

EXECUTIVE_SUMMARY:
[Provide a clear, concise 2-3 sentence summary that directly answers the user's query. Focus on the most important findings and actionable insights.]

DETAILED_ANALYSIS:
[Provide a thorough analysis that synthesizes information from all sources. Organize by themes or topics. Include specific details, examples, and evidence from the sources. Make connections between different sources and highlight consensus or disagreements.]

KEY_FINDINGS:
1. [Most important finding with supporting evidence from sources - include source numbers]
2. [Second most important finding with supporting evidence - include source numbers]
3. [Third most important finding with supporting evidence - include source numbers]
4. [Additional findings as relevant]

RECOMMENDATIONS:
- [Specific, actionable recommendation based on the findings]
- [Second recommendation with practical steps]
- [Third recommendation for further learning or action]
- [Additional recommendations as relevant]

CONFIDENCE_LEVEL: [HIGH/MEDIUM/LOW based on source quality, consistency, and relevance scores]

ADDITIONAL_INSIGHTS:
[Any additional valuable insights, trends, or patterns discovered during analysis]

Guidelines for synthesis:
- Prioritize information from higher relevance sources
- Provide specific examples and evidence
- Make the synthesis actionable and practical
- Address the user's intent behind the query
- Highlight any important caveats or limitations
- Organize information logically and clearly
- Include quantitative data when available
- Connect related concepts across sources
"""
        return prompt
    
    def _build_analysis_prompt(self, content: str, query: str) -> str:
        """Build optimized prompt for fast content analysis"""
        # Truncate content for ultra-fast processing
        content = content[:2000] if len(content) > 2000 else content  # Ultra-fast processing

        prompt = f"""
You are an expert information analyst. Analyze the following web content in relation to the user's query.

USER QUERY: {query}

WEB CONTENT:
{content}

Please provide a structured analysis in the following format:

RELEVANCE_SCORE: [Provide a score from 0.0 to 1.0 where:
- 0.8-1.0: Highly relevant, directly addresses the query
- 0.6-0.7: Moderately relevant, contains useful related information
- 0.4-0.5: Somewhat relevant, tangentially related
- 0.2-0.3: Minimally relevant, mentions query topics briefly
- 0.0-0.1: Not relevant, unrelated content]

ANALYSIS:
[Provide a detailed analysis explaining how this content relates to the user's query. Be specific about what information is useful and why.]

KEY_POINTS:
- [Extract 3-5 key points that are most relevant to the query]
- [Focus on actionable information and important facts]
- [Include specific details, numbers, or examples when available]

EXTRACTED_FACTS:
- [List 3-5 concrete facts from the content]
- [Include dates, statistics, names, or specific claims]
- [Focus on verifiable information]

Be generous with relevance scoring if the content contains any useful information related to the query, even if not perfectly aligned.
"""
        return prompt
    
    def _build_synthesis_prompt(self, analyzed_contents: List[Dict[str, Any]], 
                               query: str) -> str:
        """Build prompt for information synthesis"""
        sources_text = ""
        for i, content in enumerate(analyzed_contents[:6], 1):  # Limit to top 6 sources for speed
            sources_text += f"\nSOURCE {i}:\n"
            sources_text += f"Relevance: {content.get('relevance_score', 0.0)}\n"
            sources_text += f"Analysis: {content.get('analysis', 'No analysis')}\n"
            sources_text += f"Key Points: {', '.join(content.get('key_points', []))}\n"
            sources_text += "---\n"
        
        prompt = f"""
You are an expert research synthesizer. Based on the analyzed web content from multiple sources, 
provide a comprehensive synthesis for the user's query.

USER QUERY: {query}

ANALYZED SOURCES:
{sources_text}

Please provide a comprehensive synthesis in the following format:

EXECUTIVE_SUMMARY:
[2-3 sentence summary of the key findings]

DETAILED_ANALYSIS:
[Comprehensive analysis synthesizing information from all sources]

KEY_FINDINGS:
1. [Finding 1 with supporting evidence]
2. [Finding 2 with supporting evidence]
3. [Finding 3 with supporting evidence]

RECOMMENDATIONS:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]

CONFIDENCE_LEVEL: [HIGH/MEDIUM/LOW based on source quality and consistency]

Focus on accuracy, comprehensiveness, and providing actionable insights.
"""
        return prompt
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured analysis response"""
        try:
            result = {
                "relevance_score": 0.0,
                "analysis": "",
                "key_points": [],
                "extracted_facts": []
            }
            
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith("RELEVANCE_SCORE:"):
                    try:
                        score_text = line.split(":", 1)[1].strip()
                        result["relevance_score"] = float(score_text)
                    except (ValueError, IndexError):
                        result["relevance_score"] = 0.5
                
                elif line.startswith("ANALYSIS:"):
                    current_section = "analysis"
                    result["analysis"] = line.split(":", 1)[1].strip()
                
                elif line.startswith("KEY_POINTS:"):
                    current_section = "key_points"
                
                elif line.startswith("EXTRACTED_FACTS:"):
                    current_section = "extracted_facts"
                
                elif line.startswith("- ") and current_section:
                    point = line[2:].strip()
                    if current_section == "key_points":
                        result["key_points"].append(point)
                    elif current_section == "extracted_facts":
                        result["extracted_facts"].append(point)
                
                elif current_section == "analysis" and line and not line.startswith(("KEY_POINTS:", "EXTRACTED_FACTS:")):
                    result["analysis"] += " " + line
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing analysis response: {e}")
            return {
                "relevance_score": 0.0,
                "analysis": response_text,
                "key_points": [],
                "extracted_facts": []
            }
    
    def _parse_synthesis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured synthesis response"""
        try:
            result = {
                "executive_summary": "",
                "detailed_analysis": "",
                "key_findings": [],
                "recommendations": [],
                "confidence_level": "MEDIUM"
            }
            
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith("EXECUTIVE_SUMMARY:"):
                    current_section = "executive_summary"
                    result["executive_summary"] = line.split(":", 1)[1].strip()
                
                elif line.startswith("DETAILED_ANALYSIS:"):
                    current_section = "detailed_analysis"
                    result["detailed_analysis"] = line.split(":", 1)[1].strip()
                
                elif line.startswith("KEY_FINDINGS:"):
                    current_section = "key_findings"
                
                elif line.startswith("RECOMMENDATIONS:"):
                    current_section = "recommendations"
                
                elif line.startswith("CONFIDENCE_LEVEL:"):
                    result["confidence_level"] = line.split(":", 1)[1].strip()
                
                elif line.startswith(("1. ", "2. ", "3. ")) and current_section == "key_findings":
                    result["key_findings"].append(line[3:].strip())
                
                elif line.startswith("- ") and current_section == "recommendations":
                    result["recommendations"].append(line[2:].strip())
                
                elif current_section in ["executive_summary", "detailed_analysis"] and line:
                    if not line.startswith(("DETAILED_ANALYSIS:", "KEY_FINDINGS:", "RECOMMENDATIONS:", "CONFIDENCE_LEVEL:")):
                        result[current_section] += " " + line
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing synthesis response: {e}")
            return {
                "executive_summary": response_text[:200] + "...",
                "detailed_analysis": response_text,
                "key_findings": [],
                "recommendations": [],
                "confidence_level": "LOW"
            }

    async def generate_comprehensive_response(self, analyzed_contents: List[Dict[str, Any]],
                                            query: str) -> Dict[str, Any]:
        """Generate comprehensive AI response like ChatGPT"""
        try:
            # Build comprehensive sources text
            sources_text = ""
            for i, content in enumerate(analyzed_contents[:8], 1):
                sources_text += f"\nSOURCE {i}:\n"
                sources_text += f"Title: {content.get('title', 'No title')}\n"
                sources_text += f"URL: {content.get('url', 'Unknown')}\n"
                sources_text += f"Content: {content.get('content', '')[:800]}...\n"
                sources_text += f"Key Points: {', '.join(content.get('key_points', []))}\n"
                sources_text += "---\n"

            prompt = f"""
You are an advanced AI assistant with access to real-time web information. A user has asked: "{query}"

Based on the following web sources, provide a comprehensive, natural, and helpful response:

{sources_text}

Instructions:
1. Understand the user's intent and provide a complete, detailed answer
2. Use natural, conversational language like ChatGPT
3. Include specific facts, dates, numbers, prices from the sources
4. Organize information logically with clear structure
5. Provide actionable insights and recommendations
6. If the user asks for comparison, analysis, or explanation, do that thoroughly
7. Be comprehensive and detailed - give full information, not brief summaries
8. Include source attribution naturally in the text
9. For cryptocurrency queries, include current prices, market trends, and analysis
10. For news queries, include dates, specific events, and context
11. For technical queries, provide detailed explanations and examples

Respond in this format:

COMPREHENSIVE_ANSWER:
[Provide a detailed, comprehensive response (at least 200-300 words) that fully addresses the user's query. Write like you're having a conversation with the user. Include specific information from the sources, dates, facts, prices, and insights. Make it comprehensive, informative, and helpful. Don't just summarize - provide analysis and context.]

KEY_INSIGHTS:
- [Important insight 1 with specific details, numbers, dates]
- [Important insight 2 with specific details, numbers, dates]
- [Important insight 3 with specific details, numbers, dates]
- [Important insight 4 with specific details, numbers, dates]

ADDITIONAL_INFO:
[Any additional relevant information, context, recommendations, or analysis that would be helpful to the user. Include market trends, future outlook, or related topics.]

SOURCE_SUMMARY:
[Brief summary of the sources used, their reliability, and what type of information they provided]
"""

            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )

            if not response.text:
                # NO FALLBACK - Return error if no real AI response
                raise Exception("AI model returned empty response")

            return self._parse_comprehensive_response(response.text)

        except Exception as e:
            logger.error(f"Error generating comprehensive response: {e}")
            # NO FALLBACK - Raise error instead of generating fake content
            raise Exception(f"Failed to generate AI response: {e}")

    def _parse_comprehensive_response(self, response_text: str) -> Dict[str, Any]:
        """Parse comprehensive AI response"""
        try:
            result = {
                "comprehensive_answer": "",
                "key_insights": [],
                "additional_info": "",
                "source_summary": ""
            }

            lines = response_text.split('\n')
            current_section = None

            for line in lines:
                line = line.strip()

                if line.startswith("COMPREHENSIVE_ANSWER:"):
                    current_section = "comprehensive_answer"
                    result["comprehensive_answer"] = line.split(":", 1)[1].strip()

                elif line.startswith("KEY_INSIGHTS:"):
                    current_section = "key_insights"

                elif line.startswith("ADDITIONAL_INFO:"):
                    current_section = "additional_info"
                    result["additional_info"] = line.split(":", 1)[1].strip()

                elif line.startswith("SOURCE_SUMMARY:"):
                    current_section = "source_summary"
                    result["source_summary"] = line.split(":", 1)[1].strip()

                elif line.startswith("- ") and current_section == "key_insights":
                    result["key_insights"].append(line[2:].strip())

                elif current_section in ["comprehensive_answer", "additional_info", "source_summary"] and line:
                    if not line.startswith(("KEY_INSIGHTS:", "ADDITIONAL_INFO:", "SOURCE_SUMMARY:")):
                        result[current_section] += " " + line

            return result

        except Exception as e:
            logger.error(f"Error parsing comprehensive response: {e}")
            return {
                "comprehensive_answer": response_text,
                "key_insights": [],
                "additional_info": "",
                "source_summary": ""
            }

    # REMOVED: No more fallback responses
    # WebIntel now only returns real AI analysis of real web content
