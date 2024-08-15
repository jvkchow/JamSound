from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import json
from dotenv import load_dotenv
import os

# Create your views here.
class Results(APIView):
    def get(self, request, *args, **kwargs):
        try:
            load_dotenv()
            client_id = os.getenv("CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET")
            print(client_id, client_secret)
        except:
            return Response(status=404)