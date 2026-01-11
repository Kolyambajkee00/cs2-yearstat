from django.db import models


class Player(models.Model):
    """CS2 Player model"""
    steam_id = models.CharField(max_length=20, unique=True)
    nickname = models.CharField(max_length=100)
    avatar_url = models.URLField(max_length=500, blank=True)
    country = models.CharField(max_length=50, blank=True)
    total_hours = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Player"
        verbose_name_plural = "Players"
        ordering = ['-last_updated']

    def __str__(self):
        return f"{self.nickname} ({self.steam_id})"

    @property
    def total_matches(self):
        """Total matches played"""
        return sum(month.matches_played for month in self.monthly_stats.all())

    @property
    def total_kills(self):
        """Total kills"""
        return sum(month.kills for month in self.monthly_stats.all())

    @property
    def total_deaths(self):
        """Total deaths"""
        return sum(month.deaths for month in self.monthly_stats.all())

    @property
    def overall_kd(self):
        """Overall K/D ratio"""
        if self.total_deaths > 0:
            return round(self.total_kills / self.total_deaths, 2)
        return 0.0

    @property
    def overall_win_rate(self):
        """Overall win rate"""
        total_wins = sum(month.wins for month in self.monthly_stats.all())
        if self.total_matches > 0:
            return round((total_wins / self.total_matches) * 100, 1)
        return 0.0

    @property
    def overall_headshot_percent(self):
        """Overall headshot percentage"""
        total_headshots = sum(month.headshots for month in self.monthly_stats.all())
        if self.total_kills > 0:
            return round((total_headshots / self.total_kills) * 100, 1)
        return 0.0

    @property
    def best_teammate(self):
        """Get the most frequent teammate"""
        teammates = self.teammates.all()
        if teammates:
            return teammates.first()  # уже отсортировано по matches_together
        return None


class MonthlyStats(models.Model):
    """Monthly statistics"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='monthly_stats')
    year = models.IntegerField()
    month = models.IntegerField()  # 1-12

    matches_played = models.IntegerField(default=0)
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    headshots = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Monthly Statistics"
        verbose_name_plural = "Monthly Statistics"
        unique_together = ['player', 'year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.player.nickname} - {self.year}/{self.month:02d}"

    @property
    def kd_ratio(self):
        """Monthly K/D ratio"""
        if self.deaths > 0:
            return round(self.kills / self.deaths, 2)
        return 0.0

    @property
    def win_rate(self):
        """Monthly win rate"""
        if self.matches_played > 0:
            return round((self.wins / self.matches_played) * 100, 1)
        return 0.0

    @property
    def headshot_percent(self):
        """Monthly headshot percentage"""
        if self.kills > 0:
            return round((self.headshots / self.kills) * 100, 1)
        return 0.0


class WeaponStats(models.Model):
    """Weapon statistics"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='weapon_stats')
    weapon_name = models.CharField(max_length=50)

    kills = models.IntegerField(default=0)
    headshots = models.IntegerField(default=0)
    shots_fired = models.IntegerField(default=0)
    hits = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Weapon Statistics"
        verbose_name_plural = "Weapon Statistics"
        unique_together = ['player', 'weapon_name']
        ordering = ['-kills']

    def __str__(self):
        return f"{self.player.nickname} - {self.weapon_name}"

    @property
    def headshot_percent(self):
        """Weapon headshot percentage"""
        if self.kills > 0:
            return round((self.headshots / self.kills) * 100, 1)
        return 0.0

    @property
    def accuracy(self):
        """Weapon accuracy"""
        if self.shots_fired > 0:
            return round((self.hits / self.shots_fired) * 100, 1)
        return 0.0


class MapStats(models.Model):
    """Map statistics"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='map_stats')
    map_name = models.CharField(max_length=50)

    matches_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Map Statistics"
        verbose_name_plural = "Map Statistics"
        unique_together = ['player', 'map_name']
        ordering = ['-matches_played']

    def __str__(self):
        return f"{self.player.nickname} - {self.map_name}"

    @property
    def win_rate(self):
        """Map win rate"""
        if self.matches_played > 0:
            return round((self.wins / self.matches_played) * 100, 1)
        return 0.0


class TeammateStats(models.Model):
    """Statistics about teammates"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='teammates')
    teammate_steam_id = models.CharField(max_length=20)
    teammate_nickname = models.CharField(max_length=100)
    matches_together = models.IntegerField(default=0)
    wins_together = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Teammate Statistics"
        verbose_name_plural = "Teammate Statistics"
        unique_together = ['player', 'teammate_steam_id']
        ordering = ['-matches_together']

    def __str__(self):
        return f"{self.player.nickname} + {self.teammate_nickname}"

    @property
    def win_rate_together(self):
        """Win rate when playing together"""
        if self.matches_together > 0:
            return round((self.wins_together / self.matches_together) * 100, 1)
        return 0.0