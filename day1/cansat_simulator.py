#!/usr/bin/env python3
"""
CanSat flight telemetry simulator.

Streams synthetic telemetry (1 Hz) over a TCP socket or an optional serial
port, emulating launch, ascent, apogee, descent, and landing phases. See the
accompanying README for the data format and usage instructions.
"""

import sys
import time
import math
import random
import socket
import select
import argparse

# Telemetry Configuration
TEAM_ID = "1064"
BASE_LAT = -7.275764
BASE_LON = 112.794317

CSV_HEADER = (
    "TEAM_ID,MISSION_TIME,PACKET_COUNT,ALTITUDE,PRESSURE,TEMPERATURE,"
    "VOLTAGE,ROLL,PITCH,YAW,GPS_LAT,GPS_LON,GPS_ALT,STATE\r\n"
)


class FlightProfile:
    """Calculates realistic flight telemetry based on elapsed mission seconds."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.start_time = time.time()
        self.packet_count = 0

    def step(self):
        self.packet_count += 1
        elapsed = time.time() - self.start_time

        # Flight phase timeline (seconds within one cycle):
        # 0-10 LAUNCH_PAD | 11-40 ASCENT (~700 m) | 41-50 APOGEE
        # 51-90 DESCENT | >90 LANDED
        cycle_time = elapsed % 110.0  # auto-recycle the flight every 110 s

        if cycle_time <= 10.0:
            state = "LAUNCH_PAD"
            alt = random.uniform(0.0, 0.4)
            roll = random.uniform(-0.5, 0.5)
            pitch = random.uniform(-0.5, 0.5)
            yaw = 0.0

        elif cycle_time <= 40.0:
            state = "ASCENT"
            progress = (cycle_time - 10.0) / 30.0  # 0.0 -> 1.0
            # Smooth ascent curve
            alt = 700.0 * math.sin(progress * (math.pi / 2.0))
            alt += random.uniform(-1.5, 1.5)
            roll = random.uniform(-15.0, 15.0)
            pitch = random.uniform(5.0, 20.0)
            yaw = (cycle_time * 12.0) % 360.0

        elif cycle_time <= 50.0:
            state = "APOGEE"
            alt = 700.0 + random.uniform(-1.0, 1.0)
            roll = random.uniform(-25.0, 25.0)
            pitch = random.uniform(-10.0, 10.0)
            yaw = (cycle_time * 8.0) % 360.0

        elif cycle_time <= 90.0:
            state = "DESCENT"
            progress = (cycle_time - 50.0) / 40.0  # 0.0 -> 1.0
            # Steady parachute descent: 700m -> 0m (~17.5 m/s)
            alt = 700.0 * (1.0 - progress)
            alt = max(0.5, alt + random.uniform(-1.0, 1.0))
            roll = random.uniform(-8.0, 8.0)
            pitch = random.uniform(-5.0, 5.0)
            yaw = (cycle_time * 4.0) % 360.0

        else:
            state = "LANDED"
            alt = 0.0
            roll = random.uniform(-1.0, 1.0)
            pitch = random.uniform(-1.0, 1.0)
            yaw = 180.0

        # Secondary sensor readings
        # Barometric pressure: P = P0 * (1 - alt/44330)^5.255
        pressure = 1013.25 * math.pow(1.0 - (max(0.0, alt) / 44330.0), 5.255)
        pressure = round(pressure + random.uniform(-0.2, 0.2), 1)

        temp = round(28.5 - (alt * 0.0065) + random.uniform(-0.3, 0.3), 1)
        voltage = round(4.20 - (min(elapsed, 110.0) * 0.002) + random.uniform(-0.02, 0.02), 2)

        # GPS Drift Simulation
        drift_factor = min(cycle_time / 90.0, 1.0) * 0.0015
        gps_lat = round(BASE_LAT + (drift_factor * 0.7) + random.uniform(-0.00002, 0.00002), 6)
        gps_lon = round(BASE_LON + (drift_factor * 0.4) + random.uniform(-0.00002, 0.00002), 6)
        gps_alt = round(max(0.0, alt) + random.uniform(-2.0, 2.0), 1)

        # Mission Time (HH:MM:SS)
        total_sec = int(elapsed)
        hh = total_sec // 3600
        mm = (total_sec % 3600) // 60
        ss = total_sec % 60
        mission_time = f"{hh:02d}:{mm:02d}:{ss:02d}"

        telemetry_line = (
            f"{TEAM_ID},{mission_time},{self.packet_count},{alt:.1f},{pressure:.1f},"
            f"{temp:.1f},{voltage:.2f},{roll:.1f},{pitch:.1f},{yaw:.1f},"
            f"{gps_lat:.6f},{gps_lon:.6f},{gps_alt:.1f},{state}\r\n"
        )

        return telemetry_line, self.packet_count, mission_time, alt, state


def _client_alive(client):
    """Detect whether the peer is still connected.

    A graceful close (FIN) does not make ``sendall`` fail immediately, so we
    probe with ``select`` + ``recv(MSG_PEEK)``: readable + empty payload means
    EOF (peer closed); otherwise the connection is still open.
    """
    try:
        readable, _, _ = select.select([client], [], [], 0)
        if not readable:
            return True
        data = client.recv(1, socket.MSG_PEEK)
        return data != b""   # b"" => peer closed, still open otherwise
    except (ConnectionResetError, BrokenPipeError, OSError):
        return False


def run_tcp_server(host, port):
    """Streams telemetry to any connected GCS client over TCP socket."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)

    print("=" * 65)
    print(f"📡 CanSat Telemetry Simulator (TCP Mode)")
    print(f"   Listening on : {host}:{port}")
    print(f"   GCS Address  : 127.0.0.1:{port}")
    print("   Status       : Waiting for GCS to connect...")
    print("=" * 65)

    profile = FlightProfile()

    while True:
        client = None
        try:
            client, addr = server.accept()
            print(f"\n[+] GCS Client Connected from {addr[0]}:{addr[1]}")
            client.sendall(CSV_HEADER.encode("utf-8"))
            profile.reset()

            while True:
                if not _client_alive(client):
                    break
                line, count, m_time, alt, state = profile.step()
                try:
                    client.sendall(line.encode("utf-8"))
                except (BrokenPipeError, ConnectionResetError, OSError):
                    break
                print(f"[{m_time}] Pkt #{count:03d} | Alt: {alt:6.1f} m | State: {state:<12} -> Sent")
                time.sleep(1.0)

        except (ConnectionResetError, BrokenPipeError):
            pass
        except KeyboardInterrupt:
            print("\n[!] Simulator terminated by user.")
            break
        finally:
            if client is not None:
                try:
                    client.close()
                except Exception:
                    pass
        print("[-] GCS Client Disconnected. Waiting for reconnection...\n")

    server.close()


