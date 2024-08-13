from builder.build import parse_options


def test_default_options():
    options = []

    result = parse_options(options)

    assert result == {"prod": False, "log": "info"}


def test_prod_options():
    options = ["-prod"]

    result = parse_options(options)

    assert result == {"prod": True, "log": "info"}


def test_info_options():
    options = ["-log=info"]

    result = parse_options(options)

    assert result == {"prod": False, "log": "info"}


def test_debug_options():
    options = ["-log=debug"]

    result = parse_options(options)

    assert result == {"prod": False, "log": "debug"}


def test_error_options():
    options = ["-log=error"]

    result = parse_options(options)

    assert result == {"prod": False, "log": "error"}


def test_prod_debug_options():
    options = ["-prod", "-log=debug"]

    result = parse_options(options)

    assert result == {"prod": True, "log": "debug"}


def test_debug_prod_options():
    options = ["-log=debug", "-prod"]

    result = parse_options(options)

    assert result == {"prod": True, "log": "debug"}
