import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import openai

def retrieve_relevant(texts, query, k=3):
    if len(texts) == 0:
        return []
    try:
        vect = TfidfVectorizer(stop_words='english')
        X = vect.fit_transform(texts)
        qv = vect.transform([query])
        cosine_similarities = linear_kernel(qv, X).flatten()
        indices = cosine_similarities.argsort()[::-1]
        topk = indices[:k]
        return [texts[i] for i in topk if cosine_similarities[i] > 0][:k]
    except Exception:
        return texts[:k]

def generate_fallback(prompt, retrieved_texts):
    intro = "Anbei Vorschläge für Angebots-Textblöcke basierend auf den Dokumenten:\n\n"
    blocks = []
    for i, t in enumerate(retrieved_texts, start=1):
        snippet = t
        if len(snippet) > 800:
            snippet = snippet[:800] + "..."
        blocks.append(f"Block {i}:\n{snippet}\n")
    template = f"{intro}{''.join(blocks)}\nAufgabenstellung: {prompt}\n\nGenerischer Vorschlag:\n- Nutzen hervorheben\n- Preis/Leistung individuell anpassbar\n\nBitte prüfen und anpassen."
    return template

def generate_with_openai(prompt, retrieved_texts, api_key):
    openai.api_key = api_key
    context = "\n\n---\n\n".join(retrieved_texts)
    system_message = "Du bist ein Assistent, der auf Basis der bereitgestellten Dokumente Angebots-Textblöcke erstellt."
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Kontext:\n{context}\n\nAufgabe: Erzeuge aus diesen Dokumenten mehrere Textblöcke für ein Angebot basierend auf: {prompt}\nGebe klare, kurze Abschnitte zurück."}
    ]
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.2,
            max_tokens=800
        )
        text = resp.choices[0].message.content
        return text
    except Exception as e:
        return f"Fehler bei OpenAI-Anfrage: {e}\n\nFallback-Inhalt:\n" + generate_fallback(prompt, retrieved_texts)
