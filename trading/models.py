from django.db import models

class Market(models.Model):
    symbol = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    open = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    close = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('symbol', 'timestamp')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['timestamp']),
            # Add composite index if needed for faster lookups by both symbol and timestamp
            models.Index(fields=['symbol', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.timestamp}"
