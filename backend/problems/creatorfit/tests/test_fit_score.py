# Expected Results Validation
# For your educational content matching:

# High fit (0.7-0.9): "React tutorial" vs "React development course"
# Medium fit (0.4-0.6): "Web development" vs "JavaScript basics"
# Low fit (0.0-0.3): "Python programming" vs "Fitness content"

# If you're not seeing this pattern, the issue is likely in text preprocessing or model choice.

from __future__ import annotations

import numpy as np
import pandas as pd
import re
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer

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
    "python_programming": """
    Complete Python programming bootcamp covering basics syntax variables functions,
    object-oriented programming classes inheritance, data structures lists dictionaries,
    algorithms problem solving, web frameworks Django Flask, automation scripting,
    testing debugging, project development, Python developer career advice
    """,
    "career_guidance": """
    Technical career guidance covering software engineering interview preparation,
    coding practice algorithms data structures, system design concepts,
    resume building portfolio development, job search strategies,
    salary negotiation, career progression in tech industry
    """
}

# Test video transcripts - realistic educational content
TEST_TRANSCRIPTS = {
    "perfect_data_science": """
    Hey everyone! Today we're diving deep into Python for data science. 
    I'll show you how to use pandas for data manipulation, numpy for numerical computations,
    and we'll build a complete machine learning model using scikit-learn.
    First, let's import pandas and load our dataset. We'll clean the data,
    handle missing values, and then visualize patterns using matplotlib.
    After that, we'll train a neural network for prediction. This is perfect
    for anyone looking to break into data science careers. Don't forget to
    practice statistics concepts as they're crucial for understanding ML algorithms.
    """,
    
    "good_web_development": """
    Welcome back to my channel! In this tutorial, we're building a full-stack
    React application with Node.js backend. We'll cover React hooks, state management,
    and how to connect to our Express API. I'll show you how to handle user authentication,
    database integration with MongoDB, and deploy everything to production.
    This project will give you real-world experience that employers are looking for.
    Perfect for frontend and backend developers wanting to level up their skills.
    """,
    
    "moderate_python": """
    What's up everyone! Today I'm teaching Python basics for beginners.
    We'll cover variables, functions, and loops. Then we'll move to more advanced
    topics like classes and object-oriented programming. I'll also show you
    some cool automation scripts you can build. Python is great for web development
    too - we might touch on Django in future videos. Great for career development!
    """,
    
    "poor_match_fitness": """
    Hey fitness enthusiasts! Today we're talking about the best workout routines
    for building muscle mass. I'll show you proper form for deadlifts,
    squats, and bench press. Nutrition is also crucial - make sure you're
    getting enough protein and calories. Remember to track your progress
    and stay consistent. Let's get those gains! Don't forget to warm up properly.
    """,
    
    "mixed_career_tech": """
    In today's video, I'm sharing career advice for software engineers.
    We'll discuss how to prepare for technical interviews, practice coding challenges,
    and what recruiters are really looking for. I'll also cover salary negotiation
    tips and how to build a strong portfolio. Whether you're learning JavaScript,
    Python, or any other technology, these principles apply universally.
    """
}

def clean_text_enhanced(text: str) -> str:
    """Enhanced text preprocessing for better semantic matching."""
    if not text or pd.isna(text):
        return ""
    
    # Convert to string and lowercase
    text = str(text).lower()
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common filler words that don't add semantic value
    text = re.sub(r'\b(um|uh|like|you know|basically|actually|hey|what\'s up|welcome back)\b', '', text)
    
    # Remove special characters but keep punctuation for context
    text = re.sub(r'[^\w\s.,!?-]', ' ', text)
    
    # Remove excessive punctuation
    text = re.sub(r'[.!?]{2,}', '.', text)
    
    return text.strip()

def truncate_text_intelligently(text: str, max_tokens: int = 128) -> str:
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

