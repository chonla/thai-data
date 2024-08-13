from builder.build import parse_options


def test_default_options():
    options = []

    result = parse_options(options)

    assert result == {"check": False, "prod": False, "log": "info"}


def test_prod_options():
    options = ["-prod"]

    result = parse_options(options)

    assert result == {"check": False, "prod": True, "log": "info"}


def test_check_options():
    options = ["-check"]

    result = parse_options(options)

    assert result == {"check": True, "prod": False, "log": "info"}


def test_info_options():
    options = ["-log=info"]

    result = parse_options(options)

    assert result == {"check": False, "prod": False, "log": "info"}


def test_debug_options():
    options = ["-log=debug"]

    result = parse_options(options)

    assert result == {"check": False, "prod": False, "log": "debug"}


def test_error_options():
    options = ["-log=error"]

    result = parse_options(options)

    assert result == {"check": False, "prod": False, "log": "error"}


def test_prod_debug_options():
    options = ["-prod", "-log=debug"]

    result = parse_options(options)

    assert result == {"check": False, "prod": True, "log": "debug"}


def test_debug_prod_options():
    options = ["-log=debug", "-prod"]

    result = parse_options(options)

    assert result == {"check": False, "prod": True, "log": "debug"}


def test_check_debug_options():
    options = ["-check", "-log=debug"]

    result = parse_options(options)

    assert result == {"check": True, "prod": False, "log": "debug"}


def test_debug_check_options():
    options = ["-log=debug", "-check"]

    result = parse_options(options)

    assert result == {"check": True, "prod": False, "log": "debug"}


def test_prod_check_options():
    options = ["-prod", "-check"]

    result = parse_options(options)

    assert result == {"check": True, "prod": True, "log": "info"}


def test_check_prod_options():
    options = ["-check", "-prod"]

    result = parse_options(options)

    assert result == {"check": True, "prod": True, "log": "info"}


def test_check_prod_debug_options():
    options = ["-check", "-prod", "-log=debug"]

    result = parse_options(options)

    assert result == {"check": True, "prod": True, "log": "debug"}
