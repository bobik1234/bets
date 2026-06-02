from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from tournament.db_handler import match_list, get_payers, bet_list


class Command(BaseCommand):
    help = 'Send email reminders for unbet matches today and tomorrow'

    def handle(self, *args, **options):
        today = datetime.today().date()
        tomorrow = today + timedelta(days=1)

        matches = match_list()
        upcoming_matches = [m for m in matches if m.match_date and m.match_date.date() in (today, tomorrow)]

        if not upcoming_matches:
            self.stdout.write('No matches today or tomorrow.')
            return

        matches_id = [m.id for m in upcoming_matches]

        for player in get_payers():
            if not player.notifications or not player.user.email:
                continue

            unbet_ids = matches_id.copy()
            for bet in bet_list(user=player.user):
                if bet.match.id in unbet_ids:
                    unbet_ids.remove(bet.match.id)

            if unbet_ids:
                unbet_matches = [m for m in upcoming_matches if m.id in unbet_ids]
                match_lines = '\n'.join(
                    f'{m.teams_to_string()} UTC {m.match_date.strftime("%H:%M")} ({settings.TIME_ZONE} {timezone.localtime(m.match_date).strftime("%H:%M")})'
                    for m in unbet_matches
                )

                email_content = (
                    f'Hi {player.user.username}\n\n'
                    f'Masz nieobstawione mecze. Uważaj żeby się nie spóźnić.\n'
                    f'You have unbet matches. Be careful not to be late.\n\n'
                    f'{match_lines}\n\n'
                    f'Best regards\n/Henio'
                )

                send_mail(
                    subject="Henio reminds of matches to bet",
                    message=email_content,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[player.user.email]
                )
                self.stdout.write(f'Sent reminder to {player.user.username}')

        self.stdout.write('Done.')
