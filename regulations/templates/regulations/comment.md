{% for section in sections %}
# {{section.label}}
{{section.comment}}
{% if section.files %}
## Attachments
{% for file in section.files %}
* {{file.name}}
{% endfor %}
{% endif %}
{% if not forloop.last %}
---
{% endif %}
{% endfor %}
