#!/usr/bin/env python3
"""
Check translation progress and dataset statistics.
Run this anytime to monitor the translation process.
"""

import json
import time
from pathlib import Path

def check_progress():
    """Check translation progress."""
    print("=" * 70)
    print("📊 TRANSLATION PROGRESS CHECKER")
    print("=" * 70)
    
    merged_file = Path("dataset/merged/all_problems_merged.json")
    translated_file = Path("dataset/merged/all_problems_translated_vi.json")
    
    # Check merged file
    if merged_file.exists():
        with open(merged_file, 'r', encoding='utf-8') as f:
            merged_problems = json.load(f)
        print(f"\n✅ Merged dataset loaded:")
        print(f"   - Total problems: {len(merged_problems)}")
        print(f"   - File size: {merged_file.stat().st_size / (1024*1024):.1f} MB")
    else:
        print(f"\n❌ Merged file not found: {merged_file}")
        return
    
    # Check translation progress
    if translated_file.exists():
        file_size = translated_file.stat().st_size / (1024*1024)
        print(f"\n🔄 Translation in progress:")
        print(f"   - File size: {file_size:.1f} MB")
        
        # Try to load and count
        try:
            with open(translated_file, 'r', encoding='utf-8') as f:
                # Read line by line to avoid loading massive file
                line_count = 0
                for line in f:
                    if line.strip().startswith('"id"'):
                        line_count += 1
            
            # Estimate based on file structure
            translated_count = sum(1 for p in json.load(open(translated_file)) 
                                  if 'problem_text_vi' in p and p['problem_text_vi'])
            
            progress = (translated_count / len(merged_problems)) * 100
            
            print(f"   - Translated problems: {translated_count}/{len(merged_problems)}")
            print(f"   - Progress: {progress:.1f}%")
            
            # Progress bar
            bar_length = 50
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"   [{bar}] {progress:.1f}%")
            
        except Exception as e:
            print(f"   - Unable to read full file (still processing): {str(e)[:50]}")
            print(f"   - File size suggests: {file_size / 46 * 100:.1f}% complete (estimate)")
    else:
        print(f"\n⏳ Translation not started yet")
        print(f"   - Start translation: python translate_dataset.py")
    
    # Dataset info
    print(f"\n📈 Dataset Breakdown:")
    cf_count = sum(1 for p in merged_problems if 'CF_' in p.get('id', ''))
    lc_count = len(merged_problems) - cf_count
    print(f"   - Codeforces: {cf_count} ({cf_count*100//len(merged_problems)}%)")
    print(f"   - LeetCode: {lc_count} ({lc_count*100//len(merged_problems)}%)")
    
    # Keyword stats
    print(f"\n🏷️  Keyword Statistics:")
    keyword_counts = {}
    for p in merged_problems:
        for kw in p.get('keywords', []):
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
    
    sorted_kw = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (kw, count) in enumerate(sorted_kw[:5], 1):
        pct = (count / len(merged_problems)) * 100
        print(f"   {i}. {kw}: {count} ({pct:.1f}%)")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        check_progress()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to run this from the project root directory")
