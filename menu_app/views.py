from django.shortcuts import render, get_object_or_404
from .models import MenuItem, Menu


def index(request):
    """
    Отображение главной страницы: передаются все существующие меню, для каждого из которых вызывается show_top_menu,
    который показывает корневую ноду и первый уровень потомков.
    """
    menus = Menu.objects.all()
    return render(request, 'menu_app/index.html', {"menus": menus})

def show_menu(request, menu_name):
    """
    Отображение меню по названию. Для отображения используется кастомный тэг {% draw_menu menu_name %}.
    На отображение всего меню требуется 1 sql-запрос.
    """
    return render(request, 'menu_app/show_menu.html', {"menu_name": menu_name})

def show_current(request, item_id):
    """
    Отображение текущего пункта меню. 
    Для пункта меню определяются parents (не только родительская нода, связанная по FK, а все ноды, лежащие выше по иерархии) и 
    children (все ноды, лежащие ниже по иерархии. В шаблоне отображается только первый уровень потомков - условие {% if child.level < 2 %}).
    Определение parents и children осуществляется с помощью left- и right-values (Modified Preorder Tree Traversal).    
    """
    menu_item = get_object_or_404(MenuItem.objects.select_related("menu"), id=item_id)
    all_nodes = MenuItem.objects.filter(menu=menu_item.menu)
    parents, children  = [], []
    for node in all_nodes:
        if node.lft < menu_item.lft and node.rgt > menu_item.rgt:
            parents.append(node)
        elif node.lft > menu_item.lft and node.rgt < menu_item.rgt:
            children.append(node)
    # считаем отступы
    stack = []
    for child in children:
        if stack:
            while(stack and child.rgt > stack[len(stack)-1]):
                stack.pop()
        
        stack.append(child.rgt)
        child.level = len(stack)

    context = {"menu_item": menu_item, "parents": parents, "children": children, "indent": 0}
    return render(request, 'menu_app/show_current.html', context)
