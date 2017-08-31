from mock import Mock

from regulations.generator.sidebar import print_part


def test_print_part(monkeypatch):
    monkeypatch.setattr(print_part, 'regulation_meta', Mock())
    print_part.regulation_meta.return_value = {'cfr_title_number': 12}

    sidebar = print_part.PrintPart('333-44', 'vvvv')
    assert sidebar.context(Mock(), Mock()) == {
        'cfr_title': 12,
        'cfr_part': '333',
        'version': 'vvvv',
    }
