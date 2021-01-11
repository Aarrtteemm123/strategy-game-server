from django_mongoengine import mongo_admin as admin

# Register your models here.
from polls.models import News


class NewsAdmin(admin.DocumentAdmin):
    model = News
    fields = ('title', 'text')


admin.site.register(News, NewsAdmin)
#admin.site.register(News)