from django.contrib import admin
from .models import Player, MonthlyStats, WeaponStats, MapStats, TeammateStats

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'steam_id', 'country', 'total_hours', 'last_updated')
    search_fields = ('nickname', 'steam_id')
    list_filter = ('country', 'last_updated')
    readonly_fields = ('total_matches', 'overall_kd', 'overall_win_rate', 'overall_headshot_percent')

@admin.register(MonthlyStats)
class MonthlyStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'year', 'month', 'matches_played', 'kd_ratio', 'win_rate', 'headshot_percent')
    list_filter = ('year', 'month', 'player')
    search_fields = ('player__nickname',)

@admin.register(WeaponStats)
class WeaponStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'weapon_name', 'kills', 'headshot_percent', 'accuracy')
    list_filter = ('weapon_name',)
    search_fields = ('player__nickname', 'weapon_name')

@admin.register(MapStats)
class MapStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'map_name', 'matches_played', 'win_rate')
    list_filter = ('map_name',)
    search_fields = ('player__nickname', 'map_name')

@admin.register(TeammateStats)
class TeammateStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'teammate_nickname', 'matches_together', 'win_rate_together')
    list_filter = ('player',)
    search_fields = ('player__nickname', 'teammate_nickname')