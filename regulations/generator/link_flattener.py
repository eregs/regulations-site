import re

# <a> followed by another <a> without any intervening </a>s
link_inside_link_regex = re.compile(
    ur"(?P<outer_link><a ((?!</a>).)*)(<a ((?!</a>).)*>"
    ur"(?P<internal_content>((?!</a>).)*)</a>)",
    re.IGNORECASE | re.DOTALL)


def flatten_links(text):
    """
    Fix <a> elements that have embedded <a> elements by
    replacing the internal <a> element with its content.
    Assumes that the text does not span multiple lines and that
    the <a> tags are lowercase.
    """

    while True:
        text, sub_count = link_inside_link_regex.subn(
            ur"\g<outer_link>\g<internal_content>", text)
        if sub_count == 0:
            return text # Return only when no more subs possible
