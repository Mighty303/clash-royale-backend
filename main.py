from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = [
    "https://mighty303.github.io",   # GitHub Pages
    "https://martinwong.me"          # custom domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clash Royale API setup
API_TOKEN = os.getenv("API_TOKEN")
BASE_URL = "https://api.clashroyale.com/v1"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

@app.get("/top-clans")
async def get_top_players(limit: int = 10):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/locations/57000001/rankings/clans",
                headers=headers,
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(e)
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/top-players")
async def get_top_players(limit: int = 10):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/leaderboard/170000005",
                headers=headers,
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(e)
            raise HTTPException(status_code=400, detail=str(e))



@app.get("/popular-decks")
async def get_popular_decks(limit: int = 20):
    async with httpx.AsyncClient() as client:
        try:
            # First get top players
            response = await client.get(
                f"{BASE_URL}/locations/global/rankings/players",
                headers=headers,
                params={"limit": limit}
            )
            response.raise_for_status()
            top_players = response.json().get('items', [])
            
            # Get decks for each player
            decks = []
            for player in top_players:
                player_tag = player['tag'].replace('#', '')
                player_response = await client.get(
                    f"{BASE_URL}/players/%23{player_tag}",
                    headers=headers
                )
                if player_response.status_code == 200:
                    player_data = player_response.json()
                    if 'currentDeck' in player_data:
                        decks.append({
                            "player": player['name'],
                            "deck": player_data['currentDeck']
                        })
            
            return {"popular_decks": decks}
        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/top-player-decks")
async def get_top_player_decks(limit: int = 10):
    async with httpx.AsyncClient() as client:
        try:
            # Get top players
            top_players_resp = await client.get(
                f"{BASE_URL}/leaderboard/170000005",
                headers=headers,
                params={"limit": limit}
            )
            top_players_resp.raise_for_status()
            top_players = top_players_resp.json().get('items', [])

            decks = []
            for player in top_players:
                player_tag = player['tag'].replace('#', '')
                player_resp = await client.get(
                    f"{BASE_URL}/players/%23{player_tag}",
                    headers=headers
                )
                if player_resp.status_code == 200:
                    player_data = player_resp.json()
                    deck = player_data.get('currentDeck', [])
                    decks.append({
                        "player": player['name'],
                        "tag": player['tag'],
                        "deck": deck
                    })

            return {"top_player_decks": decks}
        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/top-support-cards")
async def get_top_support_cards(limit: int = 10):
    async with httpx.AsyncClient() as client:
        try:
            # Get top players
            top_players_resp = await client.get(
                f"{BASE_URL}/leaderboard/170000005",
                headers=headers,
                params={"limit": limit}
            )
            top_players_resp.raise_for_status()
            top_players = top_players_resp.json().get('items', [])

            support_cards = []
            for player in top_players:
                player_tag = player['tag'].replace('#', '')
                player_resp = await client.get(
                    f"{BASE_URL}/players/%23{player_tag}",
                    headers=headers
                )
                if player_resp.status_code == 200:
                    player_data = player_resp.json()
                    cards = player_data.get('currentDeckSupportCards', [])
                    support_cards.append({
                        "player": player['name'],
                        "tag": player['tag'],
                        "support_cards": cards
                    })

            return {"top_support_cards": support_cards}
        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True
    )