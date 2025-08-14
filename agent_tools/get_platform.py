import json
from simplejustwatchapi.justwatch import search

def get_tvshow_plattform(state):
  show_name = state["target_show_name"]
  task_number = state['task_number']
  results = search(show_name, "IN", "en", 5, True)

  final_results = []

  for i in results:
      available_platforms = []
      for j in i[18]:
        available_platforms.append(
          {
            "platform_name": j[8][3],
            "platform_url": j[9]
          }
        )
      info = {
          "type": i[2],
          "name": i[3],
          "date": i[6],
          "description": i[8],
          "time": i[7],
          "image": i[12],
          "available_platforms": available_platforms
      }
      final_results.append(info)

  # with open('just-results.json', 'w', encoding='utf-8') as f:
  #     json.dump(final_results, f, ensure_ascii=False)

  return {"platform_info": final_results, 'task_number': task_number + 1, "app_link": final_results[0]["available_platforms"][0]["platform_url"]}


# print(get_tvshow_plattform({"target_show_name": "stranger things"}))