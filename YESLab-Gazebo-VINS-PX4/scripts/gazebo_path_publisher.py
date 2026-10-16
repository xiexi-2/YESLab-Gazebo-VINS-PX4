#!/usr/bin/env python3
import rospy
from gazebo_msgs.msg import ModelStates
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped

rospy.init_node('gazebo_path_publisher')
path_pub = rospy.Publisher('/drone_path', Path, queue_size=10)
path = Path()
path.header.frame_id = "map"

def model_states_callback(msg):
    try:
        idx = msg.name.index('iris')
        pose = PoseStamped()
        pose.header.stamp = rospy.Time.now()
        pose.header.frame_id = "map"
        pose.pose = msg.pose[idx]
        path.poses.append(pose)
        if len(path.poses) > 5000:
            path.poses.pop(0)
        path.header.stamp = rospy.Time.now()
        path_pub.publish(path)
    except ValueError:
        pass

rospy.Subscriber('/gazebo/model_states', ModelStates, model_states_callback)
rospy.spin()
