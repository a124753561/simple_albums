from django.core.management.base import BaseCommand
from configs.models import SystemConfig


class Command(BaseCommand):
    help = "初始化系统配置默认值"

    DEFAULTS = {
        "wechat": "",
        "wechat_qrcode": "",
        "email": "",
        "phone": "",
        "about": "",
    }

    def handle(self, *args, **options):
        for key, value in self.DEFAULTS.items():
            _, created = SystemConfig.objects.get_or_create(
                key=key, defaults={"value": value, "description": key}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"创建配置: {key}"))
        self.stdout.write(self.style.SUCCESS("系统配置初始化完成"))
