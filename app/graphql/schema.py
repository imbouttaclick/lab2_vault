from pathlib import Path
from ariadne import load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL
from app.graphql.resolvers import bindables
from app.graphql.directives import IsAuthenticatedDirective, IsAdminDirective
from app.graphql.context import get_context_value

type_defs = load_schema_from_path(str(Path(__file__).parent / "schema.graphql"))

schema = make_executable_schema(
    type_defs,
    *bindables,
    directives={
        "isAuthenticated": IsAuthenticatedDirective,
        "isAdmin": IsAdminDirective,
    },
)

graphql_app = GraphQL(schema, context_value=get_context_value, debug=True)