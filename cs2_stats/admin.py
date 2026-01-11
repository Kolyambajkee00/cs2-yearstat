from django.contrib import admin
from .models import CS2Player, MonthlyStat, WeaponStat, MapStat


@admin.register(CS2Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'steam_id', 'country', 'total_hours', 'last_updated')
    search_fields = ('nickname', 'steam_id')
    list_filter = ('country', 'last_updated')
    readonly_fields = ('total_matches', 'overall_kd', 'overall_win_rate', 'overall_headshot_percent')


@admin.register(MonthlyStat)
class MonthlyStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'year', 'month', 'matches_played', 'kd_ratio', 'win_rate', 'headshot_percent')
    list_filter = ('year', 'month', 'player')
    search_fields = ('player__nickname',)
    readonly_fields = ('kd_ratio', 'win_rate', 'headshot_percent')


@admin.register(WeaponStat)
class WeaponStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'weapon_name', 'kills', 'headshot_percent', 'accuracy')
    list_filter = ('weapon_name',)
    search_fields = ('player__nickname', 'weapon_name')
    readonly_fields = ('headshot_percent', 'accuracy')


@admin.register(MapStat)
class MapStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'map_name', 'matches_played', 'win_rate')
    list_filter = ('map_name',)
    search_fields = ('player__nickname', 'map_name')
    readonly_fields = ('win_rate',)


