from django import template
from menu_app.models import MenuItem
from django.http import Http404

register = template.Library()


@register.simple_tag
def inc(value):
  return value + 1

@register.filter
def repeat(value, arg):
    """Используется для отрисовки отступов"""
    return value * int(arg)

@register.inclusion_tag("menu_app/show_top_menu.html")
def show_top_menu(menu):
    """Используется для отрисовки корневой ноды и первого уровня потомков для каждого меню"""
    root_node = menu.item.all().order_by('lft').first()
    # если меню создано, но там пока пусто, то не выводим ничего
    if not root_node:
       return
    children = root_node.child.all()
    return {"menu": menu, "root_node": root_node, "children": children}

@register.inclusion_tag("menu_app/draw_menu.html")
def draw_menu(menu_name):
    """
    Отрисовка меню по его названию. Реализуется в 1 sql-запрос, который получает все ноды, привязанные к данному меню.
    Для того, чтобы при получении parent'а у потомка первого уровня (то есть при получении корневой ноды) 
    не происходило повторного sql-запроса, сделан select_related. Корень извлекается именно так, потому что иначе
    (при получении корня через nodes[0]) порождается дополнительный запрос. 
    """
    nodes = MenuItem.objects.filter(menu__name = menu_name).select_related("parent").order_by('lft')
    if not nodes:
        raise Http404
    children = nodes[1:]
    
    root_found = False
    # считаем отступы
    stack = []
    for child in children:
        if not root_found:
            root_node = child.parent
            root_found = True
        elif stack:
            while(stack and child.rgt > stack[len(stack)-1]):
                stack.pop()
        
        stack.append(child.rgt)
        child.level = len(stack)

    return {"menu_name": menu_name, "root_node": root_node, "children": children}

