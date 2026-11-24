import os, json, glob, random, urllib.request
from datetime import datetime

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = "qwen/qwen3-coder:free"
LOG_FILE = "seo-memory/experiments-log.json"

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_log(logs):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def get_product_pages():
    pages = []
    for folder in ["excel-templates", "notion-templates", "notion-make-automation", "desktop-apps"]:
        if os.path.exists(folder):
            pages.extend(glob.glob(f"{folder}/*.md"))
    return pages

def call_openrouter(prompt):
    url = "https://openrouter.ai"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "SARH SEO Agent"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert technical SEO copywriter. Optimize the Markdown product page for Google search. Keep ALL existing payhip.com links and GitHub download links 100% intact. Improve H1 with high-intent keywords and add a concise 3-question FAQ section at the bottom. Return ONLY the updated Markdown without code fences."},
            {"role": "user", "content": prompt}
        ]
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=90) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["choices"]["message"]["content"].strip()

def main():
    if not OPENROUTER_API_KEY:
        print("Missing OPENROUTER_API_KEY")
        return
    pages = get_product_pages()
    if not pages:
        print("No product pages found")
        return
    logs = load_log()
    recent = [e["file"] for e in logs[-5:]]
    candidates = [p for p in pages if p not in recent] or pages
    target = random.choice(candidates)
    with open(target, "r", encoding="utf-8") as f:
        original = f.read()
    if "payhip.com" not in original:
        return
    updated = call_openrouter(f"Optimize this product page:\n\n{original}")
    if "payhip.com" in updated and len(updated) > 200:
        with open(target, "w", encoding="utf-8") as f:
            f.write(updated + "\n")
        logs.append({"date": datetime.utcnow().strftime("%Y-%m-%d"), "file": target, "model": MODEL})
        save_log(logs)
        print(f"Updated {target}")

if __name__ == "__main__":
    main()
