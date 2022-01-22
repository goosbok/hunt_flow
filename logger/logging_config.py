import logging

from const import LOG_FILE


class FunctionFilter(logging.Filter):
    def filter(self, record):
        functions_names = [
            'push_data',
            'run',
        ]

        if not functions_names:
            return True

        return record.funcName in functions_names


config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(name)s - %(module)s:%(funcName)s:%(lineno)s - %(message)s',
        },
    },
    'handlers': {
        'console_log': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filters': ['function_filter'],
        },
        'file_log': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': f'logs/{LOG_FILE}',
        }
    },
    'loggers': {
        'app_logger': {
            'level': 'DEBUG',
            'handlers': ['console_log', 'file_log'],
            'propagate': False,
        },
    },

    'filters': {
        'function_filter': {
            '()': FunctionFilter,
        },
    },
}