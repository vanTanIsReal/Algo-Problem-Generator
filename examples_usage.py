#!/usr/bin/env python3
"""
Quick start examples for using the merged LeetCode + Codeforces dataset.
"""

import json
from pathlib import Path
from collections import defaultdict

# Configuration
MERGED_FILE = Path("dataset/merged/all_problems_merged.json")

def load_data():
    """Load the merged dataset."""
    with open(MERGED_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def example_1_basic_stats():
    """Example 1: Get basic statistics about the dataset."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Dataset Statistics")
    print("=" * 60)
    
    problems = load_data()
    
    print(f"\n✅ Total problems: {len(problems)}")
    print(f"   - Codeforces (CF_*): {sum(1 for p in problems if 'CF_' in p.get('id', ''))}")
    print(f"   - LeetCode (others): {sum(1 for p in problems if 'CF_' not in p.get('id', ''))}")
    
    # Get all unique keywords
    all_keywords = set()
    for problem in problems:
        all_keywords.update(problem.get('keywords', []))
    
    print(f"\n✅ Unique keywords/topics: {len(all_keywords)}")
    print(f"   Top 15 keywords: {sorted(all_keywords)[:15]}")

def example_2_filter_by_topic():
    """Example 2: Filter problems by specific topics."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Filter Problems by Topic")
    print("=" * 60)
    
    problems = load_data()
    
    # Find problems about graphs
    graph_problems = [p for p in problems if 'graphs' in p.get('keywords', [])]
    print(f"\n📊 Graph problems found: {len(graph_problems)}")
    for problem in graph_problems[:3]:
        print(f"\n   ID: {problem['id']}")
        print(f"   Keywords: {problem['keywords']}")
        print(f"   Text preview: {problem['problem_text'][:80]}...")
    
    # Find problems about DP
    dp_problems = [p for p in problems if 'dynamic programming' in p.get('keywords', [])]
    print(f"\n📊 Dynamic Programming problems found: {len(dp_problems)}")

def example_3_analyze_keywords():
    """Example 3: Analyze keyword distribution."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Keyword Distribution Analysis")
    print("=" * 60)
    
    problems = load_data()
    keyword_count = defaultdict(int)
    
    for problem in problems:
        for keyword in problem.get('keywords', []):
            keyword_count[keyword] += 1
    
    # Sort by frequency
    sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n📈 Top 20 most common topics:")
    for idx, (keyword, count) in enumerate(sorted_keywords[:20], 1):
        percentage = (count / len(problems)) * 100
        print(f"   {idx:2d}. {keyword:30s} - {count:4d} problems ({percentage:5.1f}%)")

def example_4_search_problems():
    """Example 4: Search for problems by text content."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Search Problems by Content")
    print("=" * 60)
    
    problems = load_data()
    
    # Search for "array" problems
    array_problems = [p for p in problems 
                      if 'array' in p.get('problem_text', '').lower()]
    
    print(f"\n🔍 Problems mentioning 'array': {len(array_problems)}")
    for problem in array_problems[:2]:
        text = problem['problem_text']
        print(f"\n   ID: {problem['id']}")
        print(f"   Preview: {text[:100]}...")

def example_5_compare_sources():
    """Example 5: Compare Codeforces vs LeetCode problems."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Codeforces vs LeetCode Comparison")
    print("=" * 60)
    
    problems = load_data()
    
    codeforces = [p for p in problems if 'CF_' in p.get('id', '')]
    leetcode = [p for p in problems if 'CF_' not in p.get('id', '')]
    
    print(f"\n📊 Dataset Breakdown:")
    print(f"   - Codeforces: {len(codeforces)} problems ({len(codeforces)*100//len(problems)}%)")
    print(f"   - LeetCode: {len(leetcode)} problems ({len(leetcode)*100//len(problems)}%)")
    
    # Keywords in each source
    cf_keywords = defaultdict(int)
    lc_keywords = defaultdict(int)
    
    for p in codeforces:
        for kw in p.get('keywords', []):
            cf_keywords[kw] += 1
    
    for p in leetcode:
        for kw in p.get('keywords', []):
            lc_keywords[kw] += 1
    
    print(f"\n🏆 Most common topics in Codeforces:")
    for kw, count in sorted(cf_keywords.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {kw}: {count} problems")
    
    print(f"\n🏆 Most common topics in LeetCode:")
    for kw, count in sorted(lc_keywords.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {kw}: {count} problems")

def example_6_export_subset():
    """Example 6: Export a subset of problems."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Export Subset (Easy example)")
    print("=" * 60)
    
    problems = load_data()
    
    # Get first 10 problems
    subset = problems[:10]
    
    # Save to new file
    output_file = Path("dataset/merged/sample_10_problems.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(subset, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Exported {len(subset)} problems to: {output_file}")
    print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎓 MERGED LEETCODE + CODEFORCES DATASET - QUICK START EXAMPLES")
    print("=" * 60)
    
    try:
        # Run all examples
        example_1_basic_stats()
        example_2_filter_by_topic()
        example_3_analyze_keywords()
        example_4_search_problems()
        example_5_compare_sources()
        example_6_export_subset()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
    except FileNotFoundError:
        print(f"❌ Dataset file not found: {MERGED_FILE}")
        print("   Please run merge_datasets.py first")
    except Exception as e:
        print(f"❌ Error: {e}")
