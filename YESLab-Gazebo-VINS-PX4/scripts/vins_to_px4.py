#!/usr/bin/env python3
import rospy
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped, TwistStamped

rospy.init_node('force_vision_v2')

# 发布位置和速度，缺一不可
pub_pose = rospy.Publisher('/mavros/vision_pose/pose', PoseStamped, queue_size=10)
pub_vel = rospy.Publisher('/mavros/vision_speed/speed_twist', TwistStamped, queue_size=10)

def gz_cb(msg):
    try:
        idx = msg.name.index('iris')  # 找到无人机模型
        p = msg.pose[idx].position    # 位置
        q = msg.pose[idx].orientation # 姿态（四元数）
        v = msg.twist[idx].linear     # 速度

        # 1. 发布位置 (ENU 转 NED)
        pose = PoseStamped()
        pose.header.stamp = rospy.Time.now()
        pose.header.frame_id = "odom"
        # ENU (东, 北, 天) -> NED (北, 东, 地)
        pose.pose.position.x = p.y
        pose.pose.position.y = p.x
        pose.pose.position.z = -p.z
        # 姿态四元数转换
        pose.pose.orientation.x = q.y
        pose.pose.orientation.y = q.x
        pose.pose.orientation.z = -q.z
        pose.pose.orientation.w = q.w
        pub_pose.publish(pose)

        # 2. 发布速度 (ENU 转 NED)
        vel = TwistStamped()
        vel.header.stamp = rospy.Time.now()
        vel.header.frame_id = "odom"
        vel.twist.linear.x = v.y
        vel.twist.linear.y = v.x
        vel.twist.linear.z = -v.z
        pub_vel.publish(vel)

    except ValueError:
        pass

# 订阅 Gazebo 真值
rospy.Subscriber('/gazebo/model_states', ModelStates, gz_cb)
rospy.spin()
