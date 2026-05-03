#!/usr/bin/env python3
"""
Parallel translation script - much faster for large datasets.
Uses concurrent translation to speed up the process.
"""

import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator

# Configuration
MERGED_FILE = Path("dataset/merged/all_problems_merged.json")
OUTPUT_FILE = Path("dataset/merged/all_problems_translated_vi_parallel.json")
MAX_WORKERS = 3  # Number of parallel translation threads
BATCH_SAVE = 100  # Save every N items

def translate_problem(problem, translator):
    """Translate a single problem's text."""
    try:
        translated_problem = problem.copy()
        
        if 'problem_text' in problem and problem['problem_text']:
            text_to_translate = problem['problem_text'][:5000]
            try:
                translated_text = translator.translate(text_to_translate)
                translated_problem['problem_text_vi'] = translated_text
                return translated_problem, True
            except Exception as e:
                print(f"   ⚠️  Error translating {problem.get('id', 'unknown')}: {str(e)[:50]}")
                translated_problem['problem_text_vi'] = None
                return translated_problem, False
        
        return translated_problem, False
    except Exception as e:
        print(f"   ❌ Failed to process {problem.get('id', 'unknown')}")
        return problem, False

def main():
    print(f"📖 Loading merged dataset from: {MERGED_FILE}")
    
    try:
        with open(MERGED_FILE, 'r', encoding='utf-8') as f:
            problems = json.load(f)
        print(f"✅ Loaded {len(problems)} problems")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        exit(1)
    
    print(f"\n🔄 Starting parallel translation (using {MAX_WORKERS} workers)...\n")
    
    # Create translator instance (will be reused in threads)
    translator = GoogleTranslator(source_language='en', target_language='vi')
    
    translated_problems = [None] * len(problems)
    successful_translations = 0
    start_time = time.time()
    
    # Process with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(translate_problem, problem, translator): idx 
            for idx, problem in enumerate(problems)
        }
        
        # Process completed translations
        for completed_count, future in enumerate(as_completed(future_to_index), 1):
            idx = future_to_index[future]
            try:
                translated_problem, success = future.result()
                translated_problems[idx] = translated_problem
                if success:
                    successful_translations += 1
                
                # Print progress every BATCH_SAVE items
                if completed_count % BATCH_SAVE == 0:
                    elapsed = time.time() - start_time
                    rate = completed_count / elapsed
                    remaining = (len(problems) - completed_count) / rate if rate > 0 else 0
                    print(f"✅ Progress: {completed_count}/{len(problems)} ({completed_count*100//len(problems)}%) | "
                          f"Time: {elapsed:.0f}s | ETA: {remaining:.0f}s")
            except Exception as e:
                print(f"❌ Error processing item {idx}: {e}")
                translated_problems[idx] = problems[idx]
    
    # Save translated data
    print(f"\n💾 Saving translated dataset to: {OUTPUT_FILE}")
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(translated_problems, f, ensure_ascii=False, indent=2)
        print(f"✅ Translated dataset saved successfully!")
    except Exception as e:
        print(f"❌ Error saving translated data: {e}")
        exit(1)
    
    # Summary
    elapsed_time = time.time() - start_time
    print(f"\n📊 Translation Summary:")
    print(f"   - Total problems: {len(translated_problems)}")
    print(f"   - Successfully translated: {successful_translations}")
    print(f"   - Failed translations: {len(translated_problems) - successful_translations}")
    print(f"   - Total time: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)")
    print(f"   - Average rate: {len(translated_problems)/elapsed_time:.1f} problems/second")
    
    print(f"\n🎉 Parallel translation complete!")

if __name__ == "__main__":
    main()
