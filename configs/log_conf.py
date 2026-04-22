LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple_msg': {
            'format': '%(message)s'
        },
        'basic_format': {
            'format': '[%(asctime)s][%(filename)s][%(lineno)s][%(levelname)s][%(thread)d] - %(message)s'
        },
    },
    'handlers': {
        'file_handler': {
            'class': 'concurrent_log_handler.ConcurrentTimedRotatingFileHandler',
            'formatter': 'simple_msg',
            'level': 'DEBUG',
            'filename': 'logs/myapp.log',
            'when': 'D',                # 按天切割
            'interval': 1,              # 间隔一天
            'backupCount': 14,           # 保留7个文件
            'maxBytes': 200 * 1024 * 1024,  # 如果大小超过 200MB 也滚动
            'encoding': 'utf-8',
            'use_gzip': False,           # 或者 True，如果要压缩归档
        },
        'error_file_handler': {
            'class': 'concurrent_log_handler.ConcurrentTimedRotatingFileHandler',
            'formatter': 'basic_format',
            'level': 'ERROR',
            'filename': 'logs/error.log',
            'when': 'D',
            'interval': 1,
            'backupCount': 7,
            'maxBytes': 200 * 1024 * 1024,
            'encoding': 'utf-8',
            'use_gzip': False,
        },
    },
    'loggers': {
        'my.custom': {
            'handlers': ['file_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'my.custom.error': {
            'handlers': ['error_file_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
