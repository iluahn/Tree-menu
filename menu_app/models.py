from django.db import models

class Menu(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=50, unique=True)
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='item')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child')
    lft = models.IntegerField(blank=True)
    rgt = models.IntegerField(blank=True)
    level = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['menu','lft']
    
    


