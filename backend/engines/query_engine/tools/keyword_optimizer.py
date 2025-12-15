"""
QueryEngine Keyword Optimizer
"""
import json
import logging
from typing import Dict, List, Optional, Any, Tuple

from ..llms.base import LLMClient
from ..utils.config import query_config

logger = logging.getLogger(__name__)

class KeywordOptimizer:
    """Keyword optimizer for QueryEngine"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.config = query_config
    
    async def optimize_query(
        self,
        query: str,
        optimization_type: str = "keyword",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize a query for better search results"""
        try:
            if optimization_type == "keyword":
                return await self._optimize_keywords(query, context)
            elif optimization_type == "semantic":
                return await self._optimize_semantic(query, context)
            elif optimization_type == "structure":
                return await self._optimize_structure(query, context)
            elif optimization_type == "comprehensive":
                return await self._optimize_comprehensive(query, context)
            else:
                raise ValueError(f"Unknown optimization type: {optimization_type}")
                
        except Exception as e:
            logger.error(f"Error optimizing query: {str(e)}")
            raise
    
    async def _optimize_keywords(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize query keywords"""
        try:
            system_prompt = """
            You are a keyword optimization expert. Analyze the given query and optimize it for better search results.
            
            Return a JSON object with the following structure:
            {
                "optimized_query": "the optimized query",
                "original_query": "the original query",
                "optimization_type": "keyword",
                "improvements": ["list", "of", "improvements"],
                "confidence_score": 0.95,
                "additional_suggestions": ["alternative", "queries"],
                "metadata": {
                    "keyword_density": 0.8,
                    "query_length": "short|medium|long",
                    "specificity": "low|medium|high",
                    "removed_stopwords": ["list", "of", "removed", "stopwords"],
                    "added_keywords": ["list", "of", "added", "keywords"],
                    "keyword_synonyms": {"original": ["synonym1", "synonym2"]}
                }
            }
            """
            
            context_str = ""
            if context:
                context_str = f"\nContext: {json.dumps(context, indent=2)}"
            
            prompt = f"""
            Optimize this query for better search results: {query}
            {context_str}
            
            Focus on:
            1. Removing unnecessary stop words
            2. Adding relevant keywords
            3. Improving keyword specificity
            4. Maintaining the original intent
            5. Using industry-standard terminology
            """
            
            return await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            logger.error(f"Error optimizing keywords: {str(e)}")
            raise
    
    async def _optimize_semantic(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize query semantics"""
        try:
            system_prompt = """
            You are a semantic optimization expert. Analyze the given query and optimize it for better semantic understanding.
            
            Return a JSON object with the following structure:
            {
                "optimized_query": "the semantically optimized query",
                "original_query": "the original query",
                "optimization_type": "semantic",
                "improvements": ["list", "of", "semantic", "improvements"],
                "confidence_score": 0.95,
                "additional_suggestions": ["semantically", "equivalent", "queries"],
                "metadata": {
                    "semantic_similarity": 0.9,
                    "intent_clarity": "high|medium|low",
                    "ambiguity_reduction": "high|medium|low",
                    "concept_expansion": ["expanded", "concepts"],
                    "contextual_terms": ["contextually", "relevant", "terms"]
                }
            }
            """
            
            context_str = ""
            if context:
                context_str = f"\nContext: {json.dumps(context, indent=2)}"
            
            prompt = f"""
            Optimize this query semantically for better understanding: {query}
            {context_str}
            
            Focus on:
            1. Clarifying ambiguous terms
            2. Expanding relevant concepts
            3. Improving intent clarity
            4. Adding contextual terms
            5. Reducing semantic ambiguity
            """
            
            return await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            logger.error(f"Error optimizing semantics: {str(e)}")
            raise
    
    async def _optimize_structure(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize query structure"""
        try:
            system_prompt = """
            You are a query structure optimization expert. Analyze the given query and optimize its structure for better search results.
            
            Return a JSON object with the following structure:
            {
                "optimized_query": "the structurally optimized query",
                "original_query": "the original query",
                "optimization_type": "structure",
                "improvements": ["list", "of", "structural", "improvements"],
                "confidence_score": 0.95,
                "additional_suggestions": ["structurally", "optimized", "alternatives"],
                "metadata": {
                    "query_structure": "boolean|phrase|fuzzy|proximity",
                    "operator_usage": "high|medium|low",
                    "parentheses_balance": true,
                    "quote_usage": "appropriate|missing|excessive",
                    "boolean_operators": ["AND", "OR", "NOT"],
                    "proximity_terms": ["NEAR", "ADJ"]
                }
            }
            """
            
            context_str = ""
            if context:
                context_str = f"\nContext: {json.dumps(context, indent=2)}"
            
            prompt = f"""
            Optimize this query structure for better search results: {query}
            {context_str}
            
            Focus on:
            1. Adding appropriate boolean operators
            2. Using quotes for exact phrases
            3. Implementing proximity operators
            4. Balancing parentheses
            5. Structuring complex queries logically
            """
            
            return await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            logger.error(f"Error optimizing structure: {str(e)}")
            raise
    
    async def _optimize_comprehensive(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Comprehensive query optimization"""
        try:
            # Get individual optimizations
            keyword_result = await self._optimize_keywords(query, context)
            semantic_result = await self._optimize_semantic(query, context)
            structure_result = await self._optimize_structure(query, context)
            
            # Combine optimizations
            system_prompt = """
            You are a comprehensive query optimization expert. Combine the results of keyword, semantic, and structural optimizations
            to create the best possible optimized query.
            
            Return a JSON object with the following structure:
            {
                "optimized_query": "the comprehensively optimized query",
                "original_query": "the original query",
                "optimization_type": "comprehensive",
                "improvements": ["list", "of", "comprehensive", "improvements"],
                "confidence_score": 0.95,
                "additional_suggestions": ["comprehensively", "optimized", "alternatives"],
                "metadata": {
                    "keyword_optimizations": "summary of keyword improvements",
                    "semantic_optimizations": "summary of semantic improvements",
                    "structural_optimizations": "summary of structural improvements",
                    "overall_quality": "excellent|good|fair|poor",
                    "optimization_balance": "well-balanced|keyword-focused|semantic-focused|structure-focused"
                }
            }
            """
            
            prompt = f"""
            Original Query: {query}
            
            Keyword Optimization Result:
            {json.dumps(keyword_result, indent=2)}
            
            Semantic Optimization Result:
            {json.dumps(semantic_result, indent=2)}
            
            Structural Optimization Result:
            {json.dumps(structure_result, indent=2)}
            
            Combine these optimizations to create the best possible query that incorporates the strengths of each approach.
            """
            
            return await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            logger.error(f"Error in comprehensive optimization: {str(e)}")
            raise
    
    async def extract_keywords(
        self,
        query: str,
        max_keywords: int = 10
    ) -> List[str]:
        """Extract keywords from query"""
        try:
            system_prompt = f"""
            You are a keyword extraction expert. Extract the most important keywords from the given query.
            Return exactly {max_keywords} keywords in order of importance.
            
            Return a JSON object with the following structure:
            {{
                "keywords": ["keyword1", "keyword2", "keyword3", ...],
                "relevance_scores": [0.9, 0.8, 0.7, ...]
            }}
            """
            
            prompt = f"""
            Extract the {max_keywords} most important keywords from this query: {query}
            
            Focus on:
            1. Nouns and proper nouns
            2. Industry-specific terms
            3. Action verbs
            4. Descriptive adjectives
            5. Avoiding stop words
            """
            
            response = await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            return response.get("keywords", [])
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            raise
    
    async def generate_query_variations(
        self,
        query: str,
        num_variations: int = 5,
        variation_type: str = "synonym"
    ) -> List[str]:
        """Generate query variations"""
        try:
            system_prompt = f"""
            You are a query variation expert. Generate {num_variations} variations of the given query.
            The variation type is: {variation_type}
            
            Return a JSON object with the following structure:
            {{
                "variations": ["variation1", "variation2", "variation3", ...],
                "variation_type": "{variation_type}",
                "rationale": "explanation of variation approach"
            }}
            """
            
            prompt = f"""
            Generate {num_variations} variations of this query: {query}
            
            Variation type: {variation_type}
            
            For synonym variations: replace key terms with synonyms
            For structural variations: change the query structure
            For semantic variations: maintain meaning with different wording
            For expansion variations: add related concepts
            For simplification variations: make the query more concise
            """
            
            response = await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            return response.get("variations", [])
            
        except Exception as e:
            logger.error(f"Error generating query variations: {str(e)}")
            raise
    
    async def analyze_query_quality(
        self,
        query: str
    ) -> Dict[str, Any]:
        """Analyze query quality"""
        try:
            system_prompt = """
            You are a query quality analysis expert. Analyze the quality of the given query.
            
            Return a JSON object with the following structure:
            {
                "quality_score": 0.85,
                "quality_rating": "excellent|good|fair|poor",
                "strengths": ["strength1", "strength2", "strength3"],
                "weaknesses": ["weakness1", "weakness2", "weakness3"],
                "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
                "metadata": {
                    "length_appropriateness": "appropriate|too_short|too_long",
                    "specificity_level": "high|medium|low",
                    "ambiguity_level": "low|medium|high",
                    "searchability": "high|medium|low"
                }
            }
            """
            
            prompt = f"""
            Analyze the quality of this query: {query}
            
            Consider:
            1. Clarity and specificity
            2. Appropriate length
            3. Use of relevant terminology
            4. Presence of ambiguity
            5. Searchability
            """
            
            return await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            logger.error(f"Error analyzing query quality: {str(e)}")
            raise