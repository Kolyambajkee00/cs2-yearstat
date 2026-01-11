# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import requests
from django.core.cache import cache


class CS2Player(models.Model):
    """CS2 Player profile with Steam data"""
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cs2_profile')
    steam_id = models.CharField('Steam ID', max_length=20, unique=True)

    # Data from Steam API
    steam_nickname = models.CharField('Steam Nickname', max_length=100, blank=True)
    steam_avatar = models.URLField('Steam Avatar', max_length=500, blank=True)
    steam_profile_url = models.URLField('Profile URL', max_length=500, blank=True)
    country_code = models.CharField('Country Code', max_length=10, blank=True)

    # Statistics from Steam
    cs2_hours = models.FloatField('Hours in CS2', default=0)
    last_steam_update = models.DateTimeField('Last Steam Update', null=True, blank=True)

    # Settings
    is_public = models.BooleanField('Public Profile', default=True)

    # Timestamps
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    class Meta:
        verbose_name = 'CS2 Player'
        verbose_name_plural = 'CS2 Players'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.steam_nickname or 'No nickname'} ({self.steam_id})"

    def get_country_flag(self):
        """Get country flag emoji"""
        if self.country_code:
            # Convert country code to flag emoji
            # RU -> 🇷🇺, US -> 🇺🇸, etc.
            offset = 127397  # Offset for regional indicator symbols
            try:
                return ''.join(chr(ord(c) + offset) for c in self.country_code.upper())
            except:
                return ''
        return ''

    def update_from_steam(self, api_key):
        """Update data from Steam API"""
        try:
            # Cache requests for 5 minutes
            cache_key = f"steam_profile_{self.steam_id}"
            cached_data = cache.get(cache_key)

            if not cached_data:
                # 1. Get player profile
                url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={self.steam_id}"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if data['response']['players']:
                        player = data['response']['players'][0]
                        self.steam_nickname = player.get('personaname', '')
                        self.steam_avatar = player.get('avatarfull', '')
                        self.steam_profile_url = player.get('profileurl', '')
                        self.country_code = player.get('loccountrycode', '')

                # 2. Get playtime
                url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={self.steam_id}&include_appinfo=1"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    games = data['response'].get('games', [])
                    for game in games:
                        if game['appid'] == 730:  # CS2 appid
                            self.cs2_hours = round(game.get('playtime_forever', 0) / 60, 1)  # Minutes -> hours
                            break

                cache.set(cache_key, True, 300)  # Cache for 5 minutes

            self.last_steam_update = timezone.now()
            self.save()
            return True

        except Exception as e:
            print(f"Error updating from Steam: {e}")
            return False

    @property
    def total_matches(self):
        """Total matches played"""
        return self.monthly_stats.aggregate(total=models.Sum('matches_played'))['total'] or 0

    @property
    def overall_kd(self):
        """Overall K/D ratio"""
        kills = self.monthly_stats.aggregate(total=models.Sum('kills'))['total'] or 0
        deaths = self.monthly_stats.aggregate(total=models.Sum('deaths'))['total'] or 0
        return round(kills / deaths, 2) if deaths > 0 else 0.0

    @property
    def overall_win_rate(self):
        """Overall win rate"""
        wins = self.monthly_stats.aggregate(total=models.Sum('wins'))['total'] or 0
        total = self.total_matches
        return round((wins / total) * 100, 1) if total > 0 else 0.0

    @property
    def overall_hs_percent(self):
        """Overall headshot percentage"""
        headshots = self.monthly_stats.aggregate(total=models.Sum('headshots'))['total'] or 0
        kills = self.monthly_stats.aggregate(total=models.Sum('kills'))['total'] or 0
        return round((headshots / kills) * 100, 1) if kills > 0 else 0.0

    @property
    def best_month_kd(self):
        """Best monthly K/D"""
        best = self.monthly_stats.order_by('-kd_ratio').first()
        return best.kd_ratio if best else 0.0

    @property
    def favorite_weapon(self):
        """Most used weapon"""
        # We'll implement this later with WeaponStat model
        return "AK-47"


