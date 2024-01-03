from graphene import relay, ObjectType
import graphene
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialToken, SocialLogin, SocialAccount
from allauth.socialaccount.helpers import (
    complete_social_login,
)

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django.contrib.auth.models import User

from graphql_relay import from_global_id

from allauth.socialaccount import signals


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
        token = SocialToken(app=app, token=input.get(
            'access_token'), expires_at=expires_at)

        adapter_class = FacebookOAuth2Adapter(info.context)
        login = adapter_class.complete_login(
            info.context, app, access_token=token)
        login.token = token
        login.state = SocialLogin.state_from_request(info.context)
        ret = complete_social_login(info.context, login)

        return cls(login=ret)

class SocialAccountDisconnetMutation(relay.ClientIDMutation):
    success = graphene.String()

    class Input:
        social_account_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        social_account = SocialAccount.objects.get(pk=from_global_id(input.get('social_account_id'))[1])
        user = User.objects.get(pk=from_global_id(input.get('user_id'))[1])
        accounts = SocialAccount.objects.filter(user=user)

        get_adapter(info.context).validate_disconnect(social_account, accounts)

        social_account.delete()

        signals.social_account_removed.send(
            sender=SocialAccount, request=info.context, socialaccount=social_account
        )

        return cls(success=True)
    
class Mutation(ObjectType):
    facebook_login = FacebookLoginMutation.Field()
    social_account_disconnect = SocialAccountDisconnetMutation.Field()

class UserNode(DjangoObjectType):
    class Meta:
        model = User

class SocialAccountNode(DjangoObjectType):
    class Meta:
        model = SocialAccount
        filter_fields = []
        interfaces = (relay.Node, )


class Query(ObjectType):
    social_account = relay.Node.Field(SocialAccountNode)
    all_social_accounts = DjangoFilterConnectionField(SocialAccountNode)
