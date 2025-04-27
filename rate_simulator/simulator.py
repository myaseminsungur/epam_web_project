import socket
import json
import random
import time
from datetime import datetime, timedelta
import atexit
import signal

class RateSimulator:
    def __init__(self, host='localhost', port=5002):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self._setup_socket()
        print(f"Rate Simulator initialized for {host}:{port}")
        # Register cleanup
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Initial rates (as of March 2024)
        self.base_rates = {
            ('USD', 'EUR'): 0.92,
            ('USD', 'GBP'): 0.79,
            ('USD', 'TRY'): 32.50,
            ('EUR', 'USD'): 1.09,
            ('EUR', 'GBP'): 0.86,
            ('EUR', 'TRY'): 35.33,
            ('GBP', 'USD'): 1.27,
            ('GBP', 'EUR'): 1.16,
            ('GBP', 'TRY'): 41.14,
            ('TRY', 'USD'): 0.031,
            ('TRY', 'EUR'): 0.028,
            ('TRY', 'GBP'): 0.024
        }

    def _setup_socket(self):
        """Setup the UDP socket"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception as e:
            print(f"Error setting up socket: {e}")
            if self.sock:
                self.sock.close()
            raise

    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        print("\nReceived termination signal. Cleaning up...")
        self.cleanup()
        exit(0)

    def generate_rate_change(self):
        """Generate a small random change in rate (-0.5% to +0.5%)"""
        return random.uniform(-0.005, 0.005)

    def update_rate(self, rate):
        """Apply a small change to the rate"""
        change = self.generate_rate_change()
        return rate * (1 + change)

    def send_update(self, base_currency, target_currency, rate):
        """Send rate update via UDP"""
        if not self.running:
            return

        update = {
            'base_currency': base_currency,
            'target_currency': target_currency,
            'rate': round(rate, 4),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        try:
            self.sock.sendto(
                json.dumps(update).encode('utf-8'),
                (self.host, self.port)
            )
            print(f"Sent update: {base_currency}/{target_currency} = {rate}")
        except Exception as e:
            if self.running:
                print(f"Error sending update: {e}")

    def run(self):
        """Run the simulator"""
        print("Starting rate simulator...")
        self.running = True
        try:
            while self.running:
                for (base, target), rate in self.base_rates.items():
                    if not self.running:
                        break
                    new_rate = self.update_rate(rate)
                    self.base_rates[(base, target)] = new_rate
                    self.send_update(base, target, new_rate)
                    time.sleep(20)  # Wait 2 seconds between updates
        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt. Cleaning up...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        print("Cleaning up Rate Simulator...")
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        print("Rate Simulator cleaned up")

if __name__ == '__main__':
    simulator = RateSimulator()
    simulator.run() 