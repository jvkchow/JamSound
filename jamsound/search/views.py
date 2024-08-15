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
    template_name = "home.html"

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

    def search_for_artist(self, token, artist):
        url = "https://api.spotify.com/v1/search"
        headers = self.get_auth_header(token)
        #query = f"?q={artist}&type=artist,track&limit=1"
        query = f"?q={artist}&type=artist&limit=10"
        full_query = url + query

        res = get(full_query, headers=headers)
        json_res = json.loads(res.content)

        results = []
        for artist in json_res["artists"]["items"]:
            artist_info = {}
            artist_info["name"] = artist["name"]
            artist_info["url"] = artist["external_urls"]["spotify"]
            results.append(artist_info)
        return results

    def get(self, request, *args, **kwargs):
        token = self.get_token()
        try:
            search_input = request.GET["search"]
            results = self.search_for_artist(token, search_input)
            print(results)
            return render(request, self.template_name, {"artists":results})
        except:
            return render(request, self.template_name, {"artists":[]})