def run_serial(port, baudrate):
    """Streams telemetry over physical USB/UART Serial port."""
    try:
        import serial
    except ImportError:
        print("[ERROR] pyserial is required for serial mode: pip install pyserial")
        sys.exit(1)

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
    except Exception as e:
        print(f"[ERROR] Failed to open serial port {port}: {e}")
        sys.exit(1)

    print("=" * 65)
    print(f"📡 CanSat Telemetry Simulator (Serial Mode)")
    print(f"   Port     : {port} @ {baudrate} baud")
    print("   Status   : Streaming telemetry at 1 Hz...")
    print("=" * 65)

    ser.write(CSV_HEADER.encode("utf-8"))
    profile = FlightProfile()

    try:
        while True:
            line, count, m_time, alt, state = profile.step()
            ser.write(line.encode("utf-8"))
            print(f"[{m_time}] Pkt #{count:03d} | Alt: {alt:6.1f} m | State: {state:<12} -> Sent")
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n[!] Simulator terminated by user.")
    finally:
        ser.close()


def main():
    parser = argparse.ArgumentParser(description="CanSat Telemetry Simulator (GCS Development)")
    parser.add_argument("--port", type=int, default=9999, help="TCP Port (default: 9999)")
    parser.add_argument("--host", default="0.0.0.0", help="TCP Host bind (default: 0.0.0.0)")
    parser.add_argument("--serial", help="Serial port (e.g. /dev/ttyUSB0 or COM3)")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baudrate (default: 115200)")

    args = parser.parse_args()

    if args.serial:
        run_serial(args.serial, args.baud)
    else:
        run_tcp_server(args.host, args.port)


if __name__ == "__main__":
    main()
