import dataclasses
import json

import pendulum
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from api.models import EditMode
from api.queues.edit_mode import schedule_remove_user_project_edit_mode
from mbuild.settings import EDIT_MODE_CLOSE_IN_MINUTES


@dataclasses.dataclass(frozen=True)
class EditModeMessage:
    project_pk: int
    user_pk: int
    close: bool = False


class EditModeConsumer(AsyncJsonWebsocketConsumer):
    async def receive_json(self, content, **kwargs):
        if self.scope['user'] is None:
            await self.send(json.dumps({'error': 'unauthorized'}), close=1000)
            return

        message = EditModeMessage(**content, user_pk=self.scope['user'].pk)
        user_in_edit_mode = await database_sync_to_async(self.check_edit_mode)(message)

        if not user_in_edit_mode:
            await self.send(json.dumps({'error': 'missing_edit_mode'}))
        elif message.close:
            await database_sync_to_async(self.delete_edit_mode)(message)
            await self.send(json.dumps({'closed': True}))
        else:
            await database_sync_to_async(self.save_last_update)(message)
            # In case when a client don't send message more than a limit
            # delete user edit mode.
            await database_sync_to_async(self.enqueue_edit_mode_deletion)(message)
            await self.send(json.dumps({'ok': True}))

    def check_edit_mode(self, message: EditModeMessage) -> bool:
        return EditMode.objects.filter(
            project_id=message.project_pk,
            user_id=message.user_pk
        ).exists()

    def delete_edit_mode(self, message: EditModeMessage) -> None:
        EditMode.objects.filter(
            project_id=message.project_pk,
            user_id=message.user_pk
        ).delete()

    def save_last_update(self, message: EditModeMessage) -> None:
        EditMode.objects.filter(
            project_id=message.project_pk,
            user_id=message.user_pk,
        ).update(updated_at=pendulum.now().to_datetime_string())

    def enqueue_edit_mode_deletion(self, message: EditModeMessage) -> None:
        schedule_remove_user_project_edit_mode(message.user_pk, message.project_pk, (EDIT_MODE_CLOSE_IN_MINUTES * 60) + 1)
