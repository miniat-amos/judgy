from django.db import models

# Create your models here.
class TestTable(models.Model):
    test_id = models.BigAutoField(primary_key=True)
    test_name = models.CharField(max_length=200, default="Test")