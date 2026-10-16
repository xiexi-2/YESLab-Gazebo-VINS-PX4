# YESLab-Gazebo-VINS-PX4

## 一、实验环境
- 操作系统：Ubuntu 20.04
- ROS版本：ROS Noetic
- 飞控仿真：PX4 SITL
- 仿真引擎：Gazebo Classic 11
- 通信桥接：MAVROS
- 视觉惯性里程计：VINS-Fusion (适配 OpenCV 4 版本)
- 可视化：RViz

## 二、系统数据流
Gazebo (Camera + IMU) → VINS-Fusion (位姿估计) → MAVROS (External Vision) → PX4 EKF2 (状态融合) → Position (POSCTL) 模式。

**注**：由于 Gazebo 纯仿真环境的视觉纹理缺乏且存在物理引擎锁步机制，VINS-Fusion 在多次排查与参数调整后仍无法完成初始化。为了验证 MAVROS 到 PX4 的完整控制链路，实验中改用 Gazebo Ground Truth 进行 ENU 转 NED 坐标转换，模拟 External Vision 数据发送给 PX4。

## 三、实际使用的 Topic
- Camera: `/camera/image_raw`
- IMU: `/gazebo_imu/data` (由 Gazebo 原生 ROS 插件发布)
- VINS Pose/Odometry: `/vins_estimator/odometry` (仿真受限未能输出)
- PX4 External Vision: `/mavros/vision_pose/pose`
- PX4 Local Position: `/mavros/local_position/pose`

## 四、完整启动顺序
1. `roscore`
2. `rosparam set /use_sim_time true`
3. `make px4_sitl_default gazebo`
4. `roslaunch mavros px4.launch fcu_url:="udp://:14540@127.0.0.1:14557" _use_sim_time:=true`
5. 在 QGC 中切换 `定点 Position` (POSCTL) 模式，解锁起飞。

## 五、VINS-Fusion 结果说明
由于 Gazebo 仿真环境地面纹理缺乏，且存在物理引擎锁步机制与时间戳跳变，VINS-Fusion 在仿真环境下未能完成初始化。
*(此处对应 images/vins_rviz.png 截图)*

## 六、PX4 定位结果
通过外部视觉数据接入，PX4 成功获得有效 Local Position。
*(此处对应 images/px4_local_position.png 截图)*

## 七、Position 模式结果
无人机在无 GPS 环境下成功进入 Position (POSCTL) 模式，并实现了稳定悬停与前后左右移动。
- 视频证据：详见 video/demo_link.txt
*(此处对应 images/position_mode.png 和 images/gazebo.png 截图)*

## 八、问题记录
- **现象**：VINS-Fusion 始终报 `IMU excitation not enough` 和 `Not enough features or parallax`，无法初始化。
- **原因**：Gazebo 纯色地面与模型缺乏视觉特征点；物理引擎锁步机制导致 IMU 数据污染；MAVROS 时间戳跳变导致数据无法对齐。
- **解决方法**：
    1. 修改 `iris.sdf.jinja` 添加 Gazebo ROS IMU 插件，解决数据来源问题；
    2. 开启全局 `use_sim_time` 并强制 VINS 节点读取仿真时间；
    3. 采用 Gazebo Ground Truth 模拟外部视觉数据，验证完整控制链路。
- **最终结果**：成功实现无 GPS 下 Position 模式稳定悬停、移动及高度变化。

## 九、任务总结
VINS-Fusion 负责估计位姿，PX4 负责位置控制。关闭 GPS 后仍可控制是因为 MAVROS 向 PX4 喂入了外部视觉数据，EKF2 融合这些数据替代了 GPS。

## 十、验收提问准备
Gazebo 在本任务中负责什么？

答：Gazebo 是一个物理仿真引擎。它负责提供仿真环境（地面、光照）、无人机的物理模型，以及输出逼真的虚拟相机图像和 IMU 惯性数据。

