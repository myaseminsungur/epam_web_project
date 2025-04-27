import socket
import json
import threading
from datetime import datetime
import atexit
import os
from django.apps import AppConfig

# Global listener instance
rate_listener = None

class RateUpdateListener:
    def __init__(self, host='0.0.0.0', port=5002):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        # Register cleanup
        atexit.register(self.cleanup)
        print(f"UDP Listener initialized for {host}:{port}")

    def _setup_socket(self):
        """Setup the UDP socket"""
        try:
            if self.sock is None:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind((self.host, self.port))
        except Exception as e:
            print(f"Error setting up socket: {e}")
            if self.sock:
                self.sock.close()
                self.sock = None
            raise

    def start(self):
        """Start listening for rate updates in a separate thread"""
        if not self.running and self.sock is None:
            try:
                self._setup_socket()
                self.running = True
                thread = threading.Thread(target=self._listen)
                thread.daemon = True
                thread.start()
                print("UDP Listener started")
            except Exception as e:
                print(f"Failed to start listener: {e}")
                self.cleanup()

    def _listen(self):
        """Listen for incoming rate updates"""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                self._handle_update(data)
            except Exception as e:
                if self.running:  # Only print error if we're still running
                    print(f"Error receiving data: {e}")

    def _handle_update(self, data):
        """Handle incoming rate update"""
        try:
            from .models import Currency, ExchangeRate
            update = json.loads(data.decode('utf-8'))
            base_currency, _ = Currency.objects.get_or_create(
                code=update['base_currency'],
                defaults={'name': f"{update['base_currency']} Currency"}
            )
            target_currency, _ = Currency.objects.get_or_create(
                code=update['target_currency'],
                defaults={'name': f"{update['target_currency']} Currency"}
            )
            
            ExchangeRate.objects.update_or_create(
                base_currency=base_currency,
                target_currency=target_currency,
                date=update['date'],
                defaults={'rate': update['rate']}
            )
            print(f"Updated rate: {update['base_currency']}/{update['target_currency']} = {update['rate']}")
            
        except Exception as e:
            print(f"Error processing update: {e}")

    def cleanup(self):
        """Cleanup resources"""
        print("Cleaning up UDP Listener...")
        self.running = False
        if self.sock:
            try:
                self.sock.close()
                self.sock = None
            except:
                pass
        print("UDP Listener cleaned up")

def get_listener():
    """
    Get singleton listener instance, creating it if necessary
    """
    global rate_listener
    if rate_listener is None:
        rate_listener = RateUpdateListener()
    return rate_listener 