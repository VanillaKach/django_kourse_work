import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from mailing.models import Mailing, MailingLog

logger = logging.getLogger(__name__)


def send_mailing(mailing_id):
    mailing = Mailing.objects.get(id=mailing_id)

    if mailing.status != Mailing.STARTED:
        return

    now = datetime.now().astimezone()
    if mailing.start_time > now or mailing.end_time < now:
        return

    for client in mailing.clients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=False,
            )

            MailingLog.objects.create(
                mailing=mailing,
                status=MailingLog.SUCCESS,
                response='Email sent successfully'
            )

            logger.info(f"Successfully sent mailing {mailing.id} to {client.email}")

        except Exception as e:
            MailingLog.objects.create(
                mailing=mailing,
                status=MailingLog.FAILURE,
                response=str(e)
            )
            logger.error(f"Failed to send mailing {mailing.id} to {client.email}: {str(e)}")


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Проверяем каждую минуту рассылки для отправки
        scheduler.add_job(
            self.check_mailings,
            trigger=CronTrigger(second="*/30"),  # Каждые 30 секунд
            id="check_mailings",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'check_mailings'.")

        # Удаляем старые записи выполнения задач
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")

    def check_mailings(self):
        now = datetime.now().astimezone()
        mailings = Mailing.objects.filter(
            status=Mailing.STARTED,
            start_time__lte=now,
            end_time__gte=now
        )

        for mailing in mailings:
            send_mailing(mailing.id)

        # Помечаем завершенные рассылки
        Mailing.objects.filter(
            status=Mailing.STARTED,
            end_time__lt=now
        ).update(status=Mailing.COMPLETED)
