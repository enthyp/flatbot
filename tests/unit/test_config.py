def test_config_full(config):
    conf = config('config_full.yml')
    assert conf.host == '0.0.0.0' and conf.port == '8080'

def test_config_empty(config):
    conf = config('config_empty.yml')
    assert conf.host == '0.0.0.0' and conf.port == '84443'

def test_config_default(config):
    conf = config()
    assert conf.host == '0.0.0.0' and conf.port == '84443'
