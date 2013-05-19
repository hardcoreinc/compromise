from social_auth.backends.contrib.yandex import *

class FixedYandexOAuth2Backend(YandexOAuth2Backend):
	def get_user_details(self, response):
		name = response['real_name']
		last_name = ''

		if ' ' in name:
			names = name.split(' ')
			last_name = names[0]
			first_name = names[1]
		else:
			first_name = name

		return {
			'username': response["display_name"],
			'email': response["emails"][0],
			'first_name': first_name,
			'last_name': last_name,
			}

class FixedYandexOAuth2(YandexOAuth2):
	AUTH_BACKEND = FixedYandexOAuth2Backend
	REDIRECT_STATE = False

BACKENDS['yandex-oauth2'] = FixedYandexOAuth2
