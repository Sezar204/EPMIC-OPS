Input
"""Service layer — business logic lives here.

Services take a Session and orchestrate one or more repositories.
They never expose ORM objects directly to the API layer; return
Pydantic models or plain dicts.
"""