class MonthlyStat(models.Model):
    """Monthly statistics (manual input)"""
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    player = models.ForeignKey(CS2Player, on_delete=models.CASCADE, related_name='monthly_stats')
    year = models.IntegerField('Year', default=2025)
    month = models.IntegerField('Month', choices=MONTH_CHOICES)

    # Main statistics
    matches_played = models.IntegerField('Matches Played', default=0)
    kills = models.IntegerField('Kills', default=0)
    deaths = models.IntegerField('Deaths', default=0)
    assists = models.IntegerField('Assists', default=0)
    headshots = models.IntegerField('Headshots', default=0)
    wins = models.IntegerField('Wins', default=0)

    # Additional statistics
    mvps = models.IntegerField('MVPs', default=0)
    damage_per_round = models.FloatField('ADR (Damage per Round)', default=0)
    utility_damage = models.IntegerField('Utility Damage', default=0)
    clutches_won = models.IntegerField('Clutches Won', default=0)
    plants = models.IntegerField('Bombs Planted', default=0)
    defuses = models.IntegerField('Bombs Defused', default=0)

    # Notes
    notes = models.TextField('Notes', blank=True)

    # Timestamps
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    class Meta:
        verbose_name = 'Monthly Statistics'
        verbose_name_plural = 'Monthly Statistics'
        unique_together = ['player', 'year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        month_name = dict(self.MONTH_CHOICES).get(self.month, '')
        return f"{self.player.steam_nickname} - {month_name} {self.year}"

    @property
    def kd_ratio(self):
        """Monthly K/D ratio"""
        return round(self.kills / self.deaths, 2) if self.deaths > 0 else 0.0

    @property
    def win_rate(self):
        """Monthly win rate"""
        return round((self.wins / self.matches_played) * 100, 1) if self.matches_played > 0 else 0.0

    @property
    def headshot_percent(self):
        """Monthly headshot percentage"""
        return round((self.headshots / self.kills) * 100, 1) if self.kills > 0 else 0.0

    @property
    def adr(self):
        """Average Damage per Round"""
        return round(self.damage_per_round, 1) if self.damage_per_round else 0.0


class WeaponStat(models.Model):
    """Weapon statistics for a month"""
    WEAPON_CHOICES = [
        ('ak47', 'AK-47'),
        ('m4a4', 'M4A4'),
        ('m4a1s', 'M4A1-S'),
        ('awp', 'AWP'),
        ('deagle', 'Desert Eagle'),
        ('glock', 'Glock-18'),
        ('usp', 'USP-S'),
        ('p250', 'P250'),
        ('mac10', 'MAC-10'),
        ('mp9', 'MP9'),
        ('nova', 'Nova'),
        ('xm1014', 'XM1014'),
        ('mag7', 'MAG-7'),
        ('sawedoff', 'Sawed-Off'),
        ('negev', 'Negev'),
        ('m249', 'M249'),
        ('other', 'Other Weapon'),
    ]

    monthly_stat = models.ForeignKey(MonthlyStat, on_delete=models.CASCADE, related_name='weapon_stats')
    weapon_name = models.CharField('Weapon', max_length=20, choices=WEAPON_CHOICES)
    custom_name = models.CharField('Custom Name', max_length=50, blank=True)

    kills = models.IntegerField('Kills', default=0)
    headshots = models.IntegerField('Headshots', default=0)
    shots_fired = models.IntegerField('Shots Fired', default=0)
    hits = models.IntegerField('Hits', default=0)

    class Meta:
        verbose_name = 'Weapon Statistics'
        verbose_name_plural = 'Weapon Statistics'
        unique_together = ['monthly_stat', 'weapon_name']
        ordering = ['-kills']

    def __str__(self):
        return f"{self.get_weapon_name_display()} ({self.kills} kills)"

    @property
    def display_name(self):
        return self.custom_name if self.custom_name else self.get_weapon_name_display()

    @property
    def headshot_percent(self):
        return round((self.headshots / self.kills) * 100, 1) if self.kills > 0 else 0.0

    @property
    def accuracy(self):
        return round((self.hits / self.shots_fired) * 100, 1) if self.shots_fired > 0 else 0.0


class MapStat(models.Model):
    """Map statistics for a month"""
    MAP_CHOICES = [
        ('mirage', 'Mirage'),
        ('inferno', 'Inferno'),
        ('dust2', 'Dust II'),
        ('overpass', 'Overpass'),
        ('nuke', 'Nuke'),
        ('vertigo', 'Vertigo'),
        ('ancient', 'Ancient'),
        ('anubis', 'Anubis'),
        ('cache', 'Cache'),
        ('train', 'Train'),
        ('office', 'Office'),
        ('agency', 'Agency'),
    ]

    monthly_stat = models.ForeignKey(MonthlyStat, on_delete=models.CASCADE, related_name='map_stats')
    map_name = models.CharField('Map', max_length=20, choices=MAP_CHOICES)

    matches_played = models.IntegerField('Matches Played', default=0)
    wins = models.IntegerField('Wins', default=0)

    # Additional map statistics
    kills = models.IntegerField('Kills', default=0)
    deaths = models.IntegerField('Deaths', default=0)
    plants = models.IntegerField('Bombs Planted', default=0)
    defuses = models.IntegerField('Bombs Defused', default=0)

    notes = models.TextField('Notes', blank=True)

    class Meta:
        verbose_name = 'Map Statistics'
        verbose_name_plural = 'Map Statistics'
        unique_together = ['monthly_stat', 'map_name']
        ordering = ['-matches_played']

    def __str__(self):
        return f"{self.get_map_name_display()} ({self.matches_played} matches)"

    @property
    def win_rate(self):
        return round((self.wins / self.matches_played) * 100, 1) if self.matches_played > 0 else 0.0

    @property
    def kd_ratio(self):
        return round(self.kills / self.deaths, 2) if self.deaths > 0 else 0.0