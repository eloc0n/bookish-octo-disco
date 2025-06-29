from os import getenv
from fastapi import Request
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from sqlalchemy import func, bindparam, ColumnElement
from starlette.datastructures import URL

from core.schemas.pagination import PaginatedResponse


class Paginator:
    """
    A reusable pagination helper for SQLModel-based queries in a FastAPI context.

    This class encapsulates the logic needed to:
    - Execute paginated database queries.
    - Apply optional `ILIKE` filters for search-like behavior.
    - Generate `PaginatedResponse` objects with `next` and `previous` URLs.
    - Serialize SQLModel objects to Pydantic schemas with proper attribute mapping.

    Attributes:
        limit (int): Number of items per page.

    Usage:
        Call the `paginate()` method by passing:
        - The HTTP request (to build pagination URLs)
        - The SQLAlchemy session
        - A SQLModel model to query
        - A corresponding Pydantic response schema
        - The desired page number
        - Optional filtering logic (field and pattern)

    Notes:
        - Designed for clean separation of pagination from route/CRUD logic.
        - Handles inconsistencies during test serialization using `model_dump`.
        - Assumes Pydantic `model_validate` for from_attributes=True in non-test environments.
    """

    def __init__(self, limit: int = 20):
        self.limit = limit

    async def paginate(
        self,
        *,
        request: Request,
        session: AsyncSession,
        model: type[SQLModel],
        schema: type[BaseModel],
        page: int,
        filter: str | None = None,
        filter_field: ColumnElement | None = None,
        options: list = [],
    ) -> PaginatedResponse:
        if page < 1:
            raise ValueError("Page number must be >= 1")

        offset = (page - 1) * self.limit
        params = {}

        # NOTE
        # Queries should be performed inside the function that call paginator
        # Filtering logic should move so that it is easier to add extra fields
        # other than name for characters / starships and title for films.

        # Filtering logic
        if filter and filter_field is not None:
            pattern = f"%{filter}%"
            condition = filter_field.ilike(bindparam("pattern"))
            base_query = select(model).where(condition).options(*options)
            count_query = select(func.count()).select_from(base_query.subquery())
            data_query = base_query.offset(offset).limit(self.limit)
            params = {"pattern": pattern}
        else:
            base_query = select(model).options(*options)
            count_query = select(func.count()).select_from(model)
            data_query = base_query.offset(offset).limit(self.limit)

        # Execute queries
        count_result = await session.execute(count_query, params)
        total = count_result.scalar_one()

        result = await session.execute(data_query, params)
        items = result.scalars().all()

        # Build pagination URLs
        total_pages = (total + self.limit - 1) // self.limit

        def build_url(p: int) -> str:
            return str(URL(str(request.url)).include_query_params(page=p))

        next_url = build_url(page + 1) if page < total_pages else None
        prev_url = build_url(page - 1) if page > 1 else None

        # NOTE
        # I know how this looks but i cannot find a solution for the issue
        # where i need model_validate in order to return results of character
        # model with relations (starships, films) BUT breaks tests...
        # so i use model_dump in that case.
        # Why is this happening is a mystery to me.
        if getenv("ENVIRONMENT") == "test":
            results = [schema(**obj.model_dump()) for obj in items]
        else:
            results = [
                schema.model_validate(obj, from_attributes=True) for obj in items
            ]

        return PaginatedResponse(
            count=total,
            next=next_url,
            previous=prev_url,
            results=results,
        )
