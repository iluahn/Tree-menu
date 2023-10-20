from django.core.exceptions import ValidationError
from django.contrib import admin
from .models import MenuItem, Menu
from django import forms
from django.contrib import messages

class MenuItemAdmin(admin.ModelAdmin):
    fields = ('menu', 'name', 'parent')
    list_display = ('name', 'parent', 'lft', 'rgt', 'menu')
    
    def change_lftrgt_adding(self, obj, nodes):
        """Переназначение left- и right-values при добавлении новой ноды"""
        was_changed = False
        for node in nodes:
            if(node.lft > obj.lft - 1):
                node.lft += 2
                was_changed = True
            if(node.rgt > obj.lft - 1):
                node.rgt += 2
                was_changed = True
            if was_changed:
                node.save()
                was_changed = False


    def change_lftrgt_deletion(self, obj, nodes):
        """Переназначение left- и right-values при удалении ноды"""
        was_changed = False
        for node in nodes:
            if(node.lft > obj.rgt):
                node.lft -= 2
                was_changed = True
            if(node.rgt > obj.rgt):
                node.rgt -= 2
                was_changed = True
            if was_changed:
                node.save()
                was_changed = False


    def save_model(self, request, obj, form, change):
        """
        Переопределение метода сохранения записей модели MenuItem в админке, чтобы каждой новой 
        записи были присвоены правильные left- и right-values (Modified Preorder Tree Traversal).
        """
        # если не создаем, а изменяем ноду
        if(obj.id is not None):
            existing_obj = MenuItem.objects.get(id=obj.id)
            if obj.menu != existing_obj.menu:
                messages.set_level(request, messages.ERROR)
                messages.error(request, "Error: menu change is not available")
                return
            if obj.parent != existing_obj.parent:
                messages.set_level(request, messages.ERROR)
                messages.error(request, "Parent error: parent change has not yet been implemented")
                return
            super().save_model(request, obj, form, change)
            return
        
        nodes = MenuItem.objects.filter(menu=obj.menu.id).order_by('lft')
        # если корень (дерево пустое)
        if not nodes:
            obj.lft = 1
            obj.rgt = 2
            # проверка на то, чтобы корню не был назначен родитель (родитель должен быть пустым для корня)
            if obj.parent:
                messages.set_level(request, messages.ERROR)
                messages.error(request, "Parent error: first item in empty menu can't have parents!")
                return
        else:
            parent = obj.parent
            # проверка на то, что мы не пытаемся создать еще одну корневую ноду
            if not parent:
                messages.set_level(request, messages.ERROR)
                messages.error(request, "Parent error: root node already exists in this menu!")
                return
            # проверка на то, что мы не пытаемся сделать родителем ноду из другого меню
            if parent not in nodes:
                messages.set_level(request, messages.ERROR)
                messages.error(request, "Parent error: parent should be from the same menu!")
                return
            # если вставляемая нода является первым потомком
            if not parent.child.all():
                obj.lft = parent.rgt
                obj.rgt = obj.lft + 1
                self.change_lftrgt_adding(obj, nodes)
            # если уже есть потомки, то lft вставляемой должны быть равно самое большое rgt из потомков + 1
            else:
                # сортируем потомков по rgt по убыванию и берем самое большое rgt из потомков + 1
                obj.lft = parent.child.order_by('-rgt').first().rgt + 1
                obj.rgt = obj.lft + 1
                self.change_lftrgt_adding(obj, nodes)
        super().save_model(request, obj, form, change)


    def delete_model(self, request, obj):
        """
        Переопределение метода удаления записей модели MenuItem в админке, чтобы при удалении
        записи были переназначены left- и right-values (Modified Preorder Tree Traversal).
        """
        children = obj.child.all()
        if children:
            for child in children:
                self.delete_model(request, child)
        #обновляем стейт объекта
        obj = MenuItem.objects.get(id=obj.id)

        nodes = MenuItem.objects.filter(menu=obj.menu.id).order_by('lft')
        self.change_lftrgt_deletion(obj, nodes)

        super().delete_model(request, obj)


    def delete_queryset(self, request, queryset):
        """
        Переопределение метода удаления кверисетов MenuItem в админке, чтобы при удалении
        были переназначены left- и right-values (Modified Preorder Tree Traversal).
        """
        # после такой сортировки будем удалять сначала дочерние элементы
        queryset = queryset.order_by('-lft')
        for item in queryset:
            self.delete_model(request, item)



admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Menu)