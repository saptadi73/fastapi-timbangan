import serial
import sys
import time
import json
import signal
import threading
from datetime import datetime
from typing import Optional, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class ScaleConnection:
    """
    Koneksi ke timbangan SGW-3015P via serial port
    """
    
    def __init__(
        self,
        port: str = "COM3",
        baudrate: int = 2400,
        bytesize: int = 8,
        stopbits: int = 1,
        parity: str = "N",
        reconnect_ms: int = 3000,
        poll_ms: int = 1000,
        enable_poll: bool = True,
    ):
        self.base_config = {
            "port": port,
            "baudrate": baudrate,
            "bytesize": bytesize,
            "stopbits": stopbits,
            "parity": parity.upper(),
        }
        
        self.reconnect_ms = reconnect_ms
        self.poll_ms = poll_ms
        self.enable_poll = enable_poll
        self.poll_commands = [b"\r", b"\n", b"SI\r\n", b"S\r\n"]
        
        self.ser = None
        self.packet_count = 0
        self.active_config = None
        self.rx_buffer = ""
        self.is_shutting_down = False
        self.is_connected = False
        self.last_reading: Optional[Dict[str, Any]] = None
        self.connection_thread = None
        
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)


        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)
    
    # =========================
    # Helpers
    # =========================
    
    @staticmethod
    def normalize_serial_chunk(chunk: bytes) -> str:
        """Normalize serial chunk - clear non-ASCII bits"""
        return bytes([b & 0x7F for b in chunk]).decode("ascii", errors="ignore")
    
    @staticmethod
    def parse_scale_line(line: str) -> Optional[Dict[str, Any]]:
        """Parse timbangan reading from serial line"""
        cleaned = line.strip()
        
        # Strict format: ST/US, NT/GS, value, unit (e.g., "ST,NT,1234.56kg")
        strict = re.match(
            r"^([A-Z]{2}),([A-Z]{2}),([+-]?\d+(?:\.\d+)?)\.?(kg|Kg|KG|g|G|lb|LB)$",
            cleaned
        )
        if strict:
            stability, mode, value_raw, unit_raw = strict.groups()
            value = float(value_raw)
            return {
                "raw": cleaned,
                "stability": stability,
                "mode": mode,
                "value": value,
                "unit": unit_raw.lower(),
                "stable": stability == "ST"
            }
        
        # Lenient parsing - extract numbers and units
        ascii_only = re.sub(r"[^A-Za-z0-9+.\-]", "", cleaned)
        value_match = re.search(r"([+-]?\d+(?:\.\d+)?)", ascii_only)
        if not value_match:
            return None
        
        value = float(value_match.group(1))
        upper = ascii_only.upper()
        
        stability = "ST" if "ST" in upper else ("US" if "US" in upper else None)
        mode = "NT" if "NT" in upper else ("GS" if "GS" in upper else None)
        
        if "KG" in upper:
            unit = "kg"
        elif "LB" in upper:
            unit = "lb"
        elif "G" in upper:
            unit = "g"
        else:
            unit = "kg"
        
        return {
            "raw": cleaned,
            "stability": stability,
            "mode": mode,
            "value": value,
            "unit": unit,
            "stable": stability == "ST"
        }
    
    @staticmethod
    def build_candidates(base: Dict[str, Any]) -> list:
        """Build list of serial config candidates to try"""
        candidates = [
            base,
            {**base, "baudrate": 2400, "bytesize": 8, "parity": "N", "stopbits": 1},
            {**base, "baudrate": 2400, "bytesize": 7, "parity": "E", "stopbits": 1},
            {**base, "baudrate": 9600, "bytesize": 8, "parity": "N", "stopbits": 1},
            {**base, "baudrate": 4800, "bytesize": 8, "parity": "N", "stopbits": 1},
            {**base, "baudrate": 1200, "bytesize": 7, "parity": "E", "stopbits": 1},
        ]
        
        seen = set()
        unique = []
        
        for c in candidates:
            key = (c["baudrate"], c["bytesize"], c["parity"], c["stopbits"])
            if key not in seen:
                seen.add(key)
                unique.append(c)
        
        return unique
    
    # =========================
    # Polling Thread
    # =========================
    
    def _poll_loop(self):
        """Send polling commands periodically"""
        index = 0
        while not self.is_shutting_down and self.ser and self.ser.is_open:
            cmd = self.poll_commands[index % len(self.poll_commands)]
            index += 1
            try:
                self.ser.write(cmd)
                logger.debug(f"Sent poll command {index % len(self.poll_commands)}")
            except Exception as e:
                logger.error(f"Poll error: {e}")
                break
            time.sleep(self.poll_ms / 1000)
    
    # =========================
    # Connection Logic
    # =========================
    
    def _try_connect(self) -> bool:
        """Try connecting with different configurations"""
        candidates = self.build_candidates(self.base_config)
        
        for cfg in candidates:
            try:
                logger.info(f"Connecting to {cfg['port']} @ {cfg['baudrate']} baud...")
                self.ser = serial.Serial(
                    port=cfg["port"],
                    baudrate=cfg["baudrate"],
                    bytesize=cfg["bytesize"],
                    stopbits=cfg["stopbits"],
                    parity=cfg["parity"],
                    timeout=1
                )
                self.active_config = cfg
                self.is_connected = True
                logger.info(f"✓ Connected: {cfg['port']} @ {cfg['baudrate']} baud")
                return True
            except Exception as e:
                logger.debug(f"Failed to connect with {cfg}: {e}")
        
        self.is_connected = False
        return False
    
    def _read_loop(self):
        """Read and parse serial data"""
        while self.ser and self.ser.is_open and not self.is_shutting_down:
            try:
                chunk = self.ser.read(1024)
                if not chunk:
                    continue
                
                self.rx_buffer += self.normalize_serial_chunk(chunk)
                parts = self.rx_buffer.splitlines(keepends=False)
                
                if not self.rx_buffer.endswith("\n"):
                    self.rx_buffer = parts.pop() if parts else ""
                
                for line in parts:
                    if not line.strip():
                        continue
                    
                    self.packet_count += 1
                    parsed = self.parse_scale_line(line)
                    
                    if not parsed:
                        logger.debug(f"Unparsed line: {line.strip()}")
                        continue
                    
                    # Update last reading
                    self.last_reading = {
                        "ts": datetime.utcnow().isoformat(),
                        "type": "weight",
                        "packet": self.packet_count,
                        "stability": parsed["stability"],
                        "mode": parsed["mode"],
                        "stable": parsed["stable"],
                        "weight": parsed["value"],
                        "unit": parsed["unit"],
                        "raw": parsed["raw"]
                    }
                    logger.debug(f"Reading: {self.last_reading}")
            
            except Exception as e:
                logger.error(f"Read error: {e}")
                self.is_connected = False
                break
    
    def _connect_loop(self):
        """Main connection loop - reconnect automatically"""
        while not self.is_shutting_down:
            if self._try_connect():
                if self.enable_poll:
                    poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
                    poll_thread.start()
                self._read_loop()
            
            if not self.is_shutting_down:
                logger.info(f"Reconnect in {self.reconnect_ms}ms...")
                time.sleep(self.reconnect_ms / 1000)
    
    def _shutdown(self, sig=None, frame=None):
        """Shutdown handler"""
        logger.info("Shutting down...")
        self.is_shutting_down = True
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.is_connected = False
    
    # =========================
    # Public Interface
    # =========================
    
    def start(self):
        """Start connection in background thread"""
        if self.connection_thread is None or not self.connection_thread.is_alive():
            self.connection_thread = threading.Thread(
                target=self._connect_loop,
                daemon=True
            )
            self.connection_thread.start()
            logger.info("Scale connection thread started")
    
    def stop(self):
        """Stop connection"""
        self._shutdown()
        if self.connection_thread:
            self.connection_thread.join(timeout=5)
    
    def get_last_reading(self) -> Optional[Dict[str, Any]]:
        """Get last weight reading"""
        return self.last_reading
    
    def get_status(self) -> Dict[str, Any]:
        """Get connection status"""
        return {
            "connected": self.is_connected,
            "port": self.base_config.get("port"),
            "baudrate": self.base_config.get("baudrate"),
            "active_config": self.active_config,
            "packet_count": self.packet_count,
            "last_reading": self.last_reading
        }
    
    def get_available_ports(self) -> list:
        """List available serial ports"""
        ports = []
        try:
            import serial.tools.list_ports
            for port, desc, hwid in serial.tools.list_ports.comports():
                ports.append({
                    "port": port,
                    "description": desc,
                    "hwid": hwid
                })
        except Exception as e:
            logger.error(f"Error listing ports: {e}")
        return ports


# =========================
# Global Instance
# =========================

_scale_connection: Optional[ScaleConnection] = None


def get_scale_connection() -> ScaleConnection:
    """Get or create global scale connection instance"""
    global _scale_connection
    if _scale_connection is None:
        from config import settings
        
        _scale_connection = ScaleConnection(
            port=getattr(settings, 'scale_port', 'COM3'),
            baudrate=getattr(settings, 'scale_baudrate', 2400),
            bytesize=getattr(settings, 'scale_bytesize', 8),
            stopbits=getattr(settings, 'scale_stopbits', 1),
            parity=getattr(settings, 'scale_parity', 'N'),
            reconnect_ms=getattr(settings, 'scale_reconnect_ms', 3000),
            poll_ms=getattr(settings, 'scale_poll_ms', 1000),
            enable_poll=getattr(settings, 'scale_enable_poll', True),
        )
    return _scale_connection
