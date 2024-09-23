from django.contrib import admin
from .models import UserMod,CategiryMod,DescriptionMod,ButtonMod,save_user_data

admin.site.register(UserMod)
admin.site.register(save_user_data)
admin.site.register(CategiryMod)
admin.site.register(ButtonMod)
admin.site.register(DescriptionMod)
