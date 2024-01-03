from graphene import relay, ObjectType
import graphene
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialToken, SocialLogin
from allauth.socialaccount.helpers import (
    complete_social_login,
)

class FacebookLoginMutation(relay.ClientIDMutation):
    login = graphene.String()

    class Input:
        access_token = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        adapter = get_adapter()
        provider = adapter.get_provider(info.context, 'facebook')
        app = provider.app
        expires_at = None
        token = SocialToken(app=app, token=input.get('access_token'), expires_at=expires_at)

        adapter_class = FacebookOAuth2Adapter(info.context)
        login = adapter_class.complete_login(info.context, app, access_token=token)
        login.token = token
        login.state = SocialLogin.state_from_request(info.context)
        ret = complete_social_login(info.context, login)

        return cls(login=ret)
    
class Mutation(ObjectType):
    facebook_login = FacebookLoginMutation.Field()
