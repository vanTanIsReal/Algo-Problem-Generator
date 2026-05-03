#!/usr/bin/env python3
"""
Script to translate problem texts to Vietnamese using deep-translator.
"""

import json
import time
from pathlib import Path
from deep_translator import GoogleTranslator

# Configuration
MERGED_FILE = Path("dataset/merged/all_problems_merged.json")
OUTPUT_FILE = Path("dataset/merged/all_problems_translated_vi.json")
BATCH_SIZE = 10  # Process and save every N items
SLEEP_TIME = 1   # Sleep between batches to avoid rate limiting

print(f"📖 Loading merged dataset from: {MERGED_FILE}")

try:
    with open(MERGED_FILE, 'r', encoding='utf-8') as f:
        problems = json.load(f)
    print(f"✅ Loaded {len(problems)} problems")
except Exception as e:
    print(f"❌ Error loading file: {e}")
    exit(1)

# Initialize translator (English to Vietnamese)
translator = GoogleTranslator(source_language='en', target_language='vi')
translated_problems = []

print(f"\n🔄 Translating problem texts to Vietnamese...\n")

for idx, problem in enumerate(problems, 1):
    try:
        # Create a copy to avoid modifying original
        translated_problem = problem.copy()
        
        # Translate problem_text if it exists
        if 'problem_text' in problem and problem['problem_text']:
            # Limit translation to first 5000 chars to avoid API issues
            text_to_translate = problem['problem_text'][:5000]
            try:
                translated_text = translator.translate(text_to_translate)
                translated_problem['problem_text_vi'] = translated_text
                status = "✅"
            except Exception as e:
                print(f"   ⚠️  Error translating problem {problem.get('id', 'unknown')}: {e}")
                translated_problem['problem_text_vi'] = None
                status = "⚠️"
        
        translated_problems.append(translated_problem)
        
        # Print progress every BATCH_SIZE items
        if idx % BATCH_SIZE == 0:
            print(f"{status} Translated {idx}/{len(problems)} problems")
        
        # Rate limiting
        if idx % BATCH_SIZE == 0:
            print(f"   ⏸️  Waiting {SLEEP_TIME}s to avoid rate limiting...")
            time.sleep(SLEEP_TIME)
    
    except Exception as e:
        print(f"❌ Error processing problem {idx}: {e}")
        translated_problems.append(problem)

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
print(f"\n📊 Translation Summary:")
print(f"   - Total problems: {len(translated_problems)}")
translated_count = sum(1 for p in translated_problems if 'problem_text_vi' in p and p['problem_text_vi'])
print(f"   - Successfully translated: {translated_count}")
print(f"   - Failed translations: {len(translated_problems) - translated_count}")

print(f"\n🎉 Translation complete!")
print(f"   Output file: {OUTPUT_FILE}")
