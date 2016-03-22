{% spaceless %}
{% for section in sections %}
# {{section.id}}
{{section.comment}}
{% if section.files %}
## Attachments
{% for file in section.files %}
* {{file.name}}
{% endfor %}
{% endif %}
{% endfor %}
{% endspaceless %}
