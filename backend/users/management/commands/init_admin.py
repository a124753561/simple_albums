from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = "创建超级管理员账号 admin/admin321"

    def handle(self, *args, **options):
        if User.objects.filter(username="admin").exists():
            self.stdout.write(self.style.WARNING("管理员账号已存在，跳过创建"))
            return
        User.objects.create_superuser(
            username="admin",
            password="admin321",
            email="admin@example.com",
        )
        self.stdout.write(self.style.SUCCESS("超级管理员创建成功: admin/admin321"))
