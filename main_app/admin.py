from django.contrib import admin
from .models import UserMod,CategoryMod,DescriptionMod,ButtonMod,save_user_data,TeacherMod,ParentMod

admin.site.register(UserMod)
admin.site.register(ParentMod)
admin.site.register(TeacherMod)
admin.site.register(CategoryMod)
admin.site.register(ButtonMod)
admin.site.register(DescriptionMod)
admin.site.register(save_user_data)
