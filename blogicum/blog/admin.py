from django.contrib import admin

from .models import Post, Category, Location


admin.site.empty_value_display = "Не задано"


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "slug",
        "is_published",
    )
    list_editable = ("is_published",)
    search_fields = ("title",)


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


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location)
