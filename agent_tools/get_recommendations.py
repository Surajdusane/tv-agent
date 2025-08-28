import requests
from bs4 import BeautifulSoup

def get_recommendations(state):

    print("🔎 Starting recommendation search...")

    show_name = state["show_name"]
    task_number = state['task_number']

    print(f"📺 Looking for shows similar to: '{show_name}' (Task #{task_number + 1})")

    # Format title for URL
    formatted_title = show_name.strip().replace(" ", "+").lower()
    url = f"https://www.movie-map.com/{formatted_title}"

    # Send request
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to load page. Status code: {response.status_code}")

    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    map_div = soup.find('div', {'id': 'gnodMap'})
    if not map_div:
        raise Exception("Could not find recommendations on the page.")

    # Extract recommendations
    similar_titles = [a.text.strip() for a in map_div.find_all('a', class_='S')]
    similar_titles = [title for title in similar_titles if title.lower() != show_name.lower()]
    result = list(set(similar_titles))

    if not result:
        print("⚠️ No recommendations found.")

    print(f"\n🎯 Default target show for next task: {result[0]}")
    print("✅ Recommendation task completed.\n")

    return {"recommendations": result, "target_show_name": result[0], 'task_number': task_number + 1}

# # Example usage
# if __name__ == "__main__":
#     results = get_recommendations({"show_name": "stranger things"})
#     print(results)
#     for i, title in enumerate(results["recommendations"], 1):
#         print(f"{i}. {title}")
