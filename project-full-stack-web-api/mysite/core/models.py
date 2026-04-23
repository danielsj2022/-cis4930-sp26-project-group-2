from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name


class DataRun(models.Model):
    SOURCE_CHOICES = [
        ("csv", "CSV Import"),
        ("api", "API Fetch"),
    ]

    source = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_source_display()} - {self.created_at:%Y-%m-%d %H:%M}"


class Record(models.Model):
    SOURCE_CHOICES = [
        ("csv", "CSV Import"),
        ("api", "API Fetch"),
    ]

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="records"
    )
    date = models.DateField()
    temp_max = models.FloatField()
    temp_min = models.FloatField()
    precipitation = models.FloatField(default=0)
    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default="csv"
    )
    run = models.ForeignKey(
        DataRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="records"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "city__name"]
        unique_together = ("city", "date")

    def __str__(self):
        return f"{self.city.name} - {self.date}"