def validate_embeddings(model: SentenceTransformer, sample_texts: List[str]) -> None:
    """Validate that embeddings make sense."""
    print("\n" + "="*60)
    print("🔍 EMBEDDING VALIDATION")
    print("="*60)
    
    embeddings = model.encode(sample_texts, normalize_embeddings=True)
    
    # Check embedding properties
    print(f"📊 Embedding shape: {embeddings.shape}")
    norms = np.linalg.norm(embeddings, axis=1)
    print(f"📏 Embedding norm range: [{norms.min():.4f}, {norms.max():.4f}]")
    print(f"🎯 Expected norm for normalized embeddings: ~1.0")
    
    # Test with identical texts (should be 1.0)
    identical_sim = np.dot(embeddings[0], embeddings[0])
    print(f"🔄 Identical text similarity: {identical_sim:.4f} (should be 1.0)")
    
    # Test completely different texts (should be low)
    if len(embeddings) > 1:
        different_sim = np.dot(embeddings[0], embeddings[-1])
        print(f"❌ Different text similarity: {different_sim:.4f} (should be <0.5)")

def compute_similarity_with_debug(
    creator_text: str, 
    program_text: str, 
    model: SentenceTransformer,
    preprocess: bool = True,
    truncate: bool = True
) -> Tuple[float, Dict]:
    """
    Compute similarity with detailed debugging information.
    """
    # Preprocessing
    if preprocess:
        creator_clean = clean_text_enhanced(creator_text)
        program_clean = clean_text_enhanced(program_text)
    else:
        creator_clean = creator_text
        program_clean = program_text
    
    # Truncation
    if truncate:
        creator_final = truncate_text_intelligently(creator_clean, max_tokens=128)
        program_final = truncate_text_intelligently(program_clean, max_tokens=128)
    else:
        creator_final = creator_clean
        program_final = program_clean
    
    # Get embeddings
    creator_emb = model.encode([creator_final], normalize_embeddings=True)
    program_emb = model.encode([program_final], normalize_embeddings=True)
    
    # Calculate similarity
    similarity = np.dot(creator_emb[0], program_emb[0])
    
    # Debug info
    debug_info = {
        'creator_original_length': len(creator_text.split()),
        'creator_processed_length': len(creator_final.split()),
        'program_original_length': len(program_text.split()),
        'program_processed_length': len(program_final.split()),
        'creator_processed': creator_final[:100] + "..." if len(creator_final) > 100 else creator_final,
        'program_processed': program_final[:100] + "..." if len(program_final) > 100 else program_final,
        'embedding_norms': (np.linalg.norm(creator_emb), np.linalg.norm(program_emb)),
    }
    
    return similarity, debug_info

def test_model_comparison():
    """Compare different models on the same data."""
    print("\n" + "="*60)
    print("🏆 MODEL COMPARISON")
    print("="*60)
    
    models_to_test = [
        "sentence-transformers/all-MiniLM-L12-v2",  # Current model
        "sentence-transformers/all-mpnet-base-v2",   # Recommended upgrade
        "sentence-transformers/all-MiniLM-L6-v2",    # Faster alternative
    ]
    
    test_pairs = [
        (TEST_TRANSCRIPTS["perfect_data_science"], ODIN_SCHOOL_PROGRAMS["data_science"], "Expected: HIGH"),
        (TEST_TRANSCRIPTS["good_web_development"], ODIN_SCHOOL_PROGRAMS["web_development"], "Expected: HIGH"),
        (TEST_TRANSCRIPTS["poor_match_fitness"], ODIN_SCHOOL_PROGRAMS["data_science"], "Expected: LOW"),
    ]
    
    results = {}
    
    for model_name in models_to_test:
        print(f"\n🤖 Testing model: {model_name}")
        try:
            model = SentenceTransformer(model_name)
            model_results = []
            
            for creator_text, program_text, expected in test_pairs:
                similarity, _ = compute_similarity_with_debug(creator_text, program_text, model)
                model_results.append(similarity)
                print(f"   {expected}: {similarity:.4f}")
            
            results[model_name] = model_results
            
        except Exception as e:
            print(f"   ❌ Error loading model: {e}")
            results[model_name] = [0.0, 0.0, 0.0]
    
    return results

