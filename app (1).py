
import streamlit as st
import requests
import json
import os
from together import Together

# 🔑 Replace with your real keys
os.environ["together_api_key"] = "18ea421c910f4967d2ef737c2c559acecb941d9834a7c99d1a8b9a47c0b7d513"
SERPER_API_KEY = "dd8e3bb205e2e1cc635cbebb598e09438e99fa40"

client = Together()

def search_web(query):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    data = {"q": query}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def extract_snippets(results):
    snippets = ""
    for item in results.get("organic", [])[:3]:
        snippets += f"🔹 {item['title']}\n{item['snippet']}\n{item['link']}\n\n"
    return snippets.strip()

def smart_chat_with_search(user_query, expert="You are a helpful assistant."):
    search_data = search_web(user_query)
    search_text = extract_snippets(search_data)
    context = expert + f"\n\nUse the following real-time search results to answer the question:\n\n{search_text}"

    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": user_query}
    ]

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=messages,
        stream=True
    )

    for chunk in response:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content

# 🌐 Streamlit UI
st.title("📡 Real-Time LLM Chatbot with Serper API")
query = st.text_input("Ask your question")
context = st.text_area("Expert Prompt", "You are a helpful assistant.")

if st.button("Ask"):
    if query.strip():
        with st.spinner("Thinking..."):
            response_box = st.empty()
            full_text = ""
            for token in smart_chat_with_search(query, context):
                full_text += token
                response_box.markdown(full_text)
