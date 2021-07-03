from hashlib import sha256

import json
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from telegram import Bot

from apps.lib.utils import default_context
from apps.profiles.serializers import UserSerializer
from apps.profiles.utils import empty_user
from shortcuts import make_url


def base_template(request, extra=None):
    if request.method != 'GET':
        return bad_endpoint(request)
    if request.content_type == 'application/json':
        return bad_endpoint(request)
    if request.user.is_authenticated:
        user_data = UserSerializer(instance=request.user, context={'request': request}).data
    else:
        user_data = empty_user(session=request.session, user=request.user)
    context = {
        'debug': settings.DEBUG,
        'env_file': 'envs/{}.html'.format(settings.ENV_NAME),
        'base_url': make_url(''),
        'user_serialized': json.dumps(user_data)
    }
    if request.user.is_authenticated:
        context['user_email'] = request.user.guest_email or request.user.email
        email_hash = sha256()
        email_hash.update(context['user_email'].encode('utf-8'))
        context['user_email_hash'] = email_hash.hexdigest()
    context.update(extra or default_context())
    return render(
        request, 'index.html', context,
    )


def index(request):
    return base_template(request)


@api_view(('GET', 'POST', 'PATCH', 'PUT', 'HEAD', 'DELETE', 'OPTIONS'))
def bad_endpoint(request, *_args, **_kwargs):
    return Response(
        status=status.HTTP_404_NOT_FOUND, data={'detail': '{} is not a valid API Endpoint.'.format(request.path)}
    )


@api_view(('GET', 'POST', 'PATCH', 'PUT', 'HEAD', 'DELETE', 'OPTIONS'))
def bad_request(request, *_args, **_kwargs):
    return Response(
        status=status.HTTP_400_BAD_REQUEST, data={'detail': '{} does not support this method.'.format(request.path)}
    )


def force_error_email(request):
    return 1 / 0


@api_view(('GET',))
def test_telegram(request):
    if not request.user.is_authenticated:
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={'detail': 'You must be logged in to use this feature.'}
        )
    if not request.user.tg_chat_id:
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={'detail': 'You have not connected via Telegram.'}
        )
    bot = Bot(token=settings.TELEGRAM_BOT_KEY)
    bot.send_message(chat_id=request.user.tg_chat_id, text='This is a test message.')
    return Response(
        status=status.HTTP_204_NO_CONTENT
    )
