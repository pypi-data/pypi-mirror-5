# coding=utf-8

RABBITMQ_CONFIG = {
    'queue_name': 'rabbitrpc',
    'exchange': '',

    'connection_settings': {
        'host': 'redis-01',
        'port': 5672,
        'virtual_host': '/',
        'username': 'guest',
        'password': 'guest',
    }
}
