# Basic OAuth2 Parser & Validator

Includes settings in models/settings.py to add to your settings if needed.

To include for all endpoints in a route i.e `yourdomain.com/needs_login/*`
```
auth = OAuthBearer(settings.auth.well_known_endpoint)
common_dependencies = [Depends(auth)]
app.include_router(your_router_name.router, dependencies=common_dependencies)
```

The dependency adds a user object under request.state, which you need to include
```
@router.get("")
async def example(
    request: Request,
    table=Depends(some_other_dependency),
) -> None:
    request.state.user
return None
```