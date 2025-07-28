# 🧠 Adobe India Hackathon – Round 1A: Understand Your Document

## 📝 Challenge Overview
Extract a structured, hierarchical outline from a raw PDF including:
- Title
- Headings: H1, H2, H3
- Page numbers

This acts as the foundation for intelligent document navigation.

---

## 📥 Input
- Directory: /app/input/
- File(s): PDF(s) up to 50 pages

## 📤 Output
- Directory: /app/output/
- For each filename.pdf, output a corresponding filename.json in the format:
```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
