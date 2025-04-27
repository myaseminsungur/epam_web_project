from django.apps import AppConfig
import sys


class CurrencyConverterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'currency_converter'

    def ready(self):
        # Prevent auto-reloader from starting multiple instances
        if 'runserver' in sys.argv:
            # Only start in main process, not in the reloader
            if not any(arg.startswith('--noreload') for arg in sys.argv):
                import os
                if os.environ.get('RUN_MAIN') == 'true':
                    # Import here to avoid circular import
                    from .udp_listener import get_listener
                    listener = get_listener()
                    listener.start()
