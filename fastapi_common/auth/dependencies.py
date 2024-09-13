from fastapi import HTTPException, Request
from starlette.status import HTTP_403_FORBIDDEN


class ScopeChecker:
    def __init__(self, required_scopes: list[str]) -> None:
        self.required_scopes = required_scopes

    def __call__(self, request: Request) -> bool:
        scopes = request.state.user.credentials.claims["scope"].split(" ")
        unsatisfied_requirements = [
            req_scope for req_scope in self.required_scopes if req_scope not in scopes
        ]
        if len(unsatisfied_requirements) > 0:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=f"You are missing the following scopes: {unsatisfied_requirements}",
            )
        return True


class GroupChecker:
    def __init__(self, required_groups: list[str]) -> None:
        self.required_groups = required_groups

    def __call__(self, request: Request) -> bool:
        groups = request.state.user.credentials.claims["cognito:groups"].split(" ")
        unsatisfied_requirements = [
            req_group for req_group in self.required_groups if req_group not in groups
        ]
        if len(unsatisfied_requirements) > 0:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=f"You are missing the following groups: {unsatisfied_requirements}",
            )
        return True
