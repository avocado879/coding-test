"""A dependency-free agent-data demo: plan, call tools, and compose an answer."""
import argparse, json, re

def count_words(text): return len(re.findall(r"\b[\w'-]+\b", text))
def top_keywords(text, limit=5):
    words = re.findall(r"[A-Za-z][A-Za-z0-9'-]+", text.lower())
    stop = {"the", "and", "is", "to", "of", "a", "in", "for", "this", "that"}
    freq = {}
    for word in words:
        if word not in stop: freq[word] = freq.get(word, 0) + 1
    return sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:limit]

def run(text):
    result = {"plan": ["count words", "extract keywords", "compose summary"],
      "tools": {"word_count": count_words(text), "top_keywords": top_keywords(text)},
      "answer": f"The input contains {count_words(text)} words. Top keywords: " + ", ".join(k for k, _ in top_keywords(text))}
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("text", nargs="?", default="Agent data systems need reliable tools and clear outputs.")
    print(json.dumps(run(parser.parse_args().text), ensure_ascii=False, indent=2))
