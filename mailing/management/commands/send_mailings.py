from django.core.management.base import BaseCommand
from django.utils import timezone
from mailing.models import Mailing, MailingLog
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


class Command(BaseCommand):
    help = 'Send scheduled mailings'

    def handle(self, *args, **options):
        now = timezone.now()

        # Получаем рассылки, которые нужно отправить
        mailings = Mailing.objects.filter(
            status=Mailing.STARTED,
            start_time__lte=now,
            end_time__gte=now
        )

        for mailing in mailings:
            self.stdout.write(f'Processing mailing {mailing.id}')

            for client in mailing.clients.all():
                try:
                    # Отправляем письмо
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[client.email],
                        fail_silently=False,
                    )

                    # Логируем успешную отправку
                    MailingLog.objects.create(
                        mailing=mailing,
                        status=MailingLog.SUCCESS,
                        response='Email sent successfully'
                    )

                    self.stdout.write(f'Email sent to {client.email}')

                except Exception as e:
                    # Логируем ошибку
                    MailingLog.objects.create(
                        mailing=mailing,
                        status=MailingLog.FAILURE,
                        response=str(e)
                    )

                    self.stdout.write(f'Failed to send email to {client.email}: {str(e)}')

        # Помечаем завершенные рассылки
        completed_mailings = Mailing.objects.filter(
            status=Mailing.STARTED,
            end_time__lt=now
        )

        for mailing in completed_mailings:
            mailing.status = Mailing.COMPLETED
            mailing.save()
            self.stdout.write(f'Marked mailing {mailing.id} as completed')