def detailed_debugging_test():
    """Comprehensive debugging of fit score calculation."""
    print("\n" + "="*60)
    print("🔧 DETAILED DEBUGGING TEST")
    print("="*60)
    
    # Test with recommended model
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    
    # Validate embeddings first
    sample_texts = list(TEST_TRANSCRIPTS.values())[:3]
    validate_embeddings(model, sample_texts)
    
    # Test each transcript against each program
    programs = ODIN_SCHOOL_PROGRAMS
    transcripts = TEST_TRANSCRIPTS
    
    print(f"\n📋 SIMILARITY MATRIX")
    print("="*60)
    
    # Create similarity matrix
    results_matrix = []
    
    for transcript_name, transcript_text in transcripts.items():
        row = []
        print(f"\n🎥 Testing: {transcript_name}")
        
        for program_name, program_text in programs.items():
            similarity, debug_info = compute_similarity_with_debug(
                transcript_text, program_text, model
            )
            row.append(similarity)
            
            print(f"  📚 {program_name:<20}: {similarity:.4f}")
            if similarity > 0.6:
                print(f"      ✅ GOOD MATCH")
            elif similarity > 0.4:
                print(f"      ⚠️  MODERATE MATCH")
            else:
                print(f"      ❌ POOR MATCH")
        
        results_matrix.append(row)
    
    # Display as DataFrame for better visualization
    df_results = pd.DataFrame(
        results_matrix,
        index=list(transcripts.keys()),
        columns=list(programs.keys())
    )
    
    print(f"\n📊 SIMILARITY MATRIX SUMMARY")
    print("="*60)
    print(df_results.round(4))
    
    return df_results

def test_preprocessing_impact():
    """Test impact of different preprocessing approaches."""
    print("\n" + "="*60)
    print("🧹 PREPROCESSING IMPACT TEST")
    print("="*60)
    
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    
    test_text = TEST_TRANSCRIPTS["perfect_data_science"]
    program_text = ODIN_SCHOOL_PROGRAMS["data_science"]
    
    print("Testing preprocessing impact on similarity scores:")
    
    # Test 1: No preprocessing
    sim_raw, _ = compute_similarity_with_debug(
        test_text, program_text, model, preprocess=False, truncate=False
    )
    print(f"1️⃣  Raw text (no preprocessing): {sim_raw:.4f}")
    
    # Test 2: Only cleaning
    sim_clean, _ = compute_similarity_with_debug(
        test_text, program_text, model, preprocess=True, truncate=False
    )
    print(f"2️⃣  Cleaned text: {sim_clean:.4f}")
    
    # Test 3: Cleaning + truncation
    sim_full, _ = compute_similarity_with_debug(
        test_text, program_text, model, preprocess=True, truncate=True
    )
    print(f"3️⃣  Cleaned + truncated: {sim_full:.4f}")
    
    # Analysis
    print(f"\n📈 PREPROCESSING IMPACT:")
    print(f"   Cleaning impact: {abs(sim_clean - sim_raw):.4f}")
    print(f"   Truncation impact: {abs(sim_full - sim_clean):.4f}")
    
    return {
        'raw': sim_raw,
        'cleaned': sim_clean, 
        'full_processed': sim_full
    }

def test_edge_cases():
    """Test edge cases and potential failure points."""
    print("\n" + "="*60)
    print("⚠️  EDGE CASE TESTING")
    print("="*60)
    
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    
    edge_cases = {
        "empty_transcript": "",
        "very_short": "Python tutorial",
        "very_long": " ".join(["This is a very long transcript about Python programming."] * 50),
        "special_chars": "Python 🐍 programming! #coding @python $variables %data &analysis *machine learning*",
        "mixed_language": "Python programming tutorial हिंदी में explaining data science concepts తెలుగులో",
        "numbers_only": "12345 67890 2024 100 500 1000",
        "repeated_words": "Python Python Python data data science science machine learning learning"
    }
    
    program_text = ODIN_SCHOOL_PROGRAMS["data_science"]
    
    for case_name, transcript in edge_cases.items():
        try:
            similarity, debug_info = compute_similarity_with_debug(
                transcript, program_text, model
            )
            print(f"🧪 {case_name:<20}: {similarity:.4f}")
            
            if case_name == "empty_transcript" and similarity > 0.1:
                print(f"   ⚠️  WARNING: Empty text has unexpectedly high similarity!")
            elif case_name == "very_long":
                print(f"   📏 Length: {debug_info['creator_original_length']} -> {debug_info['creator_processed_length']} words")
                
        except Exception as e:
            print(f"❌ {case_name:<20}: ERROR - {e}")

