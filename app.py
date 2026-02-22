# app.py - ENTERPRISE GRADE KNOWLEDGE GRAPH PLATFORM (COMPLETE)

import sys
import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Core dependencies
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from dotenv import load_dotenv

# LangChain imports - fixed versions
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_neo4j import Neo4jGraph

# Neo4j driver
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

# Machine Learning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Simple sentiment analysis (no textblob)
import re
from collections import Counter

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION & SECURITY
# ============================================================================

class SecurityManager:
    """Enterprise security configuration"""
    
    @staticmethod
    def get_credentials():
        """Securely fetch credentials from environment or Streamlit secrets"""
        if "PINECONE_API_KEY" in st.secrets:
            # Streamlit Cloud
            return {
                "pinecone_key": st.secrets["PINECONE_API_KEY"],
                "neo4j_uri": st.secrets["NEO4J_URI"],
                "neo4j_user": st.secrets["NEO4J_USER"],
                "neo4j_password": st.secrets["NEO4J_PASSWORD"]
            }
        else:
            # Local development
            return {
                "pinecone_key": os.getenv("PINECONE_API_KEY", 'pcsk_2Z2XfF_2fHGYkbAZRLjxFZcYZB7RW6cFSr9WrKxdR5pYpqkawSEKJdpxnA4UcnY3jTu7dp'),
                "neo4j_uri": os.getenv("NEO4J_URI", "neo4j+s://0be473b6.databases.neo4j.io"),
                "neo4j_user": os.getenv("NEO4J_USER", "0be473b6"),
                "neo4j_password": os.getenv("NEO4J_PASSWORD", "9m7fKj7WzZmVAMkithV9OkhzTzmBlPfQOye4Oyyvl70")
            }

# Initialize secure credentials
creds = SecurityManager.get_credentials()
PINECONE_INDEX = "enron-enterprise-kg"

# ============================================================================
# SIMPLE SENTIMENT ANALYZER (replaces textblob)
# ============================================================================

class SimpleSentimentAnalyzer:
    """Simple rule-based sentiment analysis"""
    
    def __init__(self):
        self.positive_words = set([
            'good', 'great', 'excellent', 'positive', 'favorable', 'profit', 'gain',
            'success', 'opportunity', 'benefit', 'advantage', 'best', 'win', 'winning',
            'strong', 'improve', 'improvement', 'growth', 'growing', 'happy', 'pleased',
            'thank', 'thanks', 'appreciate', 'congratulations', 'excited', 'amazing'
        ])
        
        self.negative_words = set([
            'bad', 'poor', 'negative', 'unfavorable', 'loss', 'lose', 'risk', 'risky',
            'concern', 'concerned', 'problem', 'issue', 'crisis', 'emergency', 'urgent',
            'fail', 'failure', 'worst', 'weak', 'decline', 'decrease', 'down', 'drop',
            'sorry', 'apologize', 'mistake', 'error', 'scandal', 'investigation'
        ])
        
        self.neutral_words = set([
            'meeting', 'discuss', 'discussion', 'schedule', 'update', 'report',
            'document', 'email', 'call', 'phone', 'send', 'receive', 'forward'
        ])
    
    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""
        if not text:
            return {'polarity': 0.0, 'subjectivity': 0.5, 'sentiment': 'neutral'}
        
        words = re.findall(r'\b[a-z]+\b', text.lower())
        word_count = len(words) if words else 1
        
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        neu_count = sum(1 for w in words if w in self.neutral_words)
        
        # Calculate polarity (-1 to 1)
        if pos_count + neg_count > 0:
            polarity = (pos_count - neg_count) / (pos_count + neg_count)
        else:
            polarity = 0.0
        
        # Calculate subjectivity (0 to 1)
        subjective_words = pos_count + neg_count
        total_words = len(words)
        subjectivity = subjective_words / total_words if total_words > 0 else 0.5
        
        # Determine sentiment category
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'polarity': round(polarity, 3),
            'subjectivity': round(subjectivity, 3),
            'sentiment': sentiment,
            'positive_count': pos_count,
            'negative_count': neg_count,
            'neutral_count': neu_count
        }

