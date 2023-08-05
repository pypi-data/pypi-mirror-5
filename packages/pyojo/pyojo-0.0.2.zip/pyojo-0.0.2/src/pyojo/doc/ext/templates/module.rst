``{{ fullname }}``
===============================================================

.. automodule:: {{ fullname }}

{% block classes %}
{% if classes %}

.. rubric:: Classes

.. autosummary::
   :nosignatures:
   :toctree: {{ objname  }}/
   :template: class.rst

{% for item in classes %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

{% block functions %}
{% if functions %}


.. rubric:: Functions
   
.. autosummary::
   :toctree: {{ objname  }}/
   :template: function.rst

{% for item in functions %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}


{% block submodules %}
{% if submodules %}

.. rubric:: Modules

.. autosummary::
   :toctree: {{ objname  }}/
   :template: module.rst

{% for item in submodules %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}


{% block constants %}
{% if constants %}

.. rubric:: Defined

{% for item in constants %}
* {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}


.. template module.rst


