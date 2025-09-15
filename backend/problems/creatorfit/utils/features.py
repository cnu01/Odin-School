from __future__ import annotations
import re
from typing import Tuple, Dict, List, Optional, Iterable
import numpy as np
import pandas as pd

EDTECH_TOPICS = [
    "Python", "Data Science", "Machine Learning", "JavaScript", "React",
    "Node.js", "SQL", "Frontend Development", "Backend Development",
    "Web Development", "Mobile Development", "DevOps", "Cloud Computing",
    "Artificial Intelligence", "Deep Learning", "Analytics", "Database",
    "Career Guidance", "Interview Preparation", "System Design", "Django",
    "Programming Fundamentals", "C++", "Statistics", "Data Structures",
]

ODIN_SCHOOL_PROGRAMS = {
    "data_science": """
    Data science programming tutorial covering Python basics, pandas dataframes, 
    machine learning algorithms, statistics concepts, data visualization, 
    deep learning neural networks, career advice for data scientists
    """,
    "web_development": """
    Web development tutorial teaching HTML CSS basics, JavaScript programming,
    React components, Node.js backend, database integration, full-stack projects,
    frontend backend development career guidance
    """,
    "ai_ml": """
    Artificial Intelligence and Machine Learning tutorial covering supervised unsupervised learning,
    deep learning neural networks CNN RNN transformers, natural language processing,
    computer vision applications, reinforcement learning basics, model deployment MLOps,
    real-world AI projects, career guidance for AI ML engineers and researchers
    """,
    "career_guidance": """
    Technical career guidance covering software engineering interview preparation,
    coding practice algorithms data structures, system design concepts,
    resume building portfolio development, job search strategies,
    salary negotiation, career progression in tech industry
    """
}

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    print(f"[INFO] SentenceTransformers not available: {e}")
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

_MODEL_CACHE: Dict[str, any] = {}

def truncate_text(text: str, max_tokens: int = 128) -> str:
    """
    Truncate text while preserving semantic integrity.
    Keeps beginning and end to maintain context.
    """
    words = text.split()
    if len(words) <= max_tokens:
        return text
    
    # Keep first 60% and last 40% to preserve context
    first_part = int(max_tokens * 0.6)
    last_part = max_tokens - first_part
    
    truncated = words[:first_part] + words[-last_part:]
    return ' '.join(truncated)

def _get_emb_model(name: str):
    """Return a cached SentenceTransformer instance for the given model name."""
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise ValueError("SentenceTransformers library is not available.")

    if name not in _MODEL_CACHE:
        _MODEL_CACHE.clear()  # Clear the cache to avoid conflicts
        _MODEL_CACHE[name] = SentenceTransformer(name)
    else:
        print(f"[INFO] Using cached model: {name}")

    return _MODEL_CACHE[name]

def _normalize_text_series(s: pd.Series) -> pd.Series:
    """
    text preprocessing for better semantic matching.
    """
    def clean_text(text: str) -> str:
        if not text or pd.isna(text):
            return ""
        
        text = str(text).lower()
        
        text = re.sub(r'\s+', ' ', text)
        
        text = re.sub(r'\b(um|uh|like|you know|basically|actually)\b', '', text)
        
        # Remove special characters but keep punctuation for context
        text = re.sub(r'[^\w\s.,!?-]', ' ', text)
        
        return text.strip()
    
    return s.apply(clean_text)

def _encode_texts(
    texts: Iterable[str],
    model: SentenceTransformer,
    batch_size: int = 256,
    normalize: bool = True,
) -> np.ndarray:
    """
    Encode texts in batches (SentenceTransformer handles batching internally).
    Returns an array of shape (N, d).
    """
    return model.encode(
        list(texts),
        batch_size=batch_size,
        normalize_embeddings=normalize,   # if True, vectors are L2-normalized
        show_progress_bar=False,
    )

def is_program_relevant(content: str, program_type: str, program_text: str) -> bool:
    """Check if content contains program-related keywords"""
    if pd.isna(content) or not content:
        return False
    
    content_lower = str(content).lower()
    
    program_name = program_type.replace('_', ' ')
    if program_name in content_lower:
        return True
    
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
    
    # Extract words that are 3+ characters and not stop words
    program_words = re.findall(r'\b[a-zA-Z]{3,}\b', program_text.lower())
    meaningful_words = [word for word in program_words if word not in stop_words]
    
    matches = sum(1 for word in meaningful_words if word in content_lower)
    return matches >= 2

