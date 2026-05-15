from uuid import UUID

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status

from app.api.deps import CurrentUser, DBSession
from app.core.notifications import notification_manager
from app.core.security import decode_token
from app.repositories.user_repository import UserRepository
from app.schemas.notification import Notification as NotificationSchema
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationSchema])
async def list_notifications(
    db: DBSession,
    current_user: CurrentUser,
    limit: int = Query(default=20, ge=1, le=100),
) -> list[NotificationSchema]:
    notifications = await NotificationService(db).list_for_user(current_user.id, limit)
    return [NotificationSchema.model_validate(n) for n in notifications]


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_as_read(
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    await NotificationService(db).mark_all_as_read(current_user.id)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: DBSession,
    token: str | None = Query(None),
):
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = decode_token(token)
        user_id_raw = payload.get("sub")
        if not user_id_raw:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        user_id = UUID(str(user_id_raw))
        user = await UserRepository(db).get(user_id)
        if not user or not user.is_active:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await notification_manager.connect(user_id, websocket)
    try:
        while True:
            # Keep connection alive and wait for client to close it
            await websocket.receive_text()
    except WebSocketDisconnect:
        notification_manager.disconnect(user_id, websocket)
