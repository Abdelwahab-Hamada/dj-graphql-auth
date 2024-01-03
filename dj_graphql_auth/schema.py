import graphene

import openbook_auth.schema

class Mutation(openbook_auth.schema.Mutation, graphene.ObjectType):
    pass

class Query(graphene.ObjectType):
    description = graphene.String(default_value="socialauth")

schema = graphene.Schema(query=Query, mutation=Mutation)
