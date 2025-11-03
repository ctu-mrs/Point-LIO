from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.substitutions import FindPackageShare
from mrs_lib.remappings_custom_config_parser import RemappingsCustomConfigParser
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import (
        LaunchConfiguration,
        IfElseSubstitution,
        PythonExpression,
        PathJoinSubstitution,
        EnvironmentVariable,
        )

import launch

import os

def generate_launch_description():

    ld = launch.LaunchDescription()

    uav_name = LaunchConfiguration('uav_name')

    pkg_name = "point_lio"

    this_pkg_path = get_package_share_directory(pkg_name)

    # #{ custom_config

    custom_config = LaunchConfiguration('custom_config')

    # this adds the args to the list of args available for this launch files
    # these args can be listed at runtime using -s flag
    # default_value is required to if the arg is supposed to be optional at launch time
    ld.add_action(DeclareLaunchArgument(
        'custom_config',
        default_value="",
        description="Path to the custom configuration file. The path can be absolute, starting with '/' or relative to the current working directory",
        ))

    # behaviour:
    #     custom_config == "" => custom_config: ""
    #     custom_config == "/<path>" => custom_config: "/<path>"
    #     custom_config == "<path>" => custom_config: "$(pwd)/<path>"
    custom_config = IfElseSubstitution(
            condition=PythonExpression(['"', custom_config, '" != "" and ', 'not "', custom_config, '".startswith("/")']),
            if_value=PathJoinSubstitution([EnvironmentVariable('PWD'), custom_config]),
            else_value=custom_config
            )

    # #} end of custom_config

    # #{ uav_name

    uav_name = LaunchConfiguration('uav_name')

    ld.add_action(DeclareLaunchArgument(
        'uav_name',
        default_value=os.getenv('UAV_NAME', "uav1"),
        description="The uav name used for namespacing.",
    ))

    # #} end of custom_config

    # #{ standalone

    standalone = LaunchConfiguration('standalone')

    declare_standalone = DeclareLaunchArgument(
        'standalone',
        default_value='true',
        description='Whether to start a as a standalone or load into an existing container.'
    )

    ld.add_action(declare_standalone)

    # #} end of standalone

    # #{ use_sim_time

    use_sim_time = LaunchConfiguration('use_sim_time')

    ld.add_action(DeclareLaunchArgument(
        'use_sim_time',
        default_value=os.getenv('USE_SIM_TIME', "false"),
        description="Should the node subscribe to sim time?",
    ))

    # #} end of custom_config

    node = ComposableNode(
        package='point_lio',
        plugin='point_lio::PointLio',
        name='point_lio',
        namespace=uav_name,
        parameters=[
            {"use_sim_time": use_sim_time},
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
            {'use_sim_time': use_sim_time},
        ],
    )

    ld.add_action(container)

    # #} end of container

    return ld
