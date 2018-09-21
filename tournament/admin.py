from django.contrib import admin
from .models import Tournament, Match, Bet

# Register your models here.

class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'tournament', 'home_team', 'away_team', 'round', 'home_goals', 'away_goals', 'match_date')
    date_hierarchy = 'match_date'
    ordering = ('-match_date',)
    #list_filter = ('home_team',)
    #search_fields = ('tournament__name',) #Problem jak filtrowac po home_team i away_team

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'general_classification_only')

admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Bet)
