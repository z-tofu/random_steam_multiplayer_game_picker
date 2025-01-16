# Imports
import requests
import json
import random
from dotenv import load_dotenv
import os

# Loading the .env file with keys and user_ids
load_dotenv()

# Tenor API KEY
TENOR_API_KEY = os.getenv("TENOR_API_KEY")

TENOR_CKEY = os.getenv("TENOR_CKEY")

# Steam API KEY
API_KEY = os.getenv("STEAM_API_KEY")

# List of Steam64 IDs of the players
steam_ids_raw = os.getenv("STEAM_IDS")
STEAM_IDS = steam_ids_raw.split(",") if steam_ids_raw else []

# Cache file for storing common multiplayer games
CACHE_FILE = "common_multiplayer_games.json"


# Function to fetch games owned by a user
def get_owned_games(steam_id):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": API_KEY,
        "steamid": steam_id,
        "include_appinfo": True,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("response", {}).get("games", [])
    else:
        print(f"Failed to fetch games for SteamID {steam_id}: {response.status_code}")
        return []


# Function to check if a game supports multiplayer
def is_multiplayer(game_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={game_id}"
    response = requests.get(url)
    keywords = ["Multiplayer", "Multi-player", "Online pvp", "Online Co-op"]
    if response.status_code == 200:
        data = response.json().get(str(game_id), {}).get("data", {})
        categories = data.get("categories", [])
        return any(keyword in category["description"] for keyword in keywords for category in categories)
    return False


# Function to find and cache common multiplayer games
def find_and_cache_common_multiplayer_games(steam_ids):
    # Fetch games for all users
    user_games = []
    for steam_id in steam_ids:
        games = get_owned_games(steam_id)
        user_games.append({(game["appid"], game["name"]) for game in games})

    # Find common games
    common_games = set.intersection(*user_games)
    print(f"Common games: {common_games}")

    # Filter for multiplayer games
    multiplayer_games = []
    for game_id, game_name in common_games:
        if is_multiplayer(game_id):
            multiplayer_games.append({"appid": game_id, "name": game_name})

    # Save to cache
    with open(CACHE_FILE, "w") as f:
        json.dump(multiplayer_games, f) # type: ignore

    return multiplayer_games


# Function to load cached multiplayer games
def load_cached_games():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return None


# Main function to select a random game
def select_random_game(steam_ids):
    # Load cached games if available
    cached_games = load_cached_games()
    if cached_games:
        print("Loaded games from cache.")
        multiplayer_games = cached_games
    else:
        # Fetch and cache games if no cache exists
        print("No cache found. Fetching games from API...")
        multiplayer_games = find_and_cache_common_multiplayer_games(steam_ids)

    # Select a random multiplayer game
    if multiplayer_games:
        select_game = random.choice(multiplayer_games)
        return select_game
    else:
        return None


def tenor_gif_for_game(x):
    # set the apikey and limit
    apikey = TENOR_API_KEY  # click to set to your apikey
    lmt = 1
    ckey = TENOR_CKEY  # set the client_key for the integration and use the same value for all API calls

    # our test search
    search_term = f"hop on {x}"

    # get the top 8 GIFs for the search term
    r = requests.get(
        "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, apikey, ckey, lmt))

    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        top_gifs = json.loads(r.content)
        print(top_gifs)
    else:
        top_gifs = None


# Run
selected_game = select_random_game(STEAM_IDS)
if selected_game:
    print(
        f"Selected multiplayer game: {selected_game['name']} - https://store.steampowered.com/app/{selected_game['appid']}")
    tenor_gif_for_game(selected_game["name"])
else:
    print("No common multiplayer game found!")