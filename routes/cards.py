from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from lib.auth import get_current_user
from lib.database import get_db
from models.cardModel import Card
from models.CollectionModel import Collection
from models.LinkModel import Link
from models.userModel import User
from schemas.cards import CardCreate, CardPublic, CardUpdate
from schemas.collections import CollectionPublic
from schemas.items import CardItem, CardItemReorderRequest, CardItemType
from schemas.links import LinkPublic

router = APIRouter(prefix="/cards", tags=["cards"],)


@router.get("/me", response_model=list[CardPublic])
def get_my_card(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CardPublic]:
    cards = (
        db.query(Card)
        .filter(Card.user_id == current_user.id)
        .order_by(Card.id.asc())
        .all()
    )
    return [CardPublic.model_validate(card) for card in cards]


@router.post("", response_model=CardPublic, status_code=status.HTTP_201_CREATED)
def create_card(
    payload: CardCreate | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CardPublic:
    name = ((payload.name if payload else None) or "").strip()
    if not name:
        name = "Untitled"
    card = Card(user_id=current_user.id, name=name)
    db.add(card)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create card",
        )

    db.refresh(card)
    return CardPublic.model_validate(card)


@router.get("/{card_id}", response_model=CardPublic)
def get_card_by_id(
    card_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CardPublic:
    card = (
        db.query(Card)
        .filter(Card.id == card_id, Card.user_id == current_user.id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    return CardPublic.model_validate(card)


@router.patch("/{card_id}", response_model=CardPublic)
def update_card(
    card_id: UUID,
    payload: CardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CardPublic:
    card = (
        db.query(Card)
        .filter(Card.id == card_id, Card.user_id == current_user.id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Card name cannot be empty",
            )
        card.name = name

    db.commit()
    db.refresh(card)
    return CardPublic.model_validate(card)


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    card_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    card = (
        db.query(Card)
        .filter(Card.id == card_id, Card.user_id == current_user.id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    db.delete(card)
    db.commit()
    return None


@router.get("/{card_id}/items", response_model=list[CardItem])
def list_card_items(
    card_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CardItem]:
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
        .all()
    )
    links = (
        db.query(Link)
        .filter(Link.card_id == card_id, Link.collection_id.is_(None))
        .all()
    )

    items: list[CardItem] = []
    for collection in collections:
        items.append(
            CardItem(
                type=CardItemType.collection,
                position=collection.position,
                collection=CollectionPublic.model_validate(collection),
            )
        )
    for link in links:
        items.append(
            CardItem(
                type=CardItemType.link,
                position=link.position,
                link=LinkPublic.model_validate(link),
            )
        )

    items.sort(
        key=lambda item: (
            item.position,
            0 if item.type == CardItemType.collection else 1,
        )
    )
    return items


@router.patch("/{card_id}/items/reorder", status_code=status.HTTP_204_NO_CONTENT)
def reorder_card_items(
    card_id: UUID,
    payload: CardItemReorderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    card = (
        db.query(Card)
        .filter(Card.id == card_id, Card.user_id == current_user.id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    total_links = (
        db.query(func.count(Link.id))
        .filter(Link.card_id == card_id, Link.collection_id.is_(None))
        .scalar()
    )
    total_collections = (
        db.query(func.count(Collection.id))
        .filter(Collection.card_id == card_id)
        .scalar()
    )
    total_items = int(total_links or 0) + int(total_collections or 0)
    if total_items == 0:
        return None

    if len(payload.items) != total_items:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reorder payload must include all card items",
        )

    seen: set[tuple[CardItemType, UUID]] = set()
    positions: set[int] = set()
    for item in payload.items:
        key = (item.type, item.id)
        if key in seen:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Duplicate item in reorder payload",
            )
        if item.position in positions:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Duplicate positions in reorder payload",
            )
        seen.add(key)
        positions.add(item.position)

    link_ids = [item.id for item in payload.items if item.type == CardItemType.link]
    collection_ids = [
        item.id for item in payload.items if item.type == CardItemType.collection
    ]

    links = []
    if link_ids:
        links = (
            db.query(Link)
            .filter(
                Link.id.in_(link_ids),
                Link.card_id == card_id,
                Link.collection_id.is_(None),
            )
            .all()
        )
        if len(links) != len(link_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found",
            )

    collections = []
    if collection_ids:
        collections = (
            db.query(Collection)
            .filter(Collection.id.in_(collection_ids), Collection.card_id == card_id)
            .all()
        )
        if len(collections) != len(collection_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found",
            )

    position_by_key = {(item.type, item.id): item.position for item in payload.items}
    for link in links:
        link.position = position_by_key[(CardItemType.link, link.id)]
    for collection in collections:
        collection.position = position_by_key[(CardItemType.collection, collection.id)]

    db.commit()
    return None
