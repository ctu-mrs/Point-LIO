from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from mrs_lib.remappings_custom_config_parser import RemappingsCustomConfigParser
from ament_index_python.packages import get_package_share_directory

import launch

import os

def generate_launch_description():

    ld = launch.LaunchDescription()

    uav_name = LaunchConfiguration('uav_name')

    pkg_name = "point_lio"

    this_pkg_path = get_package_share_directory(pkg_name)

    ld.add_action(DeclareLaunchArgument(
        'uav_name',
        default_value=os.getenv('UAV_NAME', "uav1"),
        description="The uav name used for namespacing.",
    ))

    node = ComposableNode(
        package='point_lio',
        plugin='point_lio::PointLio',
        name='point_lio',
        namespace=uav_name,
        parameters=[
            {"use_sim_time": True},
            {"uav_name": uav_name},
            {"config" : this_pkg_path+'/config/simulation.yaml'},
        ],
        remappings=[
            # subscribers
            ('~/imu_in', 'hw_api/imu'),
            ('~/pc_in', 'lidar/points'),
            ('~/livox_in', '~/livox_in'),
            # publishers
            ('~/odometry_out', '~/odometry'),
            ('~/cloud_registered_out', '~/cloud_registered'),
            ('~/cloud_registered_body_out', '~/cloud_registered_body'),
            ('~/laser_cloud_map_out', '~/laser_cloud_map'),
            ('~/linear_acceleration_out', '~/linear_acceleration'),
            ('~/path_out', '~/path'),
        ]
    )

    # #{ container

    container = ComposableNodeContainer(
        name='point_lio_container',
        namespace=uav_name,
        package='rclcpp_components',
        executable='component_container_mt',
        output="screen",
        #prefix='xterm -e gdb -ex run --args',
        # prefix='gdb -ex run --args',
        # prefix='valgrind --tool=massif',
        composable_node_descriptions=[node],
        parameters=[
            {'use_intra_process_comms': True},
            {'thread_num': os.cpu_count()},
            {'use_sim_time': True},
        ],
    )

    ld.add_action(container)

    # #} end of container

    return ld
