# Markdown File Guidelines


## Purpose and Scope
- Create, edit, and generate markdown (`.md`) files


## General Principles
- **Clarity**: Write in simple, precise, and concise language.
- **Consistency**: Maintain a uniform style across sections.
- **Structure First**: Always design the document hierarchy before filling in details.
- **Self-Contained**: Each .md file should be understandable without external references (unless explicitly intended).


## File Structure
- **Title/Header**: Always start with a single # Title.
- **Sections**: Use hierarchical headers (##, ###, etc.) consistently.


## Formatting Rules
- **Headings**: Use `#` levels properly (never skip levels, e.g., don't jump from `##` to `####`).
- **Paragraphs**: Keep them short (≤4 lines).
- **Lists**:
    - Use `-` for unordered lists.
    - Use `1.` for ordered lists.
    - Nest with two spaces indentation.
- **Code Blocks**:
    - Always specify the language after triple backticks.
    - Example:

    ```python
    print("Hello World")
    ```
- **Inline Code**: Use backticks (\`) for short code snippets.


## Content Standards
- **Accuracy**: Verify all facts, numbers, and examples.
- **Examples**: Provide sample inputs/outputs for technical content.
- **Tables**:
    - Use for structured data.
    - Always include a header row.
    - Example:

        | Feature  | Description      |
        | -------- | ---------------- |
        | Accuracy | Precision of doc |
        | Clarity  | Easy to read     |

- **Links**: Use `[text](url)` format; prefer relative links when referencing local docs.


## Style & Tone
- Use **active voice**.
- Keep a **professional yet approachable tone**.
- Avoid jargon unless necessary (define it when used).
- Prefer **imperative style** for instructions (e.g., *"Run the command..."* instead of *"You should run..."*).


## Metadata (Optional but Recommended)
- At the top of the file, include a YAML front matter block when relevant:

  ```yaml
  title: Project Setup Guide
  author: LLM
  date: 2025-08-21
  version: 1.0
  ```


## Validation Criteria
Before finalizing the `.md` file, check:

- The document starts with a `# Title`.
- Section hierarchy is correct (`#`, `##`, `###`).
- Sentences are clear and concise.
- Code blocks are formatted and labeled.
- Tables (if present) are properly aligned.
- TOC is included if document >500 words.
- File is free of trailing spaces and inconsistent indentation.


## Example Template

````markdown
# Project Setup Guide

## Introduction
Briefly describe the purpose of this document.


## Requirements
- Python 3.10+
- Docker


## Installation
1. Clone repository  
2. Run `pip install -r requirements.txt`  
````



