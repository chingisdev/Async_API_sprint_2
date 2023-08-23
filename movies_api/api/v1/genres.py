from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from models.genre import Genre
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get(
    "/search",
    summary="Search throw genres",
    description="Write genre name to field search to retrieve all genres with this name.",
    tags=["Search"],
    response_model=List[Genre],
)
async def genre_details_list(
    search: str = Query(
        None,
        description="Searching text",
    ),
    page_size: int = Query(
        50,
        ge=1,
        le=100,
        description="Number of genres per page",
    ),
    page_number: int = Query(
        1,
        ge=1,
        description="Page number",
    ),
    genre_service: GenreService = Depends(get_genre_service),
) -> List[Genre]:
    genres = await genre_service.filter(
        search=search,
        page_number=page_number,
        page_size=page_size,
    )

    return genres


@router.get(
    "/{genre_id}",
    tags=["Genres"],
    description="Returns information about genre according uuid.",
    response_model=Genre,
)
async def genre_details(
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="genre not found",
        )

    return genre
