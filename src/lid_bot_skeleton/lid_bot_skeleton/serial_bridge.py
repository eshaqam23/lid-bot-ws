"""Serial bridge: /cmd_vel (Twist) -> "<left> <right>\\n" over USB to the ESP32.

Differential drive math:
    left  = v - w * L / 2
    right = v + w * L / 2
v = linear.x (m/s), w = angular.z (rad/s), L = wheel_separation (m).
Wheel speeds are then scaled to PWM (-255..255) using max_wheel_speed.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial


class SerialBridge(Node):
    def __init__(self):
        super().__init__('serial_bridge')

        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baud', 115200)
        self.declare_parameter('wheel_separation', 0.13)  # meters, measure your car
        self.declare_parameter('max_wheel_speed', 0.5)    # m/s that maps to PWM 255
        self.declare_parameter('cmd_timeout', 0.5)        # s without cmd_vel -> stop
        self.declare_parameter('send_rate', 20.0)         # Hz

        port = self.get_parameter('port').value
        baud = self.get_parameter('baud').value
        self.L = self.get_parameter('wheel_separation').value
        self.vmax = self.get_parameter('max_wheel_speed').value
        self.timeout = self.get_parameter('cmd_timeout').value

        self.port = port
        self.baud = baud
        self.ser = serial.Serial(port, baud, timeout=0)
        self.get_logger().info(f'Opened {port} at {baud}')

        self.left = 0
        self.right = 0
        self.last_cmd = self.get_clock().now()

        self.create_subscription(Twist, 'cmd_vel', self.on_cmd, 10)
        rate = self.get_parameter('send_rate').value
        self.create_timer(1.0 / rate, self.send)

    def to_pwm(self, wheel_speed):
        pwm = int(round(wheel_speed / self.vmax * 255))
        return max(-255, min(255, pwm))

    def on_cmd(self, msg: Twist):
        v = msg.linear.x
        w = msg.angular.z
        self.left = self.to_pwm(v - w * self.L / 2)
        self.right = self.to_pwm(v + w * self.L / 2)
        self.last_cmd = self.get_clock().now()

    def send(self):
        # Resend at a steady rate so the ESP32 watchdog stays fed.
        age = (self.get_clock().now() - self.last_cmd).nanoseconds / 1e9
        if age > self.timeout:
            self.left = self.right = 0
        try:
            if self.ser is None or not self.ser.is_open:
                self.ser = serial.Serial(self.port, self.baud, timeout=0)
                self.get_logger().info(f'Reconnected to {self.port}')
            self.ser.write(f'{self.left} {self.right}\n'.encode())
            data = self.ser.read(self.ser.in_waiting or 0)
            if data:
                self.get_logger().info(f'ESP32: {data.decode(errors="ignore").strip()}')
        except (serial.SerialException, OSError) as e:
            self.get_logger().warn(f'Serial error: {e}. Retrying...', throttle_duration_sec=2.0)
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None

    def destroy_node(self):
        try:
            self.ser.write(b'0 0\n')
            self.ser.close()
        except Exception:
            pass
        super().destroy_node()


def main():
    rclpy.init()
    node = SerialBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
