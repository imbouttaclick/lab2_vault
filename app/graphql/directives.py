from ariadne import SchemaDirectiveVisitor
from graphql import GraphQLError, default_field_resolver


class IsAuthenticatedDirective(SchemaDirectiveVisitor):
    def visit_field_definition(self, field, object_type):
        original_resolver = field.resolve or default_field_resolver

        def wrapped_resolver(obj, info, **kwargs):
            if not info.context.get("user"):
                raise GraphQLError("Authentication required")
            return original_resolver(obj, info, **kwargs)

        field.resolve = wrapped_resolver
        return field


class IsAdminDirective(SchemaDirectiveVisitor):
    def visit_field_definition(self, field, object_type):
        original_resolver = field.resolve or default_field_resolver

        def wrapped_resolver(obj, info, **kwargs):
            user = info.context.get("user")
            if not user:
                raise GraphQLError("Authentication required")
            if not user.is_admin:
                raise GraphQLError("Admin only")
            return original_resolver(obj, info, **kwargs)

        field.resolve = wrapped_resolver
        return field