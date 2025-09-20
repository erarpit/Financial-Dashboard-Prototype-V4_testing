import logging
import re
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from models.schemas import MarketSentiment, NewsAnalysis

logger = logging.getLogger(__name__)

class AISentimentAnalyzer:
    """Advanced AI-powered sentiment analysis for financial news and market data"""
    
    def __init__(self):
        self.financial_lexicon = self._build_financial_lexicon()
        self.impact_weights = self._build_impact_weights()
        self.sector_keywords = self._build_sector_keywords()
    
    def analyze_text_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze sentiment of text using AI-powered approach"""
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Calculate sentiment scores
            positive_score = self._calculate_sentiment_score(processed_text, 'positive')
            negative_score = self._calculate_sentiment_score(processed_text, 'negative')
            
            # Apply intensifiers and negators
            positive_score = self._apply_intensifiers(processed_text, positive_score)
            negative_score = self._apply_intensifiers(processed_text, negative_score)
            
            # Calculate final sentiment
            net_score = positive_score - negative_score
            confidence = min(abs(net_score), 1.0)
            
            if net_score > 0.1:
                return "POSITIVE", confidence
            elif net_score < -0.1:
                return "NEGATIVE", confidence
            else:
                return "NEUTRAL", 0.0
                
        except Exception as e:
            logger.error(f"Error in text sentiment analysis: {str(e)}")
            return "NEUTRAL", 0.0
    
    def analyze_advanced_sentiment(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Advanced sentiment analysis with detailed metrics"""
        try:
            processed_text = self._preprocess_text(text)
            
            # Basic sentiment analysis
            positive_score = self._calculate_sentiment_score(processed_text, 'positive')
            negative_score = self._calculate_sentiment_score(processed_text, 'negative')
            
            # Apply intensifiers and negators
            positive_score = self._apply_intensifiers(processed_text, positive_score)
            negative_score = self._apply_intensifiers(processed_text, negative_score)
            
            # Calculate metrics
            net_score = positive_score - negative_score
            magnitude = abs(positive_score) + abs(negative_score)
            confidence = min(abs(net_score), 1.0)
            
            # Determine sentiment
            if net_score > 0.1:
                sentiment = "POSITIVE"
            elif net_score < -0.1:
                sentiment = "NEGATIVE"
            else:
                sentiment = "NEUTRAL"
            
            # Extract keywords
            keywords = self._extract_sentiment_keywords(processed_text)
            
            # Calculate context impact
            context_impact = self._calculate_context_impact(text, context) if context else 0.0
            
            # Analyze emotions
            emotions = self._analyze_emotions(processed_text)
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "score": net_score,
                "magnitude": magnitude,
                "emotions": emotions,
                "keywords": keywords,
                "context_impact": context_impact,
                "positive_score": positive_score,
                "negative_score": negative_score
            }
            
        except Exception as e:
            logger.error(f"Error in advanced sentiment analysis: {str(e)}")
            return {
                "sentiment": "NEUTRAL",
                "confidence": 0.0,
                "score": 0.0,
                "magnitude": 0.0,
                "emotions": {},
                "keywords": [],
                "context_impact": 0.0,
                "error": str(e)
            }
    
    def analyze_market_sentiment(self, news_items: List[Dict[str, Any]]) -> MarketSentiment:
        """Analyze overall market sentiment from multiple news items"""
        try:
            if not news_items:
                return MarketSentiment(
                    overall_sentiment="NEUTRAL",
                    sentiment_score=0.0,
                    confidence=0.0,
                    news_count=0,
                    positive_ratio=0.0,
                    negative_ratio=0.0,
                    neutral_ratio=1.0,
                    last_updated=datetime.now().isoformat()
                )
            
            sentiments = []
            total_confidence = 0.0
            
            for item in news_items:
                text = item.get('title', '') + ' ' + item.get('content', '')
                sentiment, confidence = self.analyze_text_sentiment(text)
                sentiments.append(sentiment)
                total_confidence += confidence
            
            # Calculate ratios
            positive_count = sentiments.count('POSITIVE')
            negative_count = sentiments.count('NEGATIVE')
            neutral_count = sentiments.count('NEUTRAL')
            total_count = len(sentiments)
            
            positive_ratio = positive_count / total_count
            negative_ratio = negative_count / total_count
            neutral_ratio = neutral_count / total_count
            
            # Calculate overall sentiment score
            sentiment_scores = []
            for item in news_items:
                text = item.get('title', '') + ' ' + item.get('content', '')
                result = self.analyze_advanced_sentiment(text)
                sentiment_scores.append(result['score'])
            
            overall_score = np.mean(sentiment_scores) if sentiment_scores else 0.0
            avg_confidence = total_confidence / total_count if total_count > 0 else 0.0
            
            # Determine overall sentiment
            if overall_score > 0.1:
                overall_sentiment = "POSITIVE"
            elif overall_score < -0.1:
                overall_sentiment = "NEGATIVE"
            else:
                overall_sentiment = "NEUTRAL"
            
            return MarketSentiment(
                overall_sentiment=overall_sentiment,
                sentiment_score=overall_score,
                confidence=avg_confidence,
                news_count=total_count,
                positive_ratio=positive_ratio,
                negative_ratio=negative_ratio,
                neutral_ratio=neutral_ratio,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error in market sentiment analysis: {str(e)}")
            return MarketSentiment(
                overall_sentiment="NEUTRAL",
                sentiment_score=0.0,
                confidence=0.0,
                news_count=len(news_items),
                positive_ratio=0.0,
                negative_ratio=0.0,
                neutral_ratio=1.0,
                last_updated=datetime.now().isoformat()
            )
    
    def analyze_news_impact(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the potential market impact of a news item"""
        try:
            text = news_item.get('title', '') + ' ' + news_item.get('content', '')
            processed_text = self._preprocess_text(text)
            
            # Calculate impact score based on financial keywords
            impact_score = 0.0
            for keyword, weight in self.impact_weights.items():
                if keyword in processed_text:
                    impact_score += weight
            
            # Normalize impact score
            impact_score = min(impact_score / 10.0, 1.0)
            
            # Determine impact level
            if impact_score > 0.7:
                impact_level = "HIGH"
            elif impact_score > 0.4:
                impact_level = "MEDIUM"
            else:
                impact_level = "LOW"
            
            # Calculate market relevance
            market_relevance = self._calculate_market_relevance(processed_text)
            
            # Calculate urgency
            urgency = self._calculate_urgency(processed_text)
            
            # Analyze sector impact
            sector_impact = self._analyze_sector_impact(processed_text)
            
            return {
                "impact_score": impact_score,
                "impact_level": impact_level,
                "market_relevance": market_relevance,
                "urgency": urgency,
                "sector_impact": sector_impact,
                "keywords_found": [k for k, w in self.impact_weights.items() if k in processed_text]
            }
            
        except Exception as e:
            logger.error(f"Error in news impact analysis: {str(e)}")
            return {
                "impact_score": 0.0,
                "impact_level": "LOW",
                "market_relevance": 0.0,
                "urgency": 0.0,
                "sector_impact": {},
                "error": str(e)
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _calculate_sentiment_score(self, text: str, sentiment_type: str) -> float:
        """Calculate sentiment score for given type"""
        score = 0.0
        keywords = self.financial_lexicon.get(sentiment_type, {})
        
        for keyword, weight in keywords.items():
            if keyword in text:
                score += weight
        
        return score
    
    def _apply_intensifiers(self, text: str, score: float) -> float:
        """Apply intensifier and negator effects to sentiment score"""
        # Apply intensifiers
        for intensifier, multiplier in self.financial_lexicon['intensifiers'].items():
            if intensifier in text:
                score *= multiplier
        
        # Apply negators
        for negator, multiplier in self.financial_lexicon['negators'].items():
            if negator in text:
                score *= multiplier
        
        return score
    
    def _extract_sentiment_keywords(self, text: str) -> List[str]:
        """Extract sentiment-related keywords from text"""
        keywords = []
        
        for sentiment_type in ['positive', 'negative']:
            for keyword in self.financial_lexicon[sentiment_type].keys():
                if keyword in text:
                    keywords.append(keyword)
        
        return keywords
    
    def _calculate_context_impact(self, text: str, context: Dict[str, Any]) -> float:
        """Calculate context impact on sentiment"""
        if not context:
            return 0.0
        
        # Example: if context indicates earnings season, financial terms have higher impact
        impact = 0.0
        
        if context.get('is_earnings_season', False):
            earnings_keywords = ['earnings', 'revenue', 'profit', 'guidance', 'forecast']
            impact += sum(0.1 for keyword in earnings_keywords if keyword in text.lower())
        
        if context.get('is_market_open', False):
            impact += 0.1  # Market-moving news has higher impact during trading hours
        
        return min(impact, 1.0)
    
    def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotional content in text"""
        emotions = {
            'excitement': 0.0,
            'fear': 0.0,
            'anger': 0.0,
            'surprise': 0.0,
            'sadness': 0.0
        }
        
        # Simple emotion detection based on keywords
        emotion_keywords = {
            'excitement': ['excited', 'thrilled', 'amazing', 'incredible', 'fantastic'],
            'fear': ['fear', 'worried', 'concerned', 'nervous', 'anxious'],
            'anger': ['angry', 'furious', 'outraged', 'frustrated', 'disappointed'],
            'surprise': ['surprised', 'shocked', 'unexpected', 'sudden', 'surprising'],
            'sadness': ['sad', 'disappointed', 'depressed', 'gloomy', 'pessimistic']
        }
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    emotions[emotion] += 0.2
        
        # Normalize emotions
        for emotion in emotions:
            emotions[emotion] = min(emotions[emotion], 1.0)
        
        return emotions
    
    def _calculate_market_relevance(self, text: str) -> float:
        """Calculate how relevant the text is to market movements"""
        relevance_keywords = [
            'stock', 'market', 'trading', 'investor', 'portfolio', 'equity',
            'share', 'price', 'volume', 'volatility', 'trend', 'analysis'
        ]
        
        relevance_score = sum(0.1 for keyword in relevance_keywords if keyword in text)
        return min(relevance_score, 1.0)
    
    def _calculate_urgency(self, text: str) -> float:
        """Calculate urgency level of the news"""
        urgency_keywords = [
            'urgent', 'breaking', 'immediate', 'critical', 'emergency',
            'alert', 'warning', 'crisis', 'crash', 'plunge', 'surge'
        ]
        
        urgency_score = sum(0.2 for keyword in urgency_keywords if keyword in text)
        return min(urgency_score, 1.0)
    
    def _analyze_sector_impact(self, text: str) -> Dict[str, float]:
        """Analyze which sectors might be impacted by the news"""
        sector_impacts = {}
        
        for sector, keywords in self.sector_keywords.items():
            impact = sum(0.1 for keyword in keywords if keyword in text)
            if impact > 0:
                sector_impacts[sector] = min(impact, 1.0)
        
        return sector_impacts
        
    def _build_financial_lexicon(self) -> Dict[str, Dict[str, float]]:
        """Build comprehensive financial sentiment lexicon with weighted scores"""
        return {
            'positive': {
                # Strong positive terms
                'breakthrough': 0.9, 'surge': 0.8, 'rally': 0.8, 'soar': 0.9, 'skyrocket': 0.9,
                'bullish': 0.8, 'optimistic': 0.7, 'confident': 0.7, 'strong': 0.6, 'robust': 0.7,
                'growth': 0.6, 'profit': 0.7, 'gain': 0.6, 'rise': 0.5, 'increase': 0.5,
                'beat': 0.8, 'exceed': 0.7, 'outperform': 0.7, 'success': 0.6, 'win': 0.6,
                'recovery': 0.6, 'rebound': 0.6, 'bounce': 0.5, 'upswing': 0.6, 'momentum': 0.5,
                'breakout': 0.7, 'milestone': 0.6, 'record': 0.7, 'high': 0.5, 'peak': 0.6,
                'expansion': 0.6, 'boom': 0.8, 'thrive': 0.7, 'flourish': 0.7, 'prosper': 0.7,
                'upgrade': 0.7, 'raise': 0.6, 'boost': 0.6, 'enhance': 0.5, 'improve': 0.5,
                'positive': 0.5, 'favorable': 0.6, 'promising': 0.6, 'bright': 0.5, 'solid': 0.5
            },
            'negative': {
                # Strong negative terms
                'crash': 0.9, 'plunge': 0.8, 'slump': 0.7, 'collapse': 0.9, 'tumble': 0.7,
                'bearish': 0.8, 'pessimistic': 0.7, 'concern': 0.6, 'worry': 0.6, 'fear': 0.7,
                'crisis': 0.9, 'recession': 0.8, 'downturn': 0.7, 'decline': 0.6, 'fall': 0.5,
                'loss': 0.7, 'miss': 0.6, 'underperform': 0.6, 'disappoint': 0.6, 'fail': 0.7,
                'volatility': 0.5, 'uncertainty': 0.6, 'risk': 0.5, 'pressure': 0.5, 'stress': 0.6,
                'weak': 0.6, 'soft': 0.5, 'sluggish': 0.6, 'stagnant': 0.5, 'flat': 0.4,
                'downgrade': 0.7, 'cut': 0.6, 'reduce': 0.5, 'lower': 0.5, 'decrease': 0.5,
                'negative': 0.5, 'unfavorable': 0.6, 'concerning': 0.6, 'troubling': 0.7, 'alarming': 0.8,
                'drop': 0.5, 'down': 0.4, 'dip': 0.4, 'slip': 0.4, 'retreat': 0.5
            },
            'intensifiers': {
                # Intensifying words
                'very': 1.5, 'extremely': 2.0, 'highly': 1.8, 'significantly': 1.7, 'substantially': 1.6,
                'dramatically': 1.8, 'massively': 2.0, 'tremendously': 1.9, 'considerably': 1.6,
                'slightly': 0.7, 'somewhat': 0.8, 'moderately': 0.9, 'fairly': 0.9, 'relatively': 0.8
            },
            'negators': {
                # Negation words
                'not': -1.0, 'no': -1.0, 'never': -1.0, 'none': -1.0, 'nothing': -1.0,
                'nobody': -1.0, 'nowhere': -1.0, 'neither': -1.0, 'nor': -1.0, 'without': -1.0,
                'lack': -0.8, 'absence': -0.8, 'missing': -0.7, 'devoid': -0.8
            }
        }
    
    def _build_impact_weights(self) -> Dict[str, float]:
        """Build impact weights for different types of financial content"""
        return {
            'earnings': 1.5, 'revenue': 1.3, 'profit': 1.4, 'guidance': 1.6, 'forecast': 1.4,
            'merger': 1.8, 'acquisition': 1.7, 'partnership': 1.2, 'deal': 1.3, 'agreement': 1.1,
            'ceo': 1.3, 'executive': 1.2, 'management': 1.1, 'leadership': 1.1, 'board': 1.2,
            'dividend': 1.2, 'buyback': 1.3, 'split': 1.1, 'spinoff': 1.4, 'ipo': 1.5,
            'regulation': 1.4, 'policy': 1.3, 'government': 1.5, 'federal': 1.4, 'sec': 1.3,
            'analyst': 1.2, 'rating': 1.3, 'upgrade': 1.4, 'downgrade': 1.4, 'target': 1.2,
            'crisis': 2.0, 'scandal': 1.8, 'investigation': 1.6, 'lawsuit': 1.5, 'fine': 1.4
        }
    
    def _build_sector_keywords(self) -> Dict[str, List[str]]:
        """Build sector-specific keywords for enhanced analysis"""
        return {
            'technology': ['tech', 'software', 'ai', 'artificial intelligence', 'cloud', 'digital', 'cyber', 'data'],
            'finance': ['bank', 'financial', 'credit', 'loan', 'interest', 'rate', 'fed', 'monetary'],
            'healthcare': ['pharma', 'drug', 'medical', 'health', 'biotech', 'clinical', 'fda', 'treatment'],
            'energy': ['oil', 'gas', 'energy', 'renewable', 'solar', 'wind', 'fossil', 'drilling'],
            'retail': ['retail', 'consumer', 'shopping', 'store', 'sales', 'ecommerce', 'amazon', 'walmart'],
            'automotive': ['auto', 'car', 'vehicle', 'tesla', 'electric', 'ev', 'manufacturing', 'production']
        }

def analyze_sentiment(text: str) -> Tuple[str, float]:
    """Enhanced sentiment analysis using AI-powered approach"""
    try:
        if not text or text.strip() == "":
            return "NEUTRAL", 0.0
        
        analyzer = AISentimentAnalyzer()
        return analyzer.analyze_text_sentiment(text)
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        return "NEUTRAL", 0.0

def analyze_sentiment_advanced(text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Advanced sentiment analysis with context and detailed metrics"""
    try:
        if not text or text.strip() == "":
            return {
                "sentiment": "NEUTRAL",
                "confidence": 0.0,
                "score": 0.0,
                "magnitude": 0.0,
                "emotions": {},
                "keywords": [],
                "context_impact": 0.0
            }
        
        analyzer = AISentimentAnalyzer()
        return analyzer.analyze_advanced_sentiment(text, context)
        
    except Exception as e:
        logger.error(f"Error in advanced sentiment analysis: {str(e)}")
        return {
            "sentiment": "NEUTRAL",
            "confidence": 0.0,
            "score": 0.0,
            "magnitude": 0.0,
            "emotions": {},
            "keywords": [],
            "context_impact": 0.0,
            "error": str(e)
        }

def analyze_market_sentiment(news_items: List[Dict[str, Any]]) -> MarketSentiment:
    """Analyze overall market sentiment from multiple news items"""
    try:
        if not news_items:
            return MarketSentiment(
                overall_sentiment="NEUTRAL",
                sentiment_score=0.0,
                confidence=0.0,
                news_count=0,
                positive_ratio=0.0,
                negative_ratio=0.0,
                neutral_ratio=1.0,
                last_updated=datetime.now().isoformat()
            )
        
        analyzer = AISentimentAnalyzer()
        return analyzer.analyze_market_sentiment(news_items)
        
    except Exception as e:
        logger.error(f"Error in market sentiment analysis: {str(e)}")
        return MarketSentiment(
            overall_sentiment="NEUTRAL",
            sentiment_score=0.0,
            confidence=0.0,
            news_count=len(news_items),
            positive_ratio=0.0,
            negative_ratio=0.0,
            neutral_ratio=1.0,
            last_updated=datetime.now().isoformat()
        )

def analyze_news_impact(news_item: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the potential market impact of a news item"""
    try:
        analyzer = AISentimentAnalyzer()
        return analyzer.analyze_news_impact(news_item)
        
    except Exception as e:
        logger.error(f"Error in news impact analysis: {str(e)}")
        return {
            "impact_score": 0.0,
            "impact_level": "LOW",
            "market_relevance": 0.0,
            "urgency": 0.0,
            "sector_impact": {},
            "error": str(e)
        }
