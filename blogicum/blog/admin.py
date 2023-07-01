from django.contrib import admin

from blog.models import Post, Category, Location


admin.site.empty_value_display = "Не задано"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "slug",
        "is_published",
    )
    list_editable = ("is_published",)
    search_fields = ("title",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "short_text",
        "author",
        "location",
        "category",
        "is_published",
    )

    list_editable = (
        "is_published",
        "category",
    )
    search_fields = ("title",)
    list_filter = ("is_published",)
    list_display_links = ("title",)


admin.site.register(Location)
