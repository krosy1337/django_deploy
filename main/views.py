from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpRequest, Http404

import random

import json
from django.shortcuts import redirect
from django.contrib.auth.models import User
from .models import TalantUser
from django.contrib.auth import logout, login
from django.urls import reverse
import requests
import time
from rest_framework.views import APIView

from dataclasses import dataclass

from django.conf import settings
from authlib.integrations.requests_client import OAuth2Session
from django.contrib.auth.decorators import login_required




# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('user')
    return render(request, 'main/home.html')


def user(request):
    if not request.user.is_authenticated:
        return redirect('home')
    return render(request, 'main/user.html', {'user': request.user})



def generate_uri(request, rev):
    uri = request.build_absolute_uri(rev)
    return uri


def authenticate(request, email=None, **kwargs):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

def pageNotFound(request, exception):
    return render(request, 'main/error.html')

def auth_steam(request):
    request.user.talantuser.steam_id = random.randint(9999999999, 99999999999)
    request.user.talantuser.save()
    return redirect('user')

def logout_steam(request):
    request.user.talantuser.steam_id = None
    request.user.talantuser.save()
    return redirect('user')

def auth_blizzard(request):
    request.user.talantuser.blizzard_id = random.randint(9999999999, 99999999999)
    request.user.talantuser.save()
    return redirect('user')

def logout_blizzard(request):
    request.user.talantuser.blizzard_id = None
    request.user.talantuser.save()
    return redirect('user')



client_id = 'J0kI8tJuJXVPdHmuprtg90OCHaDnschInCB0AnrHqyV8wPcn'
client_secret = 'sKxWlUmfx31SKjANOKzI0z25OlSIVUYwL6AdmxBgQbactpC3'
token_endpoint = 'https://talent.kruzhok.org/api/oauth/issue-token/'
authpoint = 'https://talent.kruzhok.org/oauth/authorize/'


@dataclass
class TalentInfo:
    id: int
    email: str
    first_name: str
    last_name: str


def get_talent_info(token) -> TalentInfo:
    client = OAuth2Session(client_id, client_secret, token=token)
    # id, email, first_name, last_name
    resp = client.get('https://talent.kruzhok.org/api/users/me').json()
    return TalentInfo(id=resp['id'], email=resp['email'], first_name=resp['first_name'], last_name=resp['last_name'])


def register_user(talent_info: TalentInfo, token):
    user = User(email=talent_info.email, username=talent_info.email, first_name=talent_info.first_name,
                last_name=talent_info.last_name, id=talent_info.id)
    user.save()

    talent_user = TalantUser(user=user, access_token=json.dumps(token))
    talent_user.save()


class AuthLoginTalent(APIView):
    def get(self, request):
        redirect_uri = generate_uri(request, reverse('authcomplete'))

        uri, state = OAuth2Session(client_id, client_secret).create_authorization_url(
            authpoint, response_type='code',
            nonce=time.time(), redirect_uri=redirect_uri
        )


        return redirect(uri)


class AuthCompleteTalent(APIView):
    def get(self, request):
        if request.query_params.get('error'):
            return redirect('home')

        token = requests.post(token_endpoint, data={
            'grant_type': 'authorization_code',
            'scope': 'openid',
            'nonce': time.time(),
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': generate_uri(request, reverse('authcomplete')),
            'code': request.query_params['code'],
        }).json()

        user_info = get_talent_info(token)

        print(user_info)

        if not User.objects.filter(email=user_info.email).exists():
            register_user(user_info, token)

        user = authenticate(request, email=user_info.email)



        if user is not None:
            login(request, user)
            return redirect('user')
        return redirect('home')


class LogoutTalent(APIView):

    def get(self, request):
        logout(request)
        return redirect('home')