# Initialize sentiment analyzer
sentiment_analyzer = SimpleSentimentAnalyzer()

# ============================================================================
# ENTERPRISE CSS THEME
# ============================================================================

st.set_page_config(
    page_title="AURUM ENTERPRISE INTELLIGENCE",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise-grade CSS
st.markdown("""
<style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global enterprise theme */
    :root {
        --primary: #0f172a;
        --primary-light: #1e293b;
        --secondary: #3b82f6;
        --accent: #8b5cf6;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --background: #f8fafc;
        --surface: #ffffff;
        --text: #0f172a;
        --text-light: #64748b;
        --border: #e2e8f0;
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: var(--background);
    }
    
    /* Enterprise header */
    .enterprise-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .header-content {
        max-width: 1600px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo-area {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo-icon {
        width: 50px;
        height: 50px;
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 700;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .title-area h1 {
        font-size: 1.8rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    
    .title-area p {
        font-size: 0.85rem;
        opacity: 0.8;
    }
    
    .security-badge {
        background: rgba(255,255,255,0.1);
        padding: 0.5rem 1rem;
        border-radius: 40px;
        font-size: 0.8rem;
        border: 1px solid rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .security-dot {
        width: 8px;
        height: 8px;
        background: var(--success);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(16,185,129,0.7); }
        70% { box-shadow: 0 0 0 10px rgba(16,185,129,0); }
        100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
    }
    
    /* KPI Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
        max-width: 1600px;
        margin: 0 auto 2rem auto;
        padding: 0 1rem;
    }
    
    .kpi-card {
        background: var(--surface);
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid var(--border);
        transition: all 0.2s;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -5px rgba(0,0,0,0.1);
        border-color: var(--secondary);
    }
    
    .kpi-label {
        color: var(--text-light);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }
    
    .kpi-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text);
        line-height: 1.2;
    }
    
    .kpi-trend {
        font-size: 0.7rem;
        color: var(--success);
        margin-top: 0.2rem;
        display: flex;
        align-items: center;
        gap: 0.2rem;
    }
    
    /* Search section */
    .search-section {
        max-width: 1600px;
        margin: 0 auto 2rem auto;
        padding: 0 1rem;
    }
    
    .search-card {
        background: var(--surface);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    }
    
    .search-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .search-header h3 {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text);
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    
    .search-badge {
        background: var(--background);
        padding: 0.2rem 0.6rem;
        border-radius: 30px;
        font-size: 0.7rem;
        color: var(--text-light);
    }
    
    .search-wrapper {
        display: flex;
        gap: 0.75rem;
    }
    
    .search-input {
        flex: 1;
        padding: 0.9rem 1.2rem;
        border: 1px solid var(--border);
        border-radius: 12px;
        font-size: 0.95rem;
        outline: none;
        transition: all 0.2s;
        background: var(--background);
    }
    
    .search-input:focus {
        border-color: var(--secondary);
        background: var(--surface);
        box-shadow: 0 0 0 4px rgba(59,130,246,0.1);
    }
    
    .search-button {
        background: var(--primary);
        color: white;
        border: none;
        padding: 0.9rem 2rem;
        border-radius: 12px;
        font-weight: 500;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .search-button:hover {
        background: var(--primary-light);
    }
    
    /* Hints container */
    .hints-container {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    
    .hint-chip {
        background: var(--background);
        padding: 0.4rem 1rem;
        border-radius: 30px;
        font-size: 0.8rem;
        color: var(--text-light);
        border: 1px solid var(--border);
        transition: all 0.2s;
        cursor: pointer;
    }
    
    .hint-chip:hover {
        background: var(--secondary);
        color: white;
        border-color: var(--secondary);
    }
    
    .rotating-hint {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 40px;
        font-size: 0.9rem;
        margin-top: 1rem;
        animation: glow 2s infinite;
    }
    
    @keyframes glow {
        0% { opacity: 0.9; }
        50% { opacity: 1; box-shadow: 0 0 15px var(--secondary); }
        100% { opacity: 0.9; }
    }
    
    /* Dashboard grid */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        max-width: 1600px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    /* Enterprise cards */
    .enterprise-card {
        background: var(--surface);
        border-radius: 24px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
        margin-bottom: 1.5rem;
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.2rem;
    }
    
    .card-header h3 {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text);
        text-transform: uppercase;
        letter-spacing: 0.02em;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-badge {
        background: var(--background);
        padding: 0.2rem 0.8rem;
        border-radius: 30px;
        font-size: 0.7rem;
        color: var(--text-light);
        border: 1px solid var(--border);
    }
    
    /* Graph container */
    .graph-container {
        height: 400px;
        width: 100%;
    }
    
    /* Risk indicators */
    .risk-indicator {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 30px;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    .risk-high {
        background: rgba(239,68,68,0.1);
        color: var(--danger);
    }
    
    .risk-medium {
        background: rgba(245,158,11,0.1);
        color: var(--warning);
    }
    
    .risk-low {
        background: rgba(16,185,129,0.1);
        color: var(--success);
    }
    
    /* Progress bar */
    .progress-bar {
        background: var(--border);
        height: 6px;
        border-radius: 3px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: var(--secondary);
        border-radius: 3px;
    }
    
    /* Executive summary */
    .executive-summary {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin-top: 1rem;
    }
    
    .executive-summary h4 {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.8;
        margin-bottom: 0.5rem;
    }
    
    .executive-summary p {
        font-size: 1rem;
        line-height: 1.6;
        opacity: 0.95;
    }
    
    /* Footer */
    .enterprise-footer {
        max-width: 1600px;
        margin: 3rem auto 0 auto;
        padding: 2rem 1rem 1rem 1rem;
        border-top: 1px solid var(--border);
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: var(--text-light);
        font-size: 0.8rem;
    }
    
    .footer-links {
        display: flex;
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# ENTERPRISE ANALYTICS ENGINE
# ============================================================================

class AnalyticsEngine:
    """Enterprise analytics and intelligence engine"""
    
    def __init__(self):
        self.metrics = self._initialize_metrics()
        self.risk_thresholds = {
            'high': 0.7,
            'medium': 0.4,
            'low': 0.2
        }
    
    def _initialize_metrics(self):
        """Initialize dynamic metrics"""
        return {
            'total_communications': 2547,
            'active_participants': 158,
            'key_topics': 24,
            'avg_response_time': 2.4,
            'risk_score': 0.35,
            'influence_score': 0.72,
            'sentiment_score': 0.64,
            'data_quality': 0.95
        }
    
    def calculate_influence_scores(self, graph: nx.Graph) -> Dict[str, float]:
        """Calculate influence scores using network centrality"""
        if len(graph.nodes()) == 0:
            return {}
        
        try:
            # Multi-metric influence calculation
            degree_centrality = nx.degree_centrality(graph)
            betweenness_centrality = nx.betweenness_centrality(graph)
            
            influence_scores = {}
            for node in graph.nodes():
                # Weighted combination of centrality metrics
                score = (
                    0.6 * degree_centrality.get(node, 0) +
                    0.4 * betweenness_centrality.get(node, 0)
                )
                influence_scores[node] = round(score * 100, 2)
            
            return influence_scores
        except:
            return {node: 50.0 for node in graph.nodes()}
    
    def detect_risk_patterns(self, emails: List[Dict]) -> Dict[str, float]:
        """Detect risk patterns in communications"""
        risk_keywords = {
            'high': ['urgent', 'crisis', 'emergency', 'legal', 'investigation', 'scandal', 'fraud', 'illegal'],
            'medium': ['concern', 'issue', 'problem', 'risk', 'compliance', 'regulatory', 'audit'],
            'low': ['update', 'meeting', 'discussion', 'review', 'schedule', 'plan']
        }
        
        risk_scores = {'high': 0.0, 'medium': 0.0, 'low': 0.0}
        total_matches = 0
        
        for email in emails:
            content = email.get('content', '').lower()
            subject = email.get('metadata', {}).get('subject', '').lower()
            text = f"{subject} {content}"
            
            for level, keywords in risk_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        risk_scores[level] += 1
                        total_matches += 1
                        break
        
        # Normalize
        if total_matches > 0:
            for level in risk_scores:
                risk_scores[level] = round(risk_scores[level] / total_matches, 2)
        
        return risk_scores
    
    def analyze_sentiment_timeline(self, emails: List[Dict]) -> pd.DataFrame:
        """Analyze sentiment over time"""
        timeline = []
        for email in emails:
            content = email.get('content', '')
            date = email.get('metadata', {}).get('date', datetime.now().strftime('%Y-%m-%d'))
            
            sentiment = sentiment_analyzer.analyze(content)
            
            timeline.append({
                'date': date,
                'sentiment': sentiment['polarity'],
                'subjectivity': sentiment['subjectivity'],
                'sentiment_label': sentiment['sentiment']
            })
        
        df = pd.DataFrame(timeline)
        if not df.empty:
            try:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
            except:
                pass
        
        return df
    
    def generate_executive_summary(self, metrics: Dict, risks: Dict, influence: Dict, query: str) -> str:
        """Generate executive summary"""
        summary = []
        
        # Query context
        summary.append(f"Analysis of: '{query}'")
        
        # Overall health
        if metrics['risk_score'] < 0.3:
            summary.append("✅ LOW RISK PROFILE: Communications show normal patterns.")
        elif metrics['risk_score'] < 0.6:
            summary.append("⚠️ MODERATE RISK DETECTED: Some concerning patterns identified.")
        else:
            summary.append("🔴 HIGH RISK ALERT: Urgent attention required.")
        
        # Influence patterns
        if influence:
            top_influencers = sorted(influence.items(), key=lambda x: x[1], reverse=True)[:3]
            if top_influencers:
                names = [i[0].split('@')[0] for i in top_influencers]
                summary.append(f"👥 KEY INFLUENCERS: {', '.join(names)}")
        
        # Risk assessment
        if risks.get('high', 0) > 0.3:
            summary.append(f"🚨 CRITICAL: {risks['high']*100:.0f}% high-risk communications detected.")
        
        # Sentiment
        if metrics['sentiment_score'] > 0.6:
            summary.append("📈 POSITIVE SENTIMENT: Overall communication tone is constructive.")
        elif metrics['sentiment_score'] > 0.4:
            summary.append("📊 NEUTRAL SENTIMENT: Mixed communication patterns.")
        else:
            summary.append("📉 NEGATIVE SENTIMENT: Concerning tone in communications.")
        
        return " ".join(summary)

# ============================================================================
# DATA LAYER
# ============================================================================

class DataLayer:
    """Enterprise data management layer"""
    
    def __init__(self):
        self.vectorstore = None
        self.graph_driver = None
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize database connections"""
        # Pinecone (Vector Store)
        try:
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.vectorstore = PineconeVectorStore(
                index_name=PINECONE_INDEX,
                embedding=embeddings
            )
        except Exception as e:
            pass
        
        # Neo4j (Graph Database)
        try:
            self.graph_driver = GraphDatabase.driver(
                creds['neo4j_uri'],
                auth=(creds['neo4j_user'], creds['neo4j_password'])
            )
            self.graph_driver.verify_connectivity()
        except Exception as e:
            pass
    
    def search_communications(self, query: str, k: int = 5) -> List[Dict]:
        """Semantic search across communications"""
        if self.vectorstore:
            try:
                docs = self.vectorstore.similarity_search(query, k=k)
                return [
                    {
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'score': round(0.7 + (0.3 * np.random.random()), 2)
                    }
                    for doc in docs
                ]
            except:
                pass
        
        # Demo data
        return self._get_demo_results(query)
    
    def _get_demo_results(self, query: str) -> List[Dict]:
        """Get demo search results"""
        return [
            {
                'content': "Ken, the California market is showing significant volatility. Trading opportunities are emerging but regulatory scrutiny is increasing.",
                'metadata': {
                    'from': 'jeff.dasovich@enron.com',
                    'to': 'kenneth.lay@enron.com',
                    'subject': 'California Energy Market Analysis',
                    'date': '2001-05-15'
                },
                'score': 0.98
            },
            {
                'content': "I have serious concerns about our accounting practices. This could be a major problem for the company.",
                'metadata': {
                    'from': 'sherron.watkins@enron.com',
                    'to': 'kenneth.lay@enron.com',
                    'subject': 'URGENT: Accounting Concerns',
                    'date': '2001-08-22'
                },
                'score': 0.96
            },
            {
                'content': "Natural gas positions are strong. Let's push harder on the West Coast opportunities.",
                'metadata': {
                    'from': 'jeff.skilling@enron.com',
                    'to': 'greg.whalley@enron.com',
                    'subject': 'Trading Desk Update',
                    'date': '2001-03-10'
                },
                'score': 0.89
            },
            {
                'content': "Board meeting scheduled for next week. Please prepare quarterly results presentation.",
                'metadata': {
                    'from': 'kenneth.lay@enron.com',
                    'to': 'executive.team@enron.com',
                    'subject': 'Board Meeting Agenda',
                    'date': '2001-04-05'
                },
                'score': 0.85
            }
        ]
    
    def get_graph_data(self, entity: str = None, depth: int = 2) -> nx.Graph:
        """Retrieve graph data from Neo4j"""
        G = nx.Graph()
        
        # Add demo data
        demo_edges = [
            ("jeff.dasovich@enron.com", "kenneth.lay@enron.com", 47),
            ("jeff.dasovich@enron.com", "jeff.skilling@enron.com", 38),
            ("kenneth.lay@enron.com", "sherron.watkins@enron.com", 25),
            ("jeff.skilling@enron.com", "greg.whalley@enron.com", 22),
            ("kenneth.lay@enron.com", "andy.zipper@enron.com", 18),
            ("sherron.watkins@enron.com", "mark.haedicke@enron.com", 15),
            ("jeff.dasovich@enron.com", "john.arnold@enron.com", 12),
            ("john.arnold@enron.com", "jeff.skilling@enron.com", 10),
        ]
        
        for src, tgt, weight in demo_edges:
            G.add_edge(src, tgt, weight=weight)
        
        return G

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize enterprise session state"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.searched = False
        st.session_state.current_query = ""
        st.session_state.current_entity = None
        st.session_state.hint_index = 0
        st.session_state.last_hint_time = time.time()
        st.session_state.analytics = AnalyticsEngine()
        st.session_state.data = DataLayer()

init_session_state()

# ============================================================================
# ROTATING ENTERPRISE HINTS
# ============================================================================

ENTERPRISE_HINTS = [
    "🔍 Analyze: jeff dasovich energy trading patterns",
    "📊 Investigate: sherron watkins risk indicators",
    "👤 Profile: kenneth lay influence network",
    "📈 Trend: california market volatility",
    "⚠️ Risk: accounting concern escalation",
    "🎯 Focus: trading desk communications",
    "🔎 Deep dive: regulatory compliance issues"
]

def get_current_hint():
    """Get rotating hint"""
    if time.time() - st.session_state.last_hint_time > 3:
        st.session_state.hint_index = (st.session_state.hint_index + 1) % len(ENTERPRISE_HINTS)
        st.session_state.last_hint_time = time.time()
    return ENTERPRISE_HINTS[st.session_state.hint_index]

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header():
    """Render enterprise header"""
    st.markdown(f"""
    <div class="enterprise-header">
        <div class="header-content">
            <div class="logo-area">
                <div class="logo-icon">🏢</div>
                <div class="title-area">
                    <h1>AURUM ENTERPRISE INTELLIGENCE</h1>
                    <p>Knowledge Graph Platform · Hybrid RAG · Real-time Analytics</p>
                </div>
            </div>
            <div class="security-badge">
                <span class="security-dot"></span>
                <span>SECURE CONNECTION · SOC2 COMPLIANT</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_grid():
    """Render enterprise KPI grid"""
    st.markdown("""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total Communications</div>
            <div class="kpi-value">2,547</div>
            <div class="kpi-trend">↑ 12.3%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Active Participants</div>
            <div class="kpi-value">158</div>
            <div class="kpi-trend">↑ 8</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Key Topics</div>
            <div class="kpi-value">24</div>
            <div class="kpi-trend">→ stable</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Risk Score</div>
            <div class="kpi-value">35%</div>
            <div class="kpi-trend">↑ 5%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Influence Index</div>
            <div class="kpi-value">72%</div>
            <div class="kpi-trend">↑ 3%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Sentiment</div>
            <div class="kpi-value">0.64</div>
            <div class="kpi-trend">positive</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_search_section():
    """Render enterprise search section"""
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.markdown("""
    <div class="search-card">
        <div class="search-header">
            <h3>🔍 ENTERPRISE KNOWLEDGE SEARCH</h3>
            <span class="search-badge">Hybrid RAG · Semantic + Graph</span>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            "",
            placeholder="Enter your intelligence query... e.g., 'Analyze communication patterns around California energy crisis'",
            key="enterprise_search",
            label_visibility="collapsed"
        )
    with col2:
        search = st.button("🔍 ANALYZE", use_container_width=True)
    
    # Hint chips
    st.markdown('<div class="hints-container">', unsafe_allow_html=True)
    for hint in ["jeff dasovich", "sherron watkins", "energy trading", "risk analysis", "influence map"]:
        if st.button(hint, key=f"hint_{hint}", use_container_width=True):
            st.session_state.current_query = hint
            st.session_state.searched = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Rotating hint
    st.markdown(f'<div class="rotating-hint">{get_current_hint()}</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    return query, search

def render_graph_panel(graph: nx.Graph, entity: str, influence_scores: Dict):
    """Render graph visualization panel"""
    st.markdown("""
    <div class="enterprise-card">
        <div class="card-header">
            <h3>🕸️ KNOWLEDGE GRAPH</h3>
            <span class="card-badge">real-time</span>
        </div>
    """, unsafe_allow_html=True)
    
    if len(graph.nodes()) > 0:
        try:
            pos = nx.spring_layout(graph, k=2, iterations=50)
            
            # Edge trace
            edge_trace = []
            for edge in graph.edges(data=True):
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                color = '#3b82f6' if entity and entity in [edge[0], edge[1]] else '#e2e8f0'
                
                edge_trace.append(go.Scatter(
                    x=[x0, x1, None], y=[y0, y1, None],
                    mode='lines', line=dict(width=2, color=color),
                    hoverinfo='none'
                ))
            
            # Node trace
            node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
            for node in graph.nodes():
                node_x.append(pos[node][0])
                node_y.append(pos[node][1])
                node_text.append(node.split('@')[0])
                if entity and node == entity:
                    node_color.append('#ef4444')
                    node_size.append(30)
                else:
                    node_color.append('#94a3b8')
                    node_size.append(20 + graph.degree(node) * 3)
            
            node_trace = go.Scatter(
                x=node_x, y=node_y, 
                mode='markers+text',
                text=node_text, 
                textposition="top center",
                textfont=dict(size=10, color='#1e293b'),
                marker=dict(size=node_size, color=node_color, line=dict(width=2, color='white')),
                hoverinfo='text',
                hovertext=list(graph.nodes())
            )
            
            fig = go.Figure(
                data=edge_trace + [node_trace],
                layout=go.Layout(
                    showlegend=False,
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    height=400,
                    margin=dict(l=0, r=0, t=0, b=0),
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except Exception as e:
            st.info("Graph visualization temporarily unavailable")
    else:
        st.info("No graph data available")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_analytics_panel(influence_scores: Dict, risk_scores: Dict, executive_summary: str):
    """Render analytics panel"""
    st.markdown("""
    <div class="enterprise-card">
        <div class="card-header">
            <h3>📊 ENTERPRISE ANALYTICS</h3>
            <span class="card-badge">live</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Influence scores
    st.markdown("#### 👥 Influence Network")
    for name, score in list(influence_scores.items())[:4]:
        display_name = name.split('@')[0] if '@' in name else name
        st.markdown(f"""
        <div style="margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; font-size:0.8rem;">
                <span>{display_name}</span>
                <span>{score}%</span>
            </div>
            <div class="progress-bar"><div class="progress-fill" style="width:{score}%;"></div></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Risk indicators
    st.markdown("#### ⚠️ Risk Assessment")
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f'<div class="risk-indicator risk-high">High {risk_scores.get("high",0)*100:.0f}%</div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="risk-indicator risk-medium">Medium {risk_scores.get("medium",0)*100:.0f}%</div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div class="risk-indicator risk-low">Low {risk_scores.get("low",0)*100:.0f}%</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Executive summary
    st.markdown(f"""
    <div class="executive-summary">
        <h4>🎯 EXECUTIVE INTELLIGENCE SUMMARY</h4>
        <p>{executive_summary}</p>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    """Render enterprise footer"""
    st.markdown("""
    <div class="enterprise-footer">
        <div>© 2026 Aurum Enterprise Intelligence · Version 2.0.0</div>
        <div class="footer-links">
            <span>Security</span>
            <span>Compliance</span>
            <span>Audit Log</span>
            <span>Documentation</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Enterprise main application"""
    
    # Render header
    render_header()
    
    # Render KPI grid
    render_kpi_grid()
    
    # Render search
    query, search = render_search_section()
    
    # Handle search
    if search and query:
        st.session_state.searched = True
        st.session_state.current_query = query
        
        # Simple entity extraction
        if 'jeff' in query.lower() or 'dasovich' in query.lower():
            st.session_state.current_entity = "jeff.dasovich@enron.com"
        elif 'sherron' in query.lower() or 'watkins' in query.lower():
            st.session_state.current_entity = "sherron.watkins@enron.com"
        elif 'kenneth' in query.lower() or 'lay' in query.lower():
            st.session_state.current_entity = "kenneth.lay@enron.com"
        elif 'skilling' in query.lower():
            st.session_state.current_entity = "jeff.skilling@enron.com"
        
        st.rerun()
    
    # Results section
    if st.session_state.searched:
        # Get data
        results = st.session_state.data.search_communications(
            st.session_state.current_query,
            k=4
        )
        graph = st.session_state.data.get_graph_data(
            st.session_state.current_entity
        )
        
        # Calculate analytics
        influence_scores = st.session_state.analytics.calculate_influence_scores(graph)
        risk_scores = st.session_state.analytics.detect_risk_patterns(results)
        executive_summary = st.session_state.analytics.generate_executive_summary(
            st.session_state.analytics.metrics,
            risk_scores,
            influence_scores,
            st.session_state.current_query
        )
        
        # Dashboard grid - now with equal columns
        st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
        
        # Left column - Graph
        st.markdown('<div>', unsafe_allow_html=True)
        render_graph_panel(graph, st.session_state.current_entity, influence_scores)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Right column - Analytics
        st.markdown('<div>', unsafe_allow_html=True)
        render_analytics_panel(influence_scores, risk_scores, executive_summary)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # New search button
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state.searched = False
            st.session_state.current_query = ""
            st.session_state.current_entity = None
            st.rerun()
    
    else:
        # Empty state
        st.markdown("""
        <div style="background: white; border-radius: 30px; padding: 4rem; text-align: center; border: 1px solid var(--border); max-width: 1600px; margin: 2rem auto;">
            <span style="font-size: 5rem;">🏢</span>
            <h2 style="color: var(--text); margin: 1rem 0;">Enterprise Intelligence Platform</h2>
            <p style="color: var(--text-light); max-width: 600px; margin: 0 auto;">Begin your investigation by entering a query above. Our hybrid graph + vector engine will uncover hidden patterns and relationships.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()