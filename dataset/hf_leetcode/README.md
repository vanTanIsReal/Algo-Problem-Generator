---
license: mit
task_categories:
- table-question-answering
- text-classification
- zero-shot-classification
- feature-extraction
- text2text-generation
- text-generation
language:
- en
tags:
- code
- AI
- ML
- NLP
- LLM
size_categories:
- 1K<n<10K
dataset_info:
- config_name: default
  features:
  - name: user_queries
    dtype: string
  - name: expected_output
    dtype: string
  splits:
  - name: train
    num_bytes: 5900495
    num_examples: 2823
  download_size: 1645957
  dataset_size: 5900495
- config_name: instructions_problem_evaluator
  features:
  - name: user_queries
    dtype: string
  - name: expected_output
    dtype: string
  - name: __index_level_0__
    dtype: int64
  splits:
  - name: train
    num_bytes: 5923079
    num_examples: 2823
  download_size: 1661740
  dataset_size: 5923079
- config_name: problem_evaluator
  features:
  - name: user_queries
    dtype: string
  - name: expected_output
    dtype: string
  - name: __index_level_0__
    dtype: int64
  splits:
  - name: train
    num_bytes: 5923079
    num_examples: 2823
  download_size: 1661740
  dataset_size: 5923079
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
- config_name: instructions_problem_evaluator
  data_files:
  - split: train
    path: instructions_problem_evaluator/train-*
- config_name: problem_evaluator
  data_files:
  - split: train
    path: problem_evaluator/train-*
---

# LeetCode Problems Dataset

This dataset contains a comprehensive collection of LeetCode programming problems along with their features, metadata, and instructions.

---

## Attribution

This dataset is derived from multiple sources:
1. LeetCode's website (https://leetcode.com) — All problem content, solutions, and related materials are the property of LeetCode and are those that are available publicly (No premium problem is shared!).
2. LeetCodeHelp (https://leetcodehelp.github.io) — Additional solution code and explanations.

This dataset is provided for educational and research purposes only. Please refer to LeetCode's Terms of Service and Copyright Policy for more information.

Original Sources:
- [LeetCode](https://leetcode.com)
- [LeetCodeHelp](https://leetcodehelp.github.io)

---

## Repository Structure

```
.
├── data/                               # Parquet data for instruction-based evaluation 
│   └── train-00000-of-00001.parquet
├── raw_data/                           # Raw data files for manual use
│   ├── leetcode_instructions_problem_evaluator.csv
│   ├── leetcode_problems.csv
│   └── leetcode_problems.json
├── .gitattributes
└── README.md
```

---

## Datasets
This repository provides multiple ways to access the data:

#### 1. Instruction Problem Evaluator (LLM Fine-tuning)
- **Location:** `data/train-00000-of-00001.parquet`
- **Fields:** `user_queries`, `expected_output`
- **Purpose:** For training and evaluating LLMs on problem understanding and meta-reasoning
This dataset contains ~2823 instructions with corresponding output. The instructions are all ready to be fed to the model, if the task you want to work on is the same as the instructions defined here.
No further preprocessing is required on this dataset. Having said that, these instructions are based on the main crawled data, which are available at `raw_data/` directory.

> If you want to apply or study different instructions, all you have to do is to clone the raw_data, do the preprocessing and then define your own instructions. This [notebook at kaggle](https://www.kaggle.com/code/alishohadaee/leetcode-dataset-introduction) helps you get started with preprocessing. 

Now, to use these instructions, first make sure `datasets` is installed and up to date:
```python
pip install -U datasets
```

then, load the instructions with:
```python
from datasets import load_dataset
ds = load_dataset("alishohadaee/leetcode-problems-dataset")
```

When you load the dataset using `datasets` library, this instruction dataset will be loaded to your machine, not the raw(original) data.

#### 2. Raw Data Access
Located in the `raw_data/` directory, you can find:
- `leetcode_problems.csv` and `leetcode_problems.json` - Complete, original, crawled dataset with all fields
- `leetcode_instructions_problem_evaluator.csv` - Instruction-based evaluation pairs (discussed earlier, this is its .csv file)

## Dataset's Fields
In the original dataset you will find the following columns

- `frontendQuestionId`: The ID of the problem on LeetCode
- `title`: The title of the problem
- `titleSlug`: URL-friendly version of the title
- `url`: URL to the problem in LeetCode
- `description`: Full problem description in HTML format 
- `description_url`: URL to the problem description
- `difficulty`: Problem difficulty level (Easy, Medium, Hard)
- `paidOnly`: Boolean indicating if the problem is premium
- `category`: Problem category (e.g., "Algorithms")
- `hints`: List of hints provided for the problem by the LC
- `solution`: Detailed solution explanation with approaches and complexity analysis
- `solution_url`: URL to the problem solutions (Null value corresponds to premium solutions, this is the url to the original solution published officially by LC)
- `acceptance_rate`: Problem acceptance rate
- `topics`: List of related topics/tags
- `likes`: Number of likes
- `dislikes`: Number of dislikes
- `stats`: Detailed statistics including total accepted submissions and total submissions
- `similar_questions`: List of related problems
- `solution_code_url`: URL to the solution code (This the URL to the second source (`leetcodehelp.github.io`) used for retrieving Python, Java, and CPP solutions.)
- `solution_code_python`: Python solution code
- `solution_code_java`: Java solution code
- `solution_code_cpp`: C++ solution code

### Citation
If you use this dataset in your research, please cite:

```bibtex
@misc{leetcode_problems_dataset,
  author = {Seyedali Shohadaeolhosseini},
  title = {LeetCode Problems Dataset},
  year = {2025},
  publisher = {Hugging Face},
  journal = {Hugging Face Hub},
  howpublished = {\url{https://huggingface.co/datasets/Alishohadaee/leetcode-problems-dataset}}
}

@misc{leetcode,
  author = {LeetCode},
  title = {LeetCode - The World's Leading Online Programming Learning Platform},
  year = {2025},
  publisher = {LeetCode},
  howpublished = {\url{https://leetcode.com}}
}

@misc{leetcodehelp,
  author = {LeetCodeHelp},
  title = {LeetCode Solutions},
  year = {2025},
  publisher = {LeetCodeHelp},
  howpublished = {\url{https://leetcodehelp.github.io}}
}
```

## Usage
This dataset can be used for:
- Training language models for programming interview preparation
- Fine-tuning models for code generation and problem evaluation
- Research in programming education
- Development of coding assistance tools
- Analysis of programming problem patterns and difficulty
- Study of solution approaches and their effectiveness
- Evaluating a problem based on its description

### Updates and Versions
- Version 1.0.0 (Initial release)
  - Date: May 18, 2025
  - Description: Initial dataset release with comprehensive problem data and instruction-based evaluation pairs
