import logging
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail, get_connection
from django.db import transaction
from django.utils import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from mailing.models import Mailing, MailingLog

logger = logging.getLogger(__name__)

def send_mailing(mailing_id):
    """
    Отправляет рассылку и обрабатывает все возможные ошибки
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        logger.info(f"Начата обработка рассылки ID {mailing.id}")
    except Mailing.DoesNotExist:
        logger.error(f"Рассылка ID {mailing_id} не найдена")
        return

    # Проверка активности рассылки через метод модели
    if not mailing.is_active():
        logger.warning(
            f"Рассылка ID {mailing.id} не активна. "
            f"Статус: {mailing.get_status_display()}, "
            f"Время: {timezone.now()}"
        )
        return

    try:
        # Проверка доступности SMTP сервера
        conn = get_connection()
        conn.open()
        logger.debug("SMTP сервер доступен")
    except Exception as e:
        error_msg = f"Ошибка подключения к SMTP: {str(e)}"
        logger.critical(error_msg)
        MailingLog.objects.create(
            mailing=mailing,
            status=MailingLog.FAILURE,
            server_response=error_msg
        )
        return

    # Отправка писем в транзакции
    try:
        with transaction.atomic():
            success_count = 0
            clients_count = mailing.clients.count()

            for client in mailing.clients.all():
                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[client.email],
                        fail_silently=False,
                        connection=conn
                    )
                    MailingLog.objects.create(
                        mailing=mailing,
                        status=MailingLog.SUCCESS,
                        server_response="Успешно отправлено"
                    )
                    success_count += 1
                    logger.debug(f"Письмо клиенту {client.email} отправлено")

                except Exception as e:
                    error_msg = f"Ошибка отправки для {client.email}: {str(e)}"
                    logger.warning(error_msg)
                    MailingLog.objects.create(
                        mailing=mailing,
                        status=MailingLog.FAILURE,
                        server_response=error_msg
                    )

            # Обновление статуса если это последняя рассылка
            if timezone.now() >= mailing.end_time:
                mailing.status = Mailing.COMPLETED
                mailing.save()
                logger.info(f"Рассылка ID {mailing.id} автоматически завершена")

            logger.info(
                f"Рассылка ID {mailing.id} завершена. "
                f"Успешно: {success_count}/{clients_count}"
            )

    except Exception as e:
        error_msg = f"Критическая ошибка при отправке: {str(e)}"
        logger.critical(error_msg)
        MailingLog.objects.create(
            mailing=mailing,
            status=MailingLog.FAILURE,
            server_response=error_msg
        )

def check_mailings():
    """
    Проверяет и запускает активные рассылки
    """
    now = timezone.now()
    logger.debug(f"Проверка рассылок в {now}")

    # Находим рассылки которые нужно запустить сейчас
    mailings = Mailing.objects.filter(
        status=Mailing.STARTED,
        start_time__lte=now,
        end_time__gte=now
    )

    for mailing in mailings:
        logger.info(f"Запуск рассылки ID {mailing.id}")
        send_mailing(mailing.id)

    # Помечаем завершенные рассылки
    completed = Mailing.objects.filter(
        status=Mailing.STARTED,
        end_time__lt=now
    ).update(status=Mailing.COMPLETED)

    if completed:
        logger.info(f"Автоматически завершено рассылок: {completed}")

def delete_old_job_executions(max_age=604_800):
    """
    Удаляет старые записи выполнения задач (по умолчанию старше 7 дней)
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    help = "Запускает APScheduler для обработки рассылок"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Проверка рассылок каждые 30 секунд
        scheduler.add_job(
            check_mailings,
            trigger=CronTrigger(second="*/30"),
            id="check_mailings",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'check_mailings' (каждые 30 секунд)")

        # Очистка старых логов каждую неделю
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена еженедельная задача очистки логов")

        try:
            logger.info("Запуск scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Остановка scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler успешно остановлен")
