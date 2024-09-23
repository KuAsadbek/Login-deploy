from django.db import models

class TeacherMod(models.Model):
    telegram_id = models.BigIntegerField(verbose_name='Telegram ID',null=True,blank=True)
    full_name = models.CharField(max_length=100,verbose_name='ФИО',null=True,blank=True)
    school = models.CharField(max_length=100,verbose_name='Maktab',null=True,blank=True)
    class_name = models.CharField(max_length=100,verbose_name='klass',null=True,blank=True)
    city = models.CharField(max_length=100,verbose_name='Tuman',null=True,blank=True)
    number = models.CharField(max_length=100,verbose_name='Telefon rakami',null=True,blank=True)
    language = models.CharField(max_length=5,verbose_name='Til',null=True,blank=True)
    
    def __str__(self):
        return self.full_name

class save_user_data(models.Model):
    telegram_id = models.BigIntegerField(verbose_name='Telegram ID',null=True,blank=True)
    full_name = models.CharField(max_length=100,verbose_name='ФИО',null=True,blank=True)
    school = models.CharField(max_length=100,verbose_name='Maktab',null=True,blank=True)
    class_name = models.CharField(max_length=100,verbose_name='klass',null=True,blank=True)
    city = models.CharField(max_length=100,verbose_name='Tuman',null=True,blank=True)
    number = models.CharField(max_length=100,verbose_name='Telefon rakami',null=True,blank=True)
    language = models.CharField(max_length=5,verbose_name='Til',null=True,blank=True)
    
    def __str__(self):
        return self.full_name

class UserMod(models.Model):
    telegram_id = models.BigIntegerField(verbose_name='Telegram ID')
    full_name = models.CharField(max_length=100,verbose_name='ФИО')
    school = models.CharField(max_length=100,verbose_name='Maktab')
    city = models.CharField(max_length=100,verbose_name='Tuman')
    number = models.CharField(max_length=100,verbose_name='Telefon rakami')
    payment = models.BooleanField(default=False,verbose_name='Tolov')
    language = models.CharField(max_length=5,verbose_name='Til')

    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class CategiryMod(models.Model):
    name = models.CharField(max_length=100,verbose_name='holat')

    def __str__(self) -> str:
        return self.name

class DescriptionMod(models.Model):
    title = models.OneToOneField(to=CategiryMod,on_delete=models.CASCADE,verbose_name='holat')
    uz_text = models.TextField(verbose_name='Malumot uz')
    ru_text = models.TextField(verbose_name='Malumot ru')

    def __str__(self) -> str:
        return self.title.name

class ButtonMod(models.Model):
    ru_button = models.CharField(max_length=50,verbose_name='Russia')
    uz_button = models.CharField(max_length=50,verbose_name='Uzbekcha')

    def __str__(self):
        return self.ru_button
        
    class Meta:
        verbose_name = 'ButtonMod'
        verbose_name_plural = 'ButtonMods'
