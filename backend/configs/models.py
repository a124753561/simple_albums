from django.db import models


class SystemConfig(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name="配置键")
    value = models.TextField(blank=True, default="", verbose_name="配置值")
    description = models.CharField(max_length=200, blank=True, default="", verbose_name="说明")

    class Meta:
        db_table = "system_config"
        verbose_name = "系统配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.key
