from rest_framework import serializers
from .models import Category, Album, Photo


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "parent", "sort_order", "children", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_children(self, obj):
        children = obj.children.all()
        if children.exists():
            return CategoryFlatSerializer(children, many=True).data
        return []

    def validate_parent(self, value):
        if value and value.parent is not None:
            raise serializers.ValidationError("分类最多支持两级，不能选择二级分类作为父分类")
        return value

    def create(self, validated_data):
        if "parent" in validated_data and validated_data["parent"]:
            parent = validated_data["parent"]
            if parent.parent is not None:
                raise serializers.ValidationError({"parent": "分类最多支持两级"})
        return super().create(validated_data)


class CategoryFlatSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True, default="")

    class Meta:
        model = Category
        fields = ["id", "name", "parent", "parent_name", "sort_order", "created_at"]


class CategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ["id", "album", "name", "url", "file_size", "width", "height", "sort_order", "created_at"]
        read_only_fields = ["id", "created_at"]


class AlbumListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Album
        fields = ["id", "title", "cover", "category", "category_name", "homepage_show", "is_disabled",
                  "sort_order", "photo_count", "created_at", "updated_at"]
        read_only_fields = ["id", "photo_count", "created_at", "updated_at"]


class AlbumDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ["id", "title", "description", "cover", "category", "category_name",
                  "homepage_show", "is_disabled", "sort_order", "photo_count", "photos", "created_at", "updated_at"]
        read_only_fields = ["id", "photo_count", "created_at", "updated_at"]


class AlbumCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ["id", "title", "description", "cover", "category", "homepage_show", "is_disabled", "sort_order"]
        read_only_fields = ["id"]
