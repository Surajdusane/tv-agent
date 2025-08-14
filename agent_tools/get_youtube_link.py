from youtube_search import YoutubeSearch

def get_youtube_link(state):
  query = state['youtube_query']
  task_number = state['task_number']
  results = YoutubeSearch(query, max_results=10).to_dict()
  link = "https://www.youtube.com" + results[0]['url_suffix']
  return { 'app_link': link, 'task_number': task_number + 1 }
