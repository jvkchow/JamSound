from django.shortcuts import render
from rest_framework.views import APIView
from django.views import View
from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get

# Create your views here.
class HomeView(APIView):

    # get application's client ID and client secret
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    
    def get_token(self):
        # create base64 string
        auth_string = self.client_id + ":" + self.client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        # create post request
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + auth_base64
        }
        data = {"grant_type": "client_credentials"}
        res = post(url, headers=headers, data=data)
        json_res = json.loads(res.content)

        return json_res["access_token"]
    
    def get_auth_header(self, token):
        return {"Authorization": "Bearer " + token}

    def search(self, token, search):
        url = "https://api.spotify.com/v1/search"
        headers = self.get_auth_header(token)
        query = f"?q={search}&type=artist,track&limit=10"
        full_query = url + query

        res = get(full_query, headers=headers)
        json_res = json.loads(res.content)

        print("\n", json_res, "\n")

        artist_results = []
        for artist in json_res["artists"]["items"]:
            artist_info = {}
            artist_info["name"] = artist["name"]
            artist_info["url"] = artist["external_urls"]["spotify"]
            if artist["images"] == []:
                artist_info["image"] = ""
            else:
                artist_info["image"] = artist["images"][0]["url"]
            artist_results.append(artist_info)

        track_results = []
        for track in json_res["tracks"]["items"]:
            track_info = {}
            track_info["name"] = track["name"]
            track_info["url"] = track["external_urls"]["spotify"]

            if track["album"]["images"] == []:
                track_info["image"] = ""
            else:
                track_info["image"] = track["album"]["images"][0]["url"]

            track_artists = []
            for artist in track["artists"]:
                track_artists.append(artist["name"])
            track_info["artists"] = track_artists
            track_results.append(track_info)

        return artist_results, track_results

    def get(self, request, *args, **kwargs):
        token = self.get_token()
        try:
            search_input = request.GET["search"]
            artists, tracks = self.search(token, search_input)
            return render(request, "search.html", {"artists":artists, "tracks":tracks})
        except Exception as e:
            print(e)
            return render(request, "home.html")