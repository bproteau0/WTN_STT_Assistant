from flask import render_template, redirect
from app import app
from google import genai
from google.genai import types
import requests
import re

def extract_key(line):
    return re.search("\"[^\"]+\"", line)

# Get keys
keys_file = open('keys.txt', 'r')

gemini_key = extract_key(keys_file.readline())
if gemini_key is None:
    raise Exception("GEMINI_API_KEY not found in keys file")
else:
    gemini_key = gemini_key.group(0)[1:-1]

google_key = extract_key(keys_file.readline())    
if google_key is None:
    raise Exception("GOOGLE_API_KEY not found in keys file")
else:
    google_key = google_key.group(0)[1:-1]
    
google_id = extract_key(keys_file.readline())
if google_id is None:
    raise Exception("SEARCH_ENGINE_ID not found in keys file")
else:
    google_id = google_id.group(0)[1:-1]

@app.route("/")
@app.route("/index")
def index():
    return redirect('/chat/')

@app.route("/chat/")
def empty_chat():
    return render_template('chat.html', response=False)

@app.route("/chat/<query>")
def chat(query):
    
    
    client = genai.Client(api_key=gemini_key)
        
    # Pass 1
    # Extract Keywords
    def query_gemini(query, system_prompt):
        return client.models.generate_content(
            model="gemini-2.5-flash"
        )
    def ask_ctx(q, sys): return client.models.generate_content(model="gemini-2.5-flash", contents=q, config=types.GenerateContentConfig(system_instruction=sys)).text
    def ask(q): return client.models.generate_content(model="gemini-2.5-flash", contents=q).text
    keyword_extract = f"Your goal is to extract 5-6 impactful keywords or short phrases from a given query. Keep multi-word concepts together. Return as comma-separated list. If the language of the query is not English, then add English translations of each keyword to the list as well."
    keywords = ask_ctx(query, keyword_extract)
    
    print(f"keywords found: {keywords}")
    
    # Pass 2
    # Search CSE for each keyword
    sources_map = {}
    if keywords is not None:
        for word in keywords.split(', '):
            print(f"searching for: {word}")
            CSE_url = f"https://www.googleapis.com/customsearch/v1?key={google_key}&cx={google_id}&q={word}"
            search_results = requests.get(url=CSE_url).json()
            # Go through each source found for given keyword and add to sources map
            if search_results.get("items") is not None:
                for source in search_results.get("items"):
                    title = source.get("title")
                    url = source.get("link")
                    if url not in sources_map.keys():
                        sources_map[url] = [title, url]
                print(f"Found {len(search_results.get('items'))} sources for {word}.")
    print(f"{len(sources_map.keys())} Sources found:")
    for source in sources_map.values(): print(f"\t{source[0]}")
    
    # Pass 3
    # Gemini responses
    system_prompt = f"Respond to the user's query \"{query}\". In your responses, I expect you to answer in short 3-4 sentence summaries with appropriate section headers. Cite all sources used at the bottom of the response with embedded links in markdown format in a bulleted list. If you cannot find any useful information regarding the query, please do not make a response. Instead, please simply respond with the following: \"I couldn't find any resources regarding this question. Do you have any other questions?\" Please attempt to maintain a professional tone and always answer with sustainability in mind."
    NLDL_prompt = "You are the interface for an improved querying interface for the NL-Digital Library (NLDL). " + system_prompt + f" In your response, you MUST USE the following relevant pages as sources: {sources_map.values()}. If there are no relevant pages listed prior, then do not form an answer."
    
    print("Generating web response.")
    web_response_content = ask(system_prompt)
    print("Generating NLDL response.")
    NLDL_response_content = ask(NLDL_prompt)
    
    print(f"NLDL_response_content: {NLDL_response_content}\nweb_response_content: {web_response_content}")
        
    return render_template('chat.html', response=True, NLDL_response_content=NLDL_response_content, web_response_content=web_response_content)
    