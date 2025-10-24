# Code Citations

## License: unknown
https://github.com/SteinOveHelset/lynko/blob/8488f2bd5276a6b91b82b933b49b38d9c167b77f/link/views.py

```
@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
```


## License: unknown
https://github.com/NataliaSalamanca94/SalamancaNatalia47765/blob/0ab66f6852aca443fef66eae7f898be259063072/tublog/Templates/category/category_form.html

```
% endblock %}
{% block content %}
    <h2>Create Category</h2>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Create</button>
    </form>
    <a href=
```


## License: unknown
https://github.com/NerdPlayground/fcccustomforum/blob/3c0dcde09b455800ffd9486236c1dcc87bba6289/categories/templates/categories/create_category.html

```
% endblock %}
{% block content %}
    <h2>Create Category</h2>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Create</button>
    </form>
    <a href=
```


## License: unknown
https://github.com/tuan-bug/PYTHON/blob/26ab124d197d95b0346b760818dd13995d34f2cb/webapp/app/templates/admin/deleteCategory.html

```
Delete Category</h2>
    <p>Are you sure you want to delete the category "{{ category.name }}"?</p>
    <form method="post">
        {% csrf_token %}
        <button type="submit">Delete</button>
    </form>
    <a href="{% url 'dashboard' %}">Cancel</a
```


## License: Apache-2.0
https://github.com/kasareswapnil09/Nasya-Crud-operation/blob/6093d5ab6df729e9298bc1606cbd8a8eefbda092/delete_statistic.html

```
Delete Category</h2>
    <p>Are you sure you want to delete the category "{{ category.name }}"?</p>
    <form method="post">
        {% csrf_token %}
        <button type="submit">Delete</button>
    </form>
    <a href="{% url 'dashboard' %}">Cancel</a
```

