# Code Citations

## License: unknown
https://github.com/limbertlopezl/ClasificacionInventarioABC/blob/34395a41086dcb98d7005c7c76862034b9344dcd/src/gaspar/templates/forms/form.html

```
/h1>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        {% for field in form %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {% render_field field class+="form-control" %}
                {% if field.help_text %}
                    <small class="form-text text-muted">{{ field.help_text }}</small>
                {% endif %}
                {% for error in field.errors %}
                    <div class="invalid-feedback">{{ error }}</div>
                {% endfor %}
            </div>
        {% endfor %}
        
        <button type="submit" class
```


## License: unknown
https://github.com/lixiaopu/OnlineGameStore/blob/94eea94a5e28d7868daa4a3e8472ec299ff54db1/game/templates/game/edit.html

```
/h1>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        {% for field in form %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {% render_field field class+="form-control" %}
                {% if field.help_text %}
                    <small class="form-text text-muted">{{ field.help_text }}</small>
                {% endif %}
                {% for error in field.errors %}
                    <div class="invalid-feedback">{{ error }}</div>
                {% endfor %}
            </div>
        {% endfor %}
        
        <button type="submit" class
```


## License: unknown
https://github.com/raviRB/Django-Blog/blob/9fec84998ddd0f89d4c9c57652a5361a21056238/templates/setting.html

```
/h1>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        {% for field in form %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {% render_field field class+="form-control" %}
                {% if field.help_text %}
                    <small class="form-text text-muted">{{ field.help_text }}</small>
                {% endif %}
                {% for error in field.errors %}
                    <div class="invalid-feedback">{{ error }}</div>
                {% endfor %}
            </div>
        {% endfor %}
        
        <button type="submit" class
```


## License: unknown
https://github.com/AmarjotSingh21/DjangoBlog/blob/5649e7472cf57253a96de09fee23972aea3ca6b2/templates/user/profile_update.html

```
/h1>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        {% for field in form %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {% render_field field class+="form-control" %}
                {% if field.help_text %}
                    <small class="form-text text-muted">{{ field.help_text }}</small>
                {% endif %}
                {% for error in field.errors %}
                    <div class="invalid-feedback">{{ error }}</div>
                {% endfor %}
            </div>
        {% endfor %}
        
        <button type="submit" class
```


## License: unknown
https://github.com/ziho/bcr/blob/75b423f10fc8944640e6d8c5c35e5690548f4b1d/templates/Admin_CheckApplication_edit.html

```
/h1>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        {% for field in form %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {% render_field field class+="form-control" %}
                {% if field.help_text %}
                    <small class="form-text text-muted">{{ field.help_text }}</small>
                {% endif %}
                {% for error in field.errors %}
                    <div class="invalid-feedback">{{ error }}</div>
                {% endfor %}
            </div>
        {% endfor %}
        
        <button type="submit" class
```


## License: unknown
https://github.com/HE-Arc/PollsArc/blob/d0623983bc40a8921c622547d0484558426b390c/pollsarcapp/templates/registration/register.html

```
/h1>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        {% for field in form %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {% render_field field class+="form-control" %}
                {% if field.help_text %}
                    <small class="form-text text-muted">{{ field.help_text }}</small>
                {% endif %}
                {% for error in field.errors %}
                    <div class="invalid-feedback">{{ error }}</div>
                {% endfor %}
            </div>
        {% endfor %}
        
        <button type="submit" class
```


## License: unknown
https://github.com/Vix-Nguyen/pc-shop/blob/a1bbb0ae98e7a34f206cd28c72027d4c6607f9f8/app/myshop/templates/myshop/product_form.html

```
/h1>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        {% for field in form %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {% render_field field class+="form-control" %}
                {% if field.help_text %}
                    <small class="form-text text-muted">{{ field.help_text }}</small>
                {% endif %}
                {% for error in field.errors %}
                    <div class="invalid-feedback">{{ error }}</div>
                {% endfor %}
            </div>
        {% endfor %}
        
        <button type="submit" class
```


## License: unknown
https://github.com/masabagerald/circumcision_project/blob/932ba6e0b21298801164152f64a8399dd691d6a7/circumcision/templates/clients/edit_medical_history.html

```
/h1>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        {% for field in form %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {% render_field field class+="form-control" %}
                {% if field.help_text %}
                    <small class="form-text text-muted">{{ field.help_text }}</small>
                {% endif %}
                {% for error in field.errors %}
                    <div class="invalid-feedback">{{ error }}</div>
                {% endfor %}
            </div>
        {% endfor %}
        
        <button type="submit" class
```

