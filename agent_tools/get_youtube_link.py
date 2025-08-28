from youtube_search import YoutubeSearch

def get_youtube_link(state):
  print("🔎 Starting YouTube search...")
  query = state['youtube_query']
  task_number = state['task_number']

  print(f"🎬 Searching for: '{query}' (Task #{task_number + 1})")

  results = YoutubeSearch(query, max_results=10).to_dict()

  if not results:
        print("❌ No YouTube results found.")
        raise Exception("No YouTube results found for the given query.")
  
  link = "https://www.youtube.com" + results[0]['url_suffix']
  title = results[0].get('title', 'Unknown Title')

  print("✅ YouTube search successful.")
  print(f"🔗 Top Result: {title}")
  print("✅ Task completed.\n")

  return { 'app_link': link, 'task_number': task_number + 1 }
