from djongo import models


class MyDocument(models.Model):
    word = models.CharField(max_length=100)
    definition = models.TextField(blank=True, null=True)
    synonyms = models.JSONField(blank=True, null=True)
    antonyms = models.JSONField(blank=True, null=True)
    # topics = models.CharField(max_length=100, blank=True, null=True) # omit for now

    class Meta:
        db_table = 'enpyOrdered'
