from django.db import models

# Auto-generated models from entities.json config

class Player(models.Model):
    username = models.CharField(max_length=50, unique=True)
    inventory = models.ManyToManyField('Item', blank=True)
    guild = models.ForeignKey('Guild', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Player'
        verbose_name_plural = 'Players'
        db_table = 'player'

    def __str__(self):
        return f'Player {self.pk}'

class Match(models.Model):
    match_id = models.CharField(max_length=32, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Match'
        verbose_name_plural = 'Matches'
        db_table = 'match'

    def __str__(self):
        return f'Match {self.pk}'

# Placeholder models for referenced relationships
class Item(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Guild(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name