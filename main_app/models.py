from django.db import models

class ParentMod(models.Model):
    telegram_id = models.BigIntegerField(verbose_name='Telegram ID')
    parent_name = models.CharField(max_length=100,verbose_name='ФИО')
    school = models.CharField(max_length=100,verbose_name='Maktab')
    class_name = models.CharField(max_length=100,verbose_name='klass')
    city = models.CharField(max_length=100,verbose_name='Tuman')
    parent_number = models.CharField(max_length=100,verbose_name='Telefon rakami')
    payment = models.BooleanField(default=False,verbose_name='Tolov')
    language = models.CharField(max_length=5,verbose_name='Til')
    
    def __str__(self):
        return self.parent_name
    
    class Meta:
        verbose_name = 'Ota/Ona'
        verbose_name_plural = 'Otalar/Onalar'


class TeacherMod(models.Model):
    telegram_id = models.BigIntegerField(verbose_name='Telegram ID')
    teacher_name = models.CharField(max_length=100,verbose_name='ФИО')
    school = models.CharField(max_length=100,verbose_name='Maktab')
    class_name = models.CharField(max_length=100,verbose_name='klass')
    city = models.CharField(max_length=100,verbose_name='Tuman')
    teacher_number = models.CharField(max_length=100,verbose_name='Telefon rakami')
    payment = models.BooleanField(default=False,verbose_name='Tolov')
    language = models.CharField(max_length=5,verbose_name='Til')
    
    def __str__(self):
        return self.teacher_name

    class Meta:
        verbose_name = 'Uztoz'
        verbose_name_plural = 'Uztozlar'

class save_user_data(models.Model):
    telegram_id = models.BigIntegerField(verbose_name='Telegram ID',null=True,blank=True)
    who = models.CharField(max_length=10,null=True,blank=True,verbose_name='Qaysi foydalanuvchi')
    school = models.CharField(max_length=100,verbose_name='Maktab',null=True,blank=True)
    city = models.CharField(max_length=100,verbose_name='Tuman',null=True,blank=True)
    class_name = models.CharField(max_length=100,verbose_name='class_name',null=True,blank=True)
    teacher_name = models.CharField(max_length=100,verbose_name='teacher_name',null=True,blank=True)
    student_name = models.CharField(max_length=100,verbose_name='student_name',null=True,blank=True)
    student_number = models.CharField(max_length=100,verbose_name='student_number',null=True,blank=True)
    teacher_number = models.CharField(max_length=100,verbose_name='teacher_number',null=True,blank=True)
    language = models.CharField(max_length=5,verbose_name='Til',null=True,blank=True)
    code = models.CharField(max_length=50,verbose_name='Code',null=True,blank=True)
    
    def __str__(self):
        return self.teacher_name if self.teacher_name else self.student_name
    
    class Meta:
        verbose_name = 'save_user_data'
        verbose_name_plural = 'save_user_datalar'

class UserMod(models.Model):
    parents = models.ForeignKey(to=ParentMod,on_delete=models.CASCADE,verbose_name='Parents',null=True,blank=True)
    teacher_name = models.ForeignKey(to=TeacherMod,on_delete=models.CASCADE,verbose_name='Teachers',null=True,blank=True)
    code = models.CharField(max_length=50,verbose_name='Code')
    telegram_id = models.BigIntegerField(verbose_name='Telegram ID')
    student_name = models.CharField(max_length=100,verbose_name='student_name')
    teacher_name1 = models.CharField(max_length=100,verbose_name='teacher_name1')
    school = models.CharField(max_length=100,verbose_name='school')
    class_name = models.CharField(max_length=100,verbose_name='class_name')
    city = models.CharField(max_length=100,verbose_name='Tuman')
    student_number = models.CharField(max_length=100,verbose_name='student_number')
    teacher_number = models.CharField(max_length=100,verbose_name='teacher_number')
    payment = models.BooleanField(default=False,verbose_name='Tolov')
    language = models.CharField(max_length=5,verbose_name='Til')

    def __str__(self):
        return self.student_name
    
    class Meta:
        verbose_name = 'Okuvchi'
        verbose_name_plural = 'Okuvchilar'

class CategoryMod(models.Model):
    name = models.CharField(max_length=100,verbose_name='holati')

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Holat'
        verbose_name_plural = 'Holatlar'

class DescriptionMod(models.Model):
    title = models.OneToOneField(to=CategoryMod,on_delete=models.CASCADE,verbose_name='holat')
    uz_text = models.TextField(verbose_name='Malumot uz')
    ru_text = models.TextField(verbose_name='Malumot ru')

    def __str__(self) -> str:
        return self.title.name

    class Meta:
        verbose_name = 'Description'
        verbose_name_plural = 'Descriptions'

class ButtonMod(models.Model):
    uz_button = models.CharField(max_length=50,verbose_name='Uzbekcha')
    ru_button = models.CharField(max_length=50,verbose_name='Russia')

    def __str__(self):
        return self.ru_button
        
    class Meta:
        verbose_name = 'ButtonMod'
        verbose_name_plural = 'ButtonMods'
