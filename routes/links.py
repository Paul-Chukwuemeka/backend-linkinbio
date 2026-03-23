from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from lib.auth import get_current_user
from lib.database import get_db
from models.cardModel import Card
from models.CollectionModel import Collection
from models.LinkModel import Link
from models.userModel import User
from schemas.links import LinkCreate, LinkMove, LinkPublic, LinkReorderRequest, LinkUpdate

router = APIRouter(prefix="/links", tags=["links"])


@router.get("", response_model=list[LinkPublic])
def list_links(
    card_id: UUID,
    collection_id: UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[LinkPublic]:
    card = (
        db.query(Card)
        .filter(Card.id == card_id, Card.user_id == current_user.id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    query = db.query(Link).filter(Link.card_id == card_id)
    if collection_id is not None:
        collection = (
            db.query(Collection)
            .filter(Collection.id == collection_id, Collection.card_id == card_id)
            .first()
        )
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found",
            )
        query = query.filter(Link.collection_id == collection_id)

    links = query.order_by(Link.position.asc(), Link.id.asc()).all()
    return [LinkPublic.model_validate(link) for link in links]


@router.post("", response_model=LinkPublic, status_code=status.HTTP_201_CREATED)
def create_link(
    payload: LinkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LinkPublic:
    card = (
        db.query(Card)
        .filter(Card.id == payload.card_id, Card.user_id == current_user.id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    if payload.collection_id is not None:
        collection = (
            db.query(Collection)
            .filter(
                Collection.id == payload.collection_id,
                Collection.card_id == payload.card_id,
            )
            .first()
        )
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found",
            )

    if payload.collection_id is None:
        max_link = (
            db.query(func.max(Link.position))
            .filter(Link.card_id == payload.card_id, Link.collection_id.is_(None))
            .scalar()
        )
        max_collection = (
            db.query(func.max(Collection.position))
            .filter(Collection.card_id == payload.card_id)
            .scalar()
        )
        position = max(int(max_link or 0), int(max_collection or 0)) + 1
    else:
        max_position = (
            db.query(func.max(Link.position))
            .filter(
                Link.card_id == payload.card_id,
                Link.collection_id == payload.collection_id,
            )
            .scalar()
        )
        position = int(max_position or 0) + 1

    link = Link(
        title=payload.title,
        url=payload.url,
        card_id=payload.card_id,
        collection_id=payload.collection_id,
        position=position,
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    return LinkPublic.model_validate(link)


@router.patch("/reorder", status_code=status.HTTP_204_NO_CONTENT)
def reorder_links(
    payload: LinkReorderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if payload.collection_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /cards/{card_id}/items/reorder to reorder top-level links and collections",
        )

    card = (
        db.query(Card)
        .filter(Card.id == payload.card_id, Card.user_id == current_user.id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    if not payload.items:
        return None

    collection = (
        db.query(Collection)
        .filter(Collection.id == payload.collection_id, Collection.card_id == payload.card_id)
        .first()
    )
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    ids = [item.id for item in payload.items]
    if len(set(ids)) != len(ids):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Duplicate link ids in reorder payload",
        )

    links = (
        db.query(Link)
        .filter(
            Link.id.in_(ids),
            Link.card_id == payload.card_id,
            Link.collection_id == payload.collection_id,
        )
        .all()
    )
    if len(links) != len(ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    position_by_id = {item.id: item.position for item in payload.items}
    for link in links:
        link.position = position_by_id[link.id]

    db.commit()
    return None


@router.patch("/{link_id}", response_model=LinkPublic)
def update_link(
    link_id: UUID,
    payload: LinkUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LinkPublic:
    link = (
        db.query(Link)
        .join(Card, Link.card_id == Card.id)
        .filter(Link.id == link_id, Card.user_id == current_user.id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Title cannot be empty",
            )
        link.title = title
    if payload.url is not None:
        url = payload.url.strip()
        if not url:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="URL cannot be empty",
            )
        link.url = url

    if "collection_id" in payload.model_fields_set:
        if payload.collection_id is None:
            max_link = (
                db.query(func.max(Link.position))
                .filter(Link.card_id == link.card_id, Link.collection_id.is_(None))
                .scalar()
            )
            max_collection = (
                db.query(func.max(Collection.position))
                .filter(Collection.card_id == link.card_id)
                .scalar()
            )
            link.collection_id = None
            link.position = max(int(max_link or 0), int(max_collection or 0)) + 1
        else:
            collection = (
                db.query(Collection)
                .filter(
                    Collection.id == payload.collection_id,
                    Collection.card_id == link.card_id,
                )
                .first()
                )
            if not collection:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Collection not found",
                )
            link.collection_id = payload.collection_id
            max_position = (
                db.query(func.max(Link.position))
                .filter(Link.card_id == link.card_id, Link.collection_id == payload.collection_id)
                .scalar()
            )
            link.position = int(max_position or 0) + 1

    db.commit()
    db.refresh(link)
    return LinkPublic.model_validate(link)


@router.patch("/{link_id}/move", response_model=LinkPublic)
def move_link(
    link_id: UUID,
    payload: LinkMove,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LinkPublic:
    link = (
        db.query(Link)
        .join(Card, Link.card_id == Card.id)
        .filter(Link.id == link_id, Card.user_id == current_user.id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    if payload.collection_id is None:
        max_link = (
            db.query(func.max(Link.position))
            .filter(Link.card_id == link.card_id, Link.collection_id.is_(None))
            .scalar()
        )
        max_collection = (
            db.query(func.max(Collection.position))
            .filter(Collection.card_id == link.card_id)
            .scalar()
        )
        link.collection_id = None
        link.position = max(int(max_link or 0), int(max_collection or 0)) + 1
    else:
        collection = (
            db.query(Collection)
            .filter(
                Collection.id == payload.collection_id,
                Collection.card_id == link.card_id,
            )
            .first()
        )
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found",
            )
        link.collection_id = payload.collection_id
        max_position = (
            db.query(func.max(Link.position))
            .filter(Link.card_id == link.card_id, Link.collection_id == payload.collection_id)
            .scalar()
        )
        link.position = int(max_position or 0) + 1

    db.commit()
    db.refresh(link)
    return LinkPublic.model_validate(link)


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(
    link_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    link = (
        db.query(Link)
        .join(Card, Link.card_id == Card.id)
        .filter(Link.id == link_id, Card.user_id == current_user.id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    db.delete(link)
    db.commit()
    return None
