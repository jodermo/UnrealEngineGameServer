from django.db import models
from django.db.models import CASCADE, SET_NULL, PROTECT, SET_DEFAULT, DO_NOTHING
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Auto-generated models

class Item(models.Model):
    """
    Item model
    Auto-generated from entities.json configuration
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    item_type = models.CharField(max_length=50, default='common')
    value = models.IntegerField(default=0)
    rarity = models.CharField(max_length=20, default='common')

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return str(self.name)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('item-detail', kwargs={'pk': self.pk})

    @classmethod
    def get_recent(cls, limit=10):
        return cls.objects.order_by('-id')[:limit]


class Guild(models.Model):
    """
    Guild model
    Auto-generated from entities.json configuration
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    member_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Guild'
        verbose_name_plural = 'Guilds'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return str(self.name)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('guild-detail', kwargs={'pk': self.pk})

    @classmethod
    def get_recent(cls, limit=10):
        return cls.objects.order_by('-id')[:limit]


class Player(models.Model):
    """
    Player model
    Auto-generated from entities.json configuration
    """

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Player'
        verbose_name_plural = 'Players'
        ordering = ('-created_at',)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return str(self.username)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('player-detail', kwargs={'pk': self.pk})

    @classmethod
    def get_recent(cls, limit=10):
        return cls.objects.order_by('-id')[:limit]


class Match(models.Model):
    """
    Match model
    Auto-generated from entities.json configuration
    """

    match_id = models.CharField(max_length=32, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey('Player', on_delete=DO_NOTHING, null=True)

    class Meta:
        verbose_name = 'Match'
        verbose_name_plural = 'Matchs'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return str(self.match_id)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('match-detail', kwargs={'pk': self.pk})

    @classmethod
    def get_recent(cls, limit=10):
        return cls.objects.order_by('-id')[:limit]


# Utility functions
def get_all_model_counts():
    counts = {}
    counts['player'] = Player.objects.count()
    counts['match'] = Match.objects.count()
    counts['item'] = Item.objects.count()
    counts['guild'] = Guild.objects.count()
    return counts

def get_model_by_name(model_name):
    models_map = {
        'player': Player,
        'match': Match,
        'item': Item,
        'guild': Guild,
    }
    return models_map.get(model_name.lower())