def benchmark_performance():
    """Benchmark processing speed and memory usage."""
    print("\n" + "="*60)
    print("⚡ PERFORMANCE BENCHMARK")
    print("="*60)
    
    import time
    
    models_to_benchmark = [
        "sentence-transformers/all-MiniLM-L12-v2",  # Current
        "sentence-transformers/all-mpnet-base-v2",   # Recommended
        "sentence-transformers/all-MiniLM-L6-v2",    # Fast alternative
    ]
    
    test_texts = list(TEST_TRANSCRIPTS.values())
    program_text = ODIN_SCHOOL_PROGRAMS["data_science"]
    
    for model_name in models_to_benchmark:
        print(f"\n🏃 Benchmarking: {model_name}")
        try:
            # Load model
            start_time = time.time()
            model = SentenceTransformer(model_name)
            load_time = time.time() - start_time
            
            # Process texts
            start_time = time.time()
            for text in test_texts:
                compute_similarity_with_debug(text, program_text, model)
            process_time = time.time() - start_time
            
            print(f"   📥 Model load time: {load_time:.2f}s")
            print(f"   ⚡ Processing time: {process_time:.2f}s ({len(test_texts)} texts)")
            print(f"   📊 Avg per text: {process_time/len(test_texts):.3f}s")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

def validate_expected_results():
    """Validate that results meet expected patterns."""
    print("\n" + "="*60)
    print("✅ RESULT VALIDATION")
    print("="*60)
    
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    
    # Define expected patterns
    expected_patterns = [
        # (transcript_key, program_key, expected_range, description)
        ("perfect_data_science", "data_science", (0.7, 1.0), "Perfect match should be HIGH"),
        ("good_web_development", "web_development", (0.6, 0.9), "Good match should be HIGH-MEDIUM"),
        ("moderate_python", "python_programming", (0.5, 0.8), "Moderate match should be MEDIUM"),
        ("poor_match_fitness", "data_science", (0.0, 0.3), "Poor match should be LOW"),
        ("mixed_career_tech", "career_guidance", (0.4, 0.7), "Career content should match moderately"),
    ]
    
    validation_results = []
    
    for transcript_key, program_key, (min_expected, max_expected), description in expected_patterns:
        transcript = TEST_TRANSCRIPTS[transcript_key]
        program = ODIN_SCHOOL_PROGRAMS[program_key]
        
        similarity, _ = compute_similarity_with_debug(transcript, program, model)
        
        is_valid = min_expected <= similarity <= max_expected
        status = "✅ PASS" if is_valid else "❌ FAIL"
        
        print(f"{status} {description}")
        print(f"     Expected: [{min_expected:.2f}, {max_expected:.2f}] | Actual: {similarity:.4f}")
        
        validation_results.append({
            'test': description,
            'expected_min': min_expected,
            'expected_max': max_expected,
            'actual': similarity,
            'passed': is_valid
        })
    
    # Summary
    passed_tests = sum(1 for r in validation_results if r['passed'])
    total_tests = len(validation_results)
    
    print(f"\n📋 VALIDATION SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests < total_tests:
        print("❌ Some tests failed - investigate model choice or preprocessing!")
    else:
        print("✅ All tests passed - model is working correctly!")
    
    return validation_results

def run_comprehensive_test():
    """Run all test functions in sequence."""
    print("🚀 STARTING COMPREHENSIVE FIT SCORE TESTING")
    print("="*80)
    
    try:
        # Step 1: Model comparison
        print("Step 1: Comparing different models...")
        model_comparison = test_model_comparison()
        
        # Step 2: Detailed debugging  
        print("\nStep 2: Running detailed debugging...")
        detailed_results = detailed_debugging_test()
        
        # Step 3: Preprocessing impact
        print("\nStep 3: Testing preprocessing impact...")
        preprocessing_results = test_preprocessing_impact()
        
        # Step 4: Edge cases
        print("\nStep 4: Testing edge cases...")
        test_edge_cases()
        
        # Step 5: Performance benchmark
        print("\nStep 5: Performance benchmarking...")
        benchmark_performance()
        
        # Step 6: Result validation
        print("\nStep 6: Validating expected results...")
        validation_results = validate_expected_results()
        
        # Final recommendations
        print("\n" + "="*80)
        print("🎯 FINAL RECOMMENDATIONS")
        print("="*80)
        
        # Analyze results and provide recommendations
        passed_validation = sum(1 for r in validation_results if r['passed'])
        total_validation = len(validation_results)
        
        if passed_validation < total_validation:
            print("❌ ISSUES DETECTED:")
            print("   1. Consider switching to all-mpnet-base-v2 model")
            print("   2. Implement enhanced text preprocessing")
            print("   3. Add intelligent truncation for long texts")
            print("   4. Review cosine similarity range mapping")
        else:
            print("✅ FIT SCORE CALCULATION IS WORKING CORRECTLY!")
            print("   Your model and preprocessing are producing expected results.")
        
        return {
            'model_comparison': model_comparison,
            'detailed_results': detailed_results,
            'preprocessing_results': preprocessing_results,
            'validation_results': validation_results
        }
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        raise

def test_current_codebase_integration():
    """Test integration with your current features.py functions."""
    print("\n" + "="*60)
    print("🔗 CODEBASE INTEGRATION TEST")
    print("="*60)
    
    # Create test DataFrame similar to your CSV format
    test_data = {
        'creator_id': ['EDU_0001', 'EDU_0002', 'EDU_0003', 'EDU_0004', 'EDU_0005'],
        'topic': ['Python;Data Science', 'React;Node.js', 'Python', 'Fitness', 'Career;Programming'],
        'recent_video_transcript': list(TEST_TRANSCRIPTS.values()),
        'posting_cadence_days': [5, 7, 3, 4, 6],
        'views_90d': [37705, 3801, 15000, 8000, 25000],
        'clicks': [1698, 194, 800, 400, 1200],
        'leads': [296, 21, 120, 60, 180],
        'qualified_leads': [226, 16, 90, 45, 135],
        'enrollments': [197, 7, 75, 38, 110],
        'refunds': [7, 0, 3, 2, 5],
        'geography': ['INDIA'] * 5,
        'language': ['English', 'Telugu', 'English', 'English', 'English'],
        'category_tag': ['beginner-friendly', 'quick-start', 'comprehensive', 'lifestyle', 'career-focused']
    }
    
    df_test = pd.DataFrame(test_data)
    
    print("📊 Test DataFrame created:")
    print(df_test[['creator_id', 'topic', 'language']].to_string(index=False))
    
    # Test different program types
    for program_type in ['data_science', 'web_development', 'python_programming', 'career_guidance']:
        print(f"\n🎯 Testing program: {program_type}")
        
        try:
            # Simulate your compute_fit_scores function
            program_text = ODIN_SCHOOL_PROGRAMS[program_type]
            model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
            
            # Process transcripts
            texts = df_test["recent_video_transcript"].apply(clean_text_enhanced)
            
            # Get embeddings
            prog_vec = model.encode([program_text], normalize_embeddings=True)
            creator_mat = model.encode(texts.tolist(), normalize_embeddings=True)
            
            # Compute similarities
            cos = (creator_mat @ prog_vec.T).ravel()
            
            # Add to DataFrame
            df_test[f'fit_score_{program_type}'] = cos
            
            print(f"   Fit scores: {cos.round(4)}")
            print(f"   Range: [{cos.min():.4f}, {cos.max():.4f}]")
            print(f"   Best match: {df_test.loc[cos.argmax(), 'creator_id']} ({cos.max():.4f})")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return df_test

if __name__ == "__main__":
    print("🧪 STARTING FIT SCORE COMPREHENSIVE TESTING")
    print("="*80)
    
    # Check if sentence-transformers is available
    try:
        import sentence_transformers
        print("✅ sentence-transformers library available")
    except ImportError:
        print("❌ sentence-transformers not installed. Run: pip install sentence-transformers")
        exit(1)
    
    # Run all tests
    try:
        results = run_comprehensive_test()
        
        # Integration test
        integration_results = test_current_codebase_integration()
        
        print("\n" + "="*80)
        print("🏁 TESTING COMPLETE!")
        print("="*80)
        print("Check the output above for specific recommendations.")
        print("If validation tests failed, implement the suggested improvements.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()