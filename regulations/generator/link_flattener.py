import re

# <a> followed by another <a> without any intervening </a>s
# outer_link - partial outer element up to the inner link
# inner_content - content of the inner_link
link_inside_link_regex = re.compile(
    r"(?P<outer_link><a ((?!</a>).)*)<a .*?>(?P<inner_content>.*?)</a>",
    re.IGNORECASE | re.DOTALL)


def flatten_links(text):
    """
    Fix <a> elements that have embedded <a> elements by
    replacing the internal <a> element with its content.
    """

    while True:
        text, sub_count = link_inside_link_regex.subn(
            r"\g<outer_link>\g<inner_content>", text)
        if sub_count == 0:
            return text
