from __future__ import annotations

import logging
import time

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_user_mailings(self, sending_id: int) -> None:
    """
    Пример фоновой задачи рассылки пользователям:
      загрузить объект UserSending по sending_id,
      собрать получателей по ролям/компании,
      отправить письма/уведомления.
    """
    started = timezone.now()
    logger.info("send_user_mailings[%s] started at %s", sending_id, started.isoformat())

    # One-second delay
    time.sleep(1)

    # For the later things adding
    logger.info("send_user_mailings[%s] finished", sending_id)
