jinja2-pluralize-filter
=======================

Simple jinja2 filter to choose correct plural form for Russian language.

Installation

    pip install jinja2-pluralize-filter

You need to register filter on the template environment:

    from pluralize import pluralize
    environment.filters['pluralize'] = pluralize

or in Flask:
    
    from flask import current_app
    from pluralize import pluralize

    app.template_filter('pluralize')(pluralize)
    

Example of usage:

    {{ results_count|pluralize(['товар', 'товара', 'товаров']) }}