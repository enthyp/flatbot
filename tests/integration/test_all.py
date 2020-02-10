from flatbot.__main__ import main


def test(config_path):
    main(config_path('config.yml'))
