from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="分类名称")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True,
        related_name="children", verbose_name="父分类"
    )
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "category"
        verbose_name = "相册分类"
        verbose_name_plural = verbose_name
        ordering = ["sort_order", "id"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=200, verbose_name="标题")
    description = models.TextField(blank=True, default="", verbose_name="描述")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="albums", verbose_name="所属分类"
    )
    cover = models.URLField(blank=True, default="", verbose_name="封面图")
    homepage_show = models.BooleanField(default=False, verbose_name="首页显示")
    is_disabled = models.BooleanField(default=False, verbose_name="禁用")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    photo_count = models.IntegerField(default=0, verbose_name="图片数量")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "album"
        verbose_name = "相册"
        verbose_name_plural = verbose_name
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return self.title


class Photo(models.Model):
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, related_name="photos", verbose_name="所属相册"
    )
    name = models.CharField(max_length=200, verbose_name="图片名称")
    url = models.URLField(max_length=500, verbose_name="七牛云URL")
    file_size = models.BigIntegerField(default=0, verbose_name="文件大小")
    width = models.IntegerField(default=0, verbose_name="宽度")
    height = models.IntegerField(default=0, verbose_name="高度")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "photo"
        verbose_name = "图片"
        verbose_name_plural = verbose_name
        ordering = ["sort_order", "id"]