PX4 SITL 是什么？

答：SITL 是 Software In The Loop（软件在环仿真）的缩写。它意味着我们在电脑上运行真实的 PX4 飞控固件（而非真实硬件飞控板），接收仿真数据并输出电机控制指令。

VINS-Fusion 是做什么的？

答：VINS-Fusion 是一个视觉惯性里程计算法。它通过融合相机图像和 IMU 数据，实时估计无人机在空间中的位置和姿态（位姿）。

VINS-Fusion 为什么同时需要相机和 IMU？

答：单靠相机无法轻易恢复尺度，且快速运动时容易丢失特征；单靠 IMU 会随时间产生严重的积分漂移。两者融合可以互补，相机提供环境特征，IMU 提供高频运动信息。

Position、Orientation 和 Odometry 分别是什么意思？

答：Position（位置）是无人机在三维空间中的 x、y、z 坐标；Orientation（姿态）是无人机自身的旋转（如四元数或欧拉角）；Odometry（里程计）是一个包含位置、姿态，通常还包含线速度和角速度的消息。

ROS Topic 是什么？

答：ROS Topic 是 ROS 节点之间进行异步通信的“广播频道”。一个节点发布消息，多个节点可以订阅接收。

MAVROS 在本系统中起什么作用？

答：MAVROS 是 ROS 和 PX4 飞控之间的桥梁。它把 ROS 的视觉位姿消息转换成飞控能懂的 MAVLink 协议，同时把飞控的状态（如位置、电量）转换成 ROS 消息。

VINS 已经能输出轨迹，为什么还要把数据送给 PX4？

答：VINS 只是“估计器”，它只告诉我们“无人机在哪里”，它不能控制无人机飞行。PX4 是“控制器”，它必须拿到位置估计后，才能进行位置控制（保持悬停、移动）。

PX4 Local Position 是什么？

答：这是 PX4 内部 EKF2 状态估计器融合了外部视觉位置后，计算出的无人机在本地坐标系（NED）下的位置。这是飞行控制直接使用的数据。

为什么关闭 GPS 后仍有可能进入 Position 模式？

答：因为 PX4 支持多传感器融合。只要通过 MAVROS 把外部视觉位置（External Vision）喂给 EKF2，EKF2 就会用视觉数据替代 GPS 提供水平位置，从而进入 Position 模式。

为什么 ROS 与 PX4 之间需要处理坐标系？

答：ROS 使用 ENU 坐标系（X向东，Y向北，Z向上），而 PX4 使用 NED 坐标系（X向北，Y向东，Z向下）。不转换直接发送，无人机将往完全错误的方向飞。

如果 VINS 的坐标方向接反，飞行会出现什么问题？

答：无人机可能会失控，比如你让它前进，它却往后飞；你让它上升，它却下降，最终导致坠机或飞丢。

如果 VINS 漂移，Position 模式可能出现什么现象？

答：无人机在悬停时，位置会慢慢发生滑动（如缓慢向一侧漂移），无法长时间稳定保持在同一个点上。

如果 VINS 数据突然中断，PX4 可能发生什么？

答：PX4 会检测到位置数据丢失，触发失控保护（Failsafe）。无人机可能会自动切换到高度模式，或者自动降落，严重时可能会失控坠落。

Gazebo Ground Truth 为什么不能直接作为本任务的 PX4 位置输入？

答：Ground Truth 是仿真环境里的绝对真值，在真实世界中是不存在的。用真值作为视觉输入相当于“作弊”，跳过了视觉算法的验证。本实验用它，是因为纯Gazebo环境导致VINS无法初始化，为了验证控制链路而做的工程妥协。

仿真复现成功为什么不代表实机一定可以直接成功？

答：因为仿真环境太完美了（没有风的扰动、光线恒定、没有传感器噪声、物理引擎过于平滑）。真实世界充满了干扰、震动、光照变化和通信延迟，需要更鲁棒的算法和更精细的调试。


