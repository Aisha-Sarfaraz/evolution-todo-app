"""T086: Push notification subscription routes.

POST /api/{user_id}/push/subscribe — register push subscription
DELETE /api/{user_id}/push/subscribe/{id} — remove subscription
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import ValidatedUser
from src.database import get_session

from src.models.push_subscription import PushSubscription

router = APIRouter(prefix="/api/{user_id}/push", tags=["push"])


class PushSubscribeRequest(BaseModel):
    """Request schema for push subscription."""
    endpoint: str
    keys: dict[str, str]  # Must have p256dh and auth


class PushSubscribeResponse(BaseModel):
    """Response schema for push subscription."""
    subscription_id: str


@router.post("/subscribe", response_model=PushSubscribeResponse)
async def subscribe_push(
    user_id: str,
    request: PushSubscribeRequest,
    current_user: ValidatedUser,
    session: AsyncSession = Depends(get_session),
) -> PushSubscribeResponse:
    """Register a browser push notification subscription."""
    # Validate keys
    if "p256dh" not in request.keys or "auth" not in request.keys:
        raise HTTPException(
            status_code=400,
            detail="Push subscription keys must include 'p256dh' and 'auth'.",
        )

    # Check for existing subscription with same endpoint
    existing = await session.execute(
        select(PushSubscription).where(PushSubscription.endpoint == request.endpoint)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="This push subscription is already registered.",
        )

    subscription = PushSubscription(
        id=uuid4(),
        user_id=current_user.user_id,
        endpoint=request.endpoint,
        keys=request.keys,
    )
    session.add(subscription)
    await session.commit()

    return PushSubscribeResponse(subscription_id=str(subscription.id))


@router.delete("/subscribe/{subscription_id}")
async def unsubscribe_push(
    user_id: str,
    subscription_id: str,
    current_user: ValidatedUser,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Remove a push notification subscription."""
    try:
        sub_uuid = UUID(subscription_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid subscription ID.")

    result = await session.execute(
        select(PushSubscription).where(
            PushSubscription.id == sub_uuid,
            PushSubscription.user_id == current_user.user_id,
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found.")

    await session.delete(subscription)
    await session.commit()

    return {"deleted": True}
