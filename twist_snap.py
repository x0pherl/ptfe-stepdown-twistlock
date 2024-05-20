"""

Twist & Snap Connector

name: twist_snap.py
by:   x0pherl
date: May 19 2024

desc: A parameterized twist and snap fitting.

license:

    Copyright 2024 x0pherl

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
from configparser import ConfigParser
from math import radians, cos, sin
from build123d import (BuildPart, BuildSketch, Cylinder, PolarLocations,
                       sweep, Compound, Polygon, fillet, add,
                       Mode, Locations, Align, GeomType, SortBy, Axis)

def angular_intersection(radius, angle):
    """
    For a circle of a given radius, find the x,y coordinates of an intersection at the given angle

    Args:
        radius: The radius of the circle
        angle: the angle at which to find the intersection

    Returns:
        x,y: The x and y coordinates of the intersection
    """
    angle_radians = radians(angle)
    x_coord = radius * cos(angle_radians)
    y_coord = radius * sin(angle_radians)
    return x_coord, y_coord

class TwistSnapConnector:
    """TwistSnap Connector

    TwistSnap connectors and sockets that twist together and lock

    Args:
        connector_diameter (int): The diameter of the connection.
        wall_size (int): Sets bot the width and depth of the walls.

        tolerance (int): Sets the tolerance between the two parts

    Raises:
        ValueError: if end_finishes not in ["raw", "square", "fade", "chamfer"]:
    """

    def __init__(self, connector_diameter=10, wall_size=2, tolerance=.1):
        """
        Initialize the InternalFitting by loading a configuration file.

        Args:
            connector_diameter (int): The diameter of the connection.
            wall_size (int): Sets bot the width and depth of the walls. These
        can be adjusted independently through the wall_width and wall_depth 
        properties after initialization.
            tolerance (int): Sets the tolerance between the two parts
        """
        self.config = ConfigParser()
        self.connector_diameter = connector_diameter
        self.grip_diameter = connector_diameter + wall_size * 2
        self.wall_depth = wall_size
        self.wall_width = wall_size
        self.tolerance = tolerance

    def load_config(self, config_file):
        """
        Update config values by loading a configuration file.

        Args:
            config_file (str): Path to the configuration file.
        """
        self.config.read(config_file)

    @property
    def snapfit_radius_extension(self):
        """
        Gets the distance by which the snapfit connector extends
        out from the connector radius. Defaults to 2/3 of the wall_width.

        Returns:
            float: The distance by which the snapfit connector extends
        out from the connector radius.
        """
        return self.config.getfloat('snapfit', 'radius_extension', fallback=self.wall_width*2/3)

    @snapfit_radius_extension.setter
    def snapfit_radius_extension(self, value):
        """
        Sets the distance by which the snapfit connector extends
        out from the connector radius.

        Args:
            float: The distance by which the snapfit connector extends
        out from the connector radius.
        """
        if 'snapfit' not in self.config.sections():
            self.config.add_section('snapfit')
        self.config.set('snapfit', 'radius_extension', str(value))

    @property
    def snapfit_height(self):
        """
        Gets the overall height of the snapfit connector. 
        Defaults to the wall_depth.

        Returns:
            float: The overall height of the snapfit connector.
        """
        return self.config.getfloat('snapfit', 'height', fallback=self.wall_depth)

    @snapfit_height.setter
    def snapfit_height(self, value):
        """
        Sets the overall height of the snapfit connector.

        Args:
            float: The overall height of the snapfit connector.
        """
        if 'snapfit' not in self.config.sections():
            self.config.add_section('snapfit')
        self.config.set('snapfit', 'height', str(value))

    @property
    def arc_percentage(self):
        """
        Get the percentage of the circle that each snapfit extends around.

        Returns:
            float: The percentage of the circle that each snapfit extends around.
        """
        return self.config.getfloat('snapfit', 'arc_percentage', fallback=10)

    @arc_percentage.setter
    def arc_percentage(self, value):
        """
        Set the percentage of the circle that each snapfit extends around.

        Args:
            float: The percentage of the circle that each snapfit extends around.
        """
        if 'snapfit' not in self.config.sections():
            self.config.add_section('snapfit')
        self.config.set('snapfit', 'arc_percentage', str(value))

    @property
    def snapfit_count(self):
        """
        Gets the number of snapfit connectors.

        Returns:
            float: The number of snapfit connectors.
        """
        return self.config.getint('snapfit', 'count', fallback=4)

    @snapfit_count.setter
    def snapfit_count(self, value):
        """
        Sets the number of snapfit connectors.

        Args:
            float: The number of snapfit connectors.
        """
        if 'snapfit' not in self.config.sections():
            self.config.add_section('snapfit')
        self.config.set('snapfit', 'count', str(value))

    @property
    def grip_diameter(self):
        """
        Get the diameter of the PTFE tube path. Note: this is the
        value as printed but tolerance is added in the calculated
        size of the tube path.

        Returns:
            float: The diameter of the PTFE tube path.
        """
        return self.config.getfloat('grip', 'diameter', fallback=6)

    @grip_diameter.setter
    def grip_diameter(self, value):
        """
        Set the diameter of the outer fitting.

        Args:
            float: The diameter of the outer fitting.
        """
        if 'grip' not in self.config.sections():
            self.config.add_section('grip')
        self.config.set('grip', 'diameter', str(value))

    @property
    def wall_depth(self):
        """
        Get the wall thickness used in calculating various part sizes.

        Returns:
            float: The wall thickness used in calculating various part sizes.
        """
        return self.config.getfloat('general', 'wall_depth', fallback=2)

    @wall_depth.setter
    def wall_depth(self, value):
        """
        Set the wall thickness used in calculating various part sizes.

        Args:
            float: The wall thickness used in calculating various part sizes.
        """
        if 'general' not in self.config.sections():
            self.config.add_section('general')
        self.config.set('general', 'wall_depth', str(value))

    @property
    def wall_width(self):
        """
        Get the thickness for the outer wall of the socket.

        Returns:
            float: The thickness for the outer wall of the socket.
        """
        return self.config.getfloat('general', 'wall_width', fallback=2)

    @wall_width.setter
    def wall_width(self, value):
        """
        Set the thickness for the outer wall of the socket.

        Args:
            float: The thickness for the outer wall of the socket.
        """
        if 'general' not in self.config.sections():
            self.config.add_section('general')
        self.config.set('general', 'wall_width', str(value))

    @property
    def tolerance(self):
        """
        Get the allowance of size between the socket and the connector.

        Returns:
            float: The allowance of size between the socket and the connector.
        """
        return self.config.getfloat('general', 'tolerance', fallback=.1)

    @tolerance.setter
    def tolerance(self, value):
        """
        Set the allowance of size between the socket and the connector.

        Args:
            float: The allowance of size between the socket and the connector.
        """
        if 'general' not in self.config.sections():
            self.config.add_section('general')
        self.config.set('general', 'tolerance', str(value))

    @property
    def twist_snap_connector(self) -> Compound:
        """
        Builds a Part for the defined twist snap connector
        """
        with BuildPart() as twistbase:
            Cylinder(
                radius=self.connector_diameter,
                height=self.wall_depth*2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            path = (
                twistbase.edges()
                .filter_by(GeomType.CIRCLE)
                .sort_by(Axis.Z, reverse=True)
                .sort_by(SortBy.RADIUS)[-1]
            )  # top edge of cylinder
            path = path.trim(self.arc_percentage/-200,
                             self.arc_percentage/200)
            with BuildPart(mode=Mode.PRIVATE) as snapfit:
                path = path.rotate(Axis.Z, 90)
                with BuildSketch(path ^ 0):
                    Polygon(
                        (
                            (0, 0),
                            (self.snapfit_radius_extension, 0),
                            (self.snapfit_radius_extension, self.snapfit_height),
                            (0, self.snapfit_height/2),
                        ),
                        align=(Align.MAX, Align.MIN),
                    )
                sweep(path=path)
                with Locations(snapfit.part.center() + (0, self.snapfit_radius_extension / 2, 0)):
                    Cylinder(radius=self.snapfit_radius_extension / 2,
                             height=self.snapfit_height*3, mode=Mode.SUBTRACT)
                fillet(
                    snapfit.faces().sort_by(Axis.Y)[-2:].edges().filter_by(Axis.Z),
                    min(self.snapfit_radius_extension / 8,
                        snapfit.part.max_fillet(
                            snapfit.faces().sort_by(Axis.Y)[-2:].edges().
                            filter_by(Axis.Z), max_iterations=40))
                )

            with PolarLocations(0, self.snapfit_count):
                add(snapfit.part)
        return twistbase

    @property
    def xtwist_snap_socket(self) -> Compound:
        """
        Returns a Part for the defined twist snap socket
        """
        with BuildPart() as socket_fitting:
            with BuildPart() as snap_socket:
                Cylinder(
                    radius=self.connector_diameter+self.wall_width*2,
                    height=self.wall_depth*2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                Cylinder(
                    radius=self.connector_diameter+self.tolerance,
                    height=self.wall_depth*2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT
                )
                trace_path = (
                    snap_socket.edges()
                    .filter_by(GeomType.CIRCLE)
                    .sort_by(Axis.Z, reverse=True)
                    .sort_by(SortBy.RADIUS, reverse=True)[-1]
                )  # top edge of cylinder
                path = trace_path.trim((self.arc_percentage/-200)*1.1,
                                       (self.arc_percentage/200)*1.1)
                with BuildPart(mode=Mode.PRIVATE) as snapfit:
                    path = path.rotate(Axis.Z, 90)
                    with BuildSketch(path ^ 0):
                        Polygon(
                            (
                                (0, 0),
                                (self.snapfit_radius_extension, 0),
                                (self.snapfit_radius_extension, self.snapfit_height*2),
                                (0, self.snapfit_height*2),
                            ),
                            align=(Align.MAX, Align.MIN),
                        )
                    sweep(path=path)
                    fillet(
                        snapfit.faces().sort_by(Axis.Y)[-1].edges().filter_by(Axis.Z),
                        self.snapfit_radius_extension / 8,
                    )
                with PolarLocations(0, self.snapfit_count):
                    add(snapfit.part, mode=Mode.SUBTRACT)

                path = trace_path.trim((self.arc_percentage/-200)*1.1,
                                       (self.arc_percentage/200)*3.1)
                with BuildPart(mode=Mode.PRIVATE) as snapfit:
                    path = path.rotate(Axis.Z, 90)
                    with BuildSketch(path ^ 0):
                        Polygon(
                            (
                                (0, 0),
                                (self.snapfit_radius_extension+self.tolerance, 0),
                                (self.snapfit_radius_extension+self.tolerance,
                                    self.snapfit_height+self.tolerance),
                                (0, self.snapfit_height/2+self.tolerance),
                            ),
                            align=(Align.MAX, Align.MIN),
                        )
                    sweep(path=path)
                    fillet(
                        snapfit.faces().sort_by(Axis.Y)[-1].edges().filter_by(Axis.Z),
                        self.snapfit_radius_extension / 8,
                    )
                with PolarLocations(0, self.snapfit_count):
                    add(snapfit.part, mode=Mode.SUBTRACT)
                with PolarLocations(
                        self.connector_diameter+self.snapfit_radius_extension+
                        self.tolerance*2, self.snapfit_count,
                        start_angle=360/self.arc_percentage+90):
                    Cylinder(radius=self.snapfit_radius_extension / 2,
                                height=self.snapfit_height,
                                align=(Align.CENTER,Align.CENTER, Align.MIN))
            with BuildPart(snap_socket.faces().sort_by(Axis.Z, reverse=True)[-1]):
                Cylinder(
                    radius=self.connector_diameter+self.wall_width*2,
                    height=self.wall_depth*1,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

        return socket_fitting

    @property
    def twist_snap_socket(self) -> Compound:
        """
        Returns a Part for the defined twist snap socket
        """
        with BuildPart() as socket_fitting:
            # Cylinder(
            #     radius=self.connector_diameter+self.wall_width*4/3,
            #     height=self.wall_depth,
            #     align=(Align.CENTER, Align.CENTER, Align.MIN),
            # )
            # with BuildPart(socket_fitting.faces().sort_by(Axis.Z)[-1]) as snap_socket:
            with BuildPart() as snap_socket:
                Cylinder(
                    radius=self.connector_diameter+self.wall_width*4/3,
                    height=self.wall_depth*2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                Cylinder(
                    radius=self.connector_diameter+self.tolerance,
                    height=self.wall_depth*2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT
                )
            trace_path = (
                snap_socket.edges()
                .filter_by(GeomType.CIRCLE)
                .sort_by(Axis.Z, reverse=True)
                .sort_by(SortBy.RADIUS, reverse=True)[-1]
            )  # top edge of cylinder
            path = trace_path.trim((self.arc_percentage/-200)*1.1,
                                    (self.arc_percentage/200)*1.1)
            with BuildPart(mode=Mode.PRIVATE) as snapfit:
                path = path.rotate(Axis.Z, 90)
                with BuildSketch(path ^ 0):
                    Polygon(
                        (
                            (0, 0),
                            (self.snapfit_radius_extension, 0),
                            (self.snapfit_radius_extension, self.snapfit_height*2),
                            (0, self.snapfit_height*2),
                        ),
                        align=(Align.MAX, Align.MIN),
                    )
                sweep(path=path)
                fillet(
                    snapfit.faces().sort_by(Axis.Y)[-1].edges().filter_by(Axis.Z),
                    self.snapfit_radius_extension / 8,
                )
            with PolarLocations(0, self.snapfit_count):
                add(snapfit.part, mode=Mode.SUBTRACT)

            path = trace_path.trim((self.arc_percentage/-200)*3.1,
                                   (self.arc_percentage/200)*1.1)
            with BuildPart(mode=Mode.PRIVATE) as snapfit:
                path = path.rotate(Axis.Z, 90)
                with BuildSketch(path ^ 0):
                    Polygon(
                        (
                            (0, 0),
                            (self.snapfit_radius_extension+self.tolerance, 0),
                            (self.snapfit_radius_extension+self.tolerance,
                                self.snapfit_height+self.tolerance),
                            (0, self.snapfit_height/2+self.tolerance),
                        ),
                        align=(Align.MAX, Align.MIN),
                    )
                sweep(path=path)
                fillet(
                    snapfit.faces().sort_by(Axis.Y)[-1].edges().filter_by(Axis.Z),
                    self.snapfit_radius_extension / 8,
                )
            with PolarLocations(0, self.snapfit_count):
                add(snapfit.part, mode=Mode.SUBTRACT)
            with PolarLocations(
                    self.connector_diameter+self.snapfit_radius_extension+
                    self.tolerance*2, self.snapfit_count,
                    start_angle=self.arc_percentage*-4):
                Cylinder(radius=self.snapfit_radius_extension / 2,
                            height=self.snapfit_height*2,
                            align=(Align.CENTER,Align.CENTER, Align.MIN))

        return socket_fitting
    
from ocp_vscode import show
ts = TwistSnapConnector(4.5,2)
show(ts.twist_snap_socket.part)
from build123d import export_stl
export_stl(ts.twist_snap_socket.part, 'stl/snap-socket.stl')