import graphene

import openbook_auth.schema

class Mutation(openbook_auth.schema.Mutation, graphene.ObjectType):
    pass

class Query(openbook_auth.schema.Query, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
