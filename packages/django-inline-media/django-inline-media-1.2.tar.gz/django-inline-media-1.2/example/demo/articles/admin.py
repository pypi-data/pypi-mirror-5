from django.contrib import admin

from inline_media.admin import AdminTextFieldWithInlinesMixin

from demo.articles.models import Article

class ArticleAdmin(AdminTextFieldWithInlinesMixin, admin.ModelAdmin):
    list_display  = ('title', 'publish')
    list_filter   = ('publish',)
    search_fields = ('title', 'abstract', 'body')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = ((None, 
                  {'fields': ('title', 'slug', 'abstract', 'body', 
                              'publish',)}),)

admin.site.register(Article, ArticleAdmin)
