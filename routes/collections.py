from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from lib.auth import get_current_user
from lib.database import get_db
from models.card_model import Card
from models.collection_model import Collection
from models.link_model import Link
from models.user_model import User
from schemas.collections import (
    CollectionCreate,
    CollectionPublic,
    CollectionReorderRequest,
    CollectionUpdate,
)

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("", response_model=list[CollectionPublic])
def list_collections(
    card_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CollectionPublic]:
    card = (
        db.query(Card)
        .filter(Card.id == card_id, Card.user_id == current_user.id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    collections = (
        db.query(Collection)
        .filter(Collection.card_id == card_id)
        .order_by(Collection.position.asc(), Collection.id.asc())
        .all()
    )
    return [CollectionPublic.model_validate(collection) for collection in collections]


@router.post("", response_model=CollectionPublic, status_code=status.HTTP_201_CREATED)
def create_collection(
    payload: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CollectionPublic:
    card = (
        db.query(Card)
        .filter(Card.id == payload.card_id, Card.user_id == current_user.id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    max_collection = (
        db.query(func.max(Collection.position))
        .filter(Collection.card_id == payload.card_id)
        .scalar()
    )
    max_link = (
        db.query(func.max(Link.position))
        .filter(Link.card_id == payload.card_id, Link.collection_id.is_(None))
        .scalar()
    )
    position = max(int(max_collection or 0), int(max_link or 0)) + 1

    title = payload.title.strip()
    if not title:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title cannot be empty",
        )

    collection = Collection(title=title, card_id=payload.card_id, position=position)
    db.add(collection)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Collection title already exists for this card",
        )
    db.refresh(collection)
    return CollectionPublic.model_validate(collection)


@router.patch("/{collection_id}", response_model=CollectionPublic)
def update_collection(
    collection_id: UUID,
    payload: CollectionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CollectionPublic:
    collection = (
        db.query(Collection)
        .join(Card, Collection.card_id == Card.id)
        .filter(Collection.id == collection_id, Card.user_id == current_user.id)
        .first()
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Title cannot be empty",
            )
        collection.title = title

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Collection title already exists for this card",
        )
    db.refresh(collection)
    return CollectionPublic.model_validate(collection)




@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    collection = (
        db.query(Collection)
        .join(Card, Collection.card_id == Card.id)
        .filter(Collection.id == collection_id, Card.user_id == current_user.id)
        .first()
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )

    db.delete(collection)
    db.commit()
    return None

