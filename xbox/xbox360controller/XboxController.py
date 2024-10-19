import pygame
import xbox360_controller
import rclpy
from std_msgs.msg import Float32MultiArray
from rclpy.node import Node
from geometry_msgs.msg import Twist, Vector3

class XboxController(Node):
    def __init__(self):
        super().__init__('xbox_controller')
                
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        pygame.init()
        pygame.joystick.init()

        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()
        if joystick_count != 1:
            print("cant detect controller")
            print("Number of joysticks: {}".format(joystick_count))

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        self.name = self.joystick.get_name()
        print(f"Joystick name: {self.name}")
        
    def xbox_cmdvel(self):
        # 이벤트 처리 루프
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Exiting...")
                return

        # 축 정보 가져오기
        self.axes = self.joystick.get_numaxes()

        # 선형 속도 계산 (오른쪽 스틱 X축)
        self.linear_axis = xbox360_controller.RIGHT_STICK_X
        self.linear_val = self.joystick.get_axis(self.linear_axis)

        # 선형 속도: 1 (go) ~ -1 (back)
        linear_vel = -(self.linear_val) * 1.5

        # 각속도 계산 (좌우 트리거)
        # L_Yaw_axis = xbox360_controller.LEFT_TRIGGER
        L_Yaw_axis = 5
        L_Yaw_value = self.joystick.get_axis(L_Yaw_axis) + 1
        # R_Yaw_axis = xbox360_controller.RIGHT_TRIGGER
        R_Yaw_axis = 4  
        R_Yaw_value = self.joystick.get_axis(R_Yaw_axis) + 1

        delta_Yaw_value = R_Yaw_value - L_Yaw_value
        Yaw_maximum_value = 1.5  # radian/s
        angular_vel = (delta_Yaw_value / 2) * Yaw_maximum_value

        # Twist 메시지 생성 및 발행
        xbox_msg = Twist()
        xbox_msg.linear = Vector3(x=linear_vel, y=0.0, z=0.0)
        xbox_msg.angular = Vector3(x=0.0, y=0.0, z=angular_vel)
        self.publisher.publish(xbox_msg)

        print(f"linear : {linear_vel}")
        print(f"angular : {angular_vel}")

def main():
    rclpy.init(args=None)
    node = XboxController()  # XboxController 클래스 인스턴스 생성
    
    try:
        while rclpy.ok():
            node.xbox_cmdvel()  # 컨트롤러 입력을 받아들임
            rclpy.spin_once(node, timeout_sec=0.1)  # 이벤트를 처리하며 0.1초 동안 스핀
    except (Exception, KeyboardInterrupt):
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
