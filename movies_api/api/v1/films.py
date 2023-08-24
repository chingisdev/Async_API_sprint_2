from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from models.film import Film
from models.sort import MoviesSortOptions
from services.film import get_film_service

from .service_protocol import ModelServiceProtocol

router = APIRouter()


@router.get(
    "/search",
    summary="Search throw all movies.",
    description="Search throw all movies.",
    tags=["Search"],
    response_model=List[Film],
)
async def film_details_list(
    search: str = Query(
        None,
        description="Searching text",
    ),
    sort: MoviesSortOptions = Query(
        None,
        description='Sort order (Use "imdb_rating" for ascending or "-imdb_rating" for descending)',
    ),
    page_size: int = Query(
        50,
        ge=1,
        le=100,
        description="Number of films per page",
    ),
    page_number: int = Query(
        1,
        ge=1,
        description="Page number",
    ),
    model_service: ModelServiceProtocol[Film] = Depends(get_film_service),
) -> List[Film]:
    films = await model_service.get_by_parameters(
        search=search,
        page_number=page_number,
        page_size=page_size,
        sort=sort,
    )
    return films


@router.get(
    "/{film_id}",
    description="Returns information about movie according uuid.",
    tags=["Movies"],
    response_model=Film,
)
async def film_details(
    film_id: str,
    model_service: ModelServiceProtocol[Film] = Depends(get_film_service),
) -> Film:
    film = await model_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="film not found",
        )
    return film