def compute_fit_scores(
    df: pd.DataFrame,
    program_type: str,
    program_text: str,
    emb_model_name = DEFAULT_EMBEDDING_MODEL,
    model = None,
    batch_size: int = 256,
) -> pd.Series:
    """
    Compute semantic Fit Score between each creator transcript and the program description.
    """
    if not isinstance(program_text, str) or not program_text.strip():
        raise ValueError("program_text must be a non-empty string.")
    
    relevant_mask = (
        df["recent_video_transcript"].apply(lambda x: is_program_relevant(x, program_type, program_text)) |
        df["topic"].apply(lambda x: is_program_relevant(x, program_type, program_text))
    )

    if not relevant_mask.any():
        return pd.Series(0.0, index=df.index, name="fit_score")
    
    df_filtered = df[relevant_mask]

    transcript = _normalize_text_series(df_filtered["recent_video_transcript"])
    program_text_truncated = truncate_text(program_text, max_tokens=128)
    transcript_truncated = transcript.apply(lambda x: truncate_text(x, max_tokens=128))

    emb = model or _get_emb_model(emb_model_name)

    if emb is None:
        raise ValueError("Embedding model is not available.")

    prog_vec = _encode_texts([program_text_truncated], emb, batch_size=1, normalize=True)
    creator_mat = _encode_texts(transcript_truncated, emb, batch_size=batch_size, normalize=True)

    cos = (creator_mat @ prog_vec.T).ravel()

    actual_min, actual_max = cos.min(), cos.max()

    if actual_min < 0:
        cos = (cos - actual_min) / (actual_max - actual_min)

    cos = np.clip(cos, 0.0, 1.0)

    result = pd.Series(0.0, index=df.index, name="fit_score")

    result[relevant_mask] = cos

    return result


def build_features(
    df_clean: pd.DataFrame,
    program_type: str = "data_science",
    emb_model_name: str = DEFAULT_EMBEDDING_MODEL,
    model = None,
) -> Tuple[pd.DataFrame, pd.Series, Dict[str, List[str]]]:
    """
    Build EdTech-specific features for predicting qualified leads.
    
    EdTech CreatorFit features:
      - Content-program fit score (semantic similarity with APEX AI programs)
      - Creator tier classification (Established/Growing/Emerging)  
      - Language scoring (English premium, Hindi/Telugu regional)
      - Educational content validation
      - Posting consistency and engagement metrics

    Returns pre-booking features only (no data leakage).
    """
    df = df_clean.copy()

    if program_type not in ODIN_SCHOOL_PROGRAMS:
        program_type = "data_science"  # Default fallback
    program_text = ODIN_SCHOOL_PROGRAMS[program_type]

    df["fit_score"] = compute_fit_scores(
        df=df,
        program_type=program_type,
        program_text=program_text,
        emb_model_name=emb_model_name,
        model=model,
    )
    
    df = df.drop(columns=['recent_video_transcript', 'clicks', 'leads'], errors='ignore')
    
    numeric = [
        "fit_score",                      
        "posting_cadence_days",           
        "views_90d",                      
        "educational_transcript_score",   
        "transcript_length",             
        "topic_count",                   
        "edtech_topic_depth",             
        "topic",                          
        "category_tag",                   
        "language"                        
    ]
    categorical = []
    target = "qualified_leads"

    leakage_cols = {"clicks", "leads", "qualified_leads", 
                   "click_rate", "lead_rate", "qualification_rate"}
    feature_cols = set(numeric + categorical)
    if feature_cols & leakage_cols:
        raise ValueError(f"DATA LEAKAGE detected! Features overlap with outcomes: {feature_cols & leakage_cols}")

    X = df[numeric + categorical].copy()
    y = df[target].astype(float).copy()

    if X.isna().any().any():
        nan_cols = X.columns[X.isna().any()].tolist()
        raise ValueError(f"Missing values in features: {nan_cols}")

    meta = {"numeric": numeric, "categorical": categorical, "target": target}
    return X, y, meta
