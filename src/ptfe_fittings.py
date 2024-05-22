"""

Twist & Snap PTFE Connectors

name: ptfe_fittings.py
by:   x0pherl
date: May 19 2024

desc: Creates 3d objects for connecting PTFE tubing with a twist-lock
connection.

license:

    Copyright 2024 x0pherl

    Use of this source code is governed by an MIT-style
    license that can be found in the LICENSE file or at
    https://opensource.org/licenses/MIT.
"""

from dataclasses import dataclass
from build123d import (export_step, export_stl, add,
    BuildPart, Cylinder, Mode, Axis, Circle, Plane, BuildSketch,
    loft, Align, Location, Locations, RegularPolygon, fillet,
    Part
    )
from bd_warehouse.thread import TrapezoidalThread
from ocp_vscode import show
from twist_snap import TwistSnapConnector

@dataclass
class ThreadedConnector:
    """ThreadedConnector

    Data class containing the details needed to construct a threaded 
    connector

    Args:
        diameter (float): The diameter of the connector.
        length (float): The length of the connector.
        thread_pitch (float): The thread pitch of the connector.
        thread_angle (float): The thread angle of the connector.
    """

    diameter: float = 10
    length: float = 6.7
    thread_pitch:float = 1
    thread_angle:float = 30

def tapered_tube_path(external_radius: float, taper_start_radius:float, taper_end_radius:float,
                     taper_length:float, length:float):
    """
    Returns a tube path through the object with a short printed path
    so that the tube ending is internal to the fitting

    Args:
        external_radius: The outer radius of the tube path
        taper_start_radius: The inner radius of the tube
        taper_end_radius: The inner radius of the exit path
        workplanes: the base workplane to build down from
        taper_length: the length of the printed interior path/funnel
        length: the overall length of the tube path

    Returns:
        an ojbect for cutting the defined tube path
    """
    with BuildPart() as tubecut:
        with BuildPart():
            Cylinder(radius=external_radius, height=length-taper_length,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart():
            with BuildSketch(tubecut.faces().sort_by(Axis.Z)[-1]):
                Circle(radius=taper_start_radius)
            with BuildSketch(tubecut.faces().sort_by(Axis.Z)[-1].offset(taper_length)):
                Circle(radius=taper_end_radius)
            loft()
    return tubecut

def flush_tube_path(external_radius: float, length: float):
    """
    Returns a straight tube path through the object, probably overkill
    but included to keep the interface similar to other tubecuts.
    You can trim the end of the tube precisely after inserting

    Args:
        external_radius: The outer radius of the tube path
        workplanes: the base workplane to build down from
        length: the length of the tube path

    Returns:
        an ojbect for cutting the defined tube path
    """
    with BuildPart() as tubecut:
        Cylinder(radius=external_radius, height=length,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
    return tubecut

def connector_fitting(knob_length:float=10) -> Part:
    """
    Returns a twist snap connector fitting with no internal cuts for tubing
    or screw-in connectors

    Args:
        knob_length: the length of the grip

    Returns:
        a Part ojbect which is a twist snap connector fitting with no internal cuts for tubing
    or screw-in connectors
    """

    with BuildPart() as assembly:
        with BuildPart() as cone:
            with BuildSketch(Plane(origin=(0,0,0), z_dir=(0,0,1))) as cone_end:
                RegularPolygon(radius=7, side_count=6, rotation=20)
                fillet(cone_end.vertices(), radius=1)
            with BuildSketch(Plane(origin=(0,0,knob_length), z_dir=(0,0,1))):
                Circle(radius=4.5+4*2/3)
            loft()
        with BuildPart(cone.faces().sort_by(Axis.Z)[-1]):
            with Locations(Location((0,0,4),(0,180,0))):
                add(TwistSnapConnector(4.5,2).twist_snap_connector.part)
    return assembly.part

def socket_fitting(knob_length:float=10) -> Part:
    """
    Returns a twist snap socket fitting with no internal cuts for tubing
    or screw-in connectors

    Args:
        knob_length: the length of the grip

    Returns:
        a Part ojbect which is a twist snap socket fitting with no internal cuts for tubing
    or screw-in connectors
    """
    with BuildPart() as assembly:
        with BuildPart():
            with BuildSketch(Plane(origin=(0,0,0), z_dir=(0,0,1))) as cone_end:
                RegularPolygon(radius=7, side_count=6, rotation=20)
                fillet(cone_end.vertices(), radius=1)
            with BuildSketch(Plane(origin=(0,0,knob_length), z_dir=(0,0,1))):
                Circle(radius=4.5+4*2/3)
            loft()
        with BuildPart(assembly.faces().sort_by(Axis.Z)[-1]):
            add(TwistSnapConnector(4.5,2).twist_snap_socket.part)
    return assembly.part

def straight_cut_socket_fitting(knob_length=15, tube_outer_diameter=4.3,
                    threaded_connector:ThreadedConnector = ThreadedConnector()) -> Part:
    """
    Returns a twist snap socket fitting with a straight path for
    connecting identical tube diameters with flush mounts or pairing
    with tapered connector fittings

    Args:
        knob_length: the length of the grip
        tube_outer_diameter: the outer diameter of the tube running through the connector 
                            (you'll want to leave some extra tolerance room)
        threaded_connector: a ThreadedConnector object for the screw-in PTFE connector

    Returns:
        a Part ojbect which is a twist snap socket fitting with a straight path for
        connecting identical tube diameters with flush mounts or pairing
        with tapered connector fittings
    """

    with BuildPart() as assembly:
        add(socket_fitting(knob_length))
        add(flush_tube_path(external_radius=tube_outer_diameter, length=knob_length+2),
            mode=Mode.SUBTRACT)
        add(Cylinder(radius=threaded_connector.diameter/2, height=threaded_connector.length,
                     align=(Align.CENTER, Align.CENTER, Align.MIN)),
            mode=Mode.SUBTRACT)

    thread = TrapezoidalThread(
                    diameter=threaded_connector.diameter,
                    pitch=threaded_connector.thread_pitch,
                    length=threaded_connector.length,
                    thread_angle = threaded_connector.thread_angle,
                    external=False,
                    hand="right",
                    align=(Align.CENTER, Align.CENTER, Align.MIN)
                    )
    thread.label = "thread"
    return Part(label="Socket Fitting", children=[
        Part(label="assembly", children=[assembly.part]),
        thread])

def taper_cut_socket_fitting(knob_length=15, tube_outer_diameter=6.4, tube_inner_diameter=3.4,
                        taper_end_diameter=2.7, taper_length=4,
                        threaded_connector:ThreadedConnector = ThreadedConnector()) -> Part:
    """
    Returns a twist snap socket fitting with a tapered path for
    steping down tube diameters with flush mounted connector fittings

    Args:
        knob_length: the length of the grip
        tube_outer_diameter: the outer diameter of the tube running through the connector 
                            (you'll want to leave some extra tolerance room)
        tube_inner_diameter: the inner diameter of the tube running through the connector
        taper_end_diameter: the diameter to leave at the end of the measured tube; should match
                            the inner diameter of the corresponding connector's tube
        taper_length: the length of the cone for the taper.
        threaded_connector: a ThreadedConnector object for the screw-in PTFE connector

    Returns:
        a Part ojbect which is a twist snap socket fitting with a straight path for
        connecting identical tube diameters with flush mounts or pairing
        with tapered connector fittings
    """

    with BuildPart() as assembly:
        add(socket_fitting(knob_length))
        add(tapered_tube_path(external_radius=tube_outer_diameter/2,
                              taper_start_radius=tube_inner_diameter/2,
                              taper_end_radius=taper_end_diameter/2,
                              taper_length=taper_length,
                              length=knob_length+2), mode=Mode.SUBTRACT)
        add(Cylinder(radius=threaded_connector.diameter/2, height=threaded_connector.length,
                     align=(Align.CENTER, Align.CENTER, Align.MIN)),
            mode=Mode.SUBTRACT)

    thread = TrapezoidalThread(
                    diameter=threaded_connector.diameter,
                    pitch=threaded_connector.thread_pitch,
                    length=threaded_connector.length,
                    thread_angle = threaded_connector.thread_angle,
                    external=False,
                    hand="right",
                    align=(Align.CENTER, Align.CENTER, Align.MIN)
                    )
    thread.label = "thread"
    return Part(label="Socket Fitting", children=[
        Part(label="assembly", children=[assembly.part]),
        thread])

def straight_cut_connector_fitting(knob_length=15, tube_diameter=4.3,
                        threaded_connector:ThreadedConnector = ThreadedConnector()) -> Part:
    """
    Returns a twist snap connector fitting with a straight path for
    connecting identical tube diameters with flush mounts or pairing
    with tapered socket fittings

    Args:
        knob_length: the length of the grip
        tube_outer_diameter: the outer diameter of the tube running through the connector 
                            (you'll want to leave some extra tolerance room)
        threaded_connector: a ThreadedConnector object for the screw-in PTFE connector

    Returns:
        a Part ojbect which is a twist snap connector fitting with a straight path for
        connecting identical tube diameters with flush mounts or pairing with tapered 
        socket fittings
    """

    with BuildPart() as assembly:
        add(connector_fitting(knob_length))
        add(flush_tube_path(external_radius=tube_diameter/2, length=knob_length+4),
            mode=Mode.SUBTRACT)
        add(Cylinder(radius=threaded_connector.diameter/2, height=threaded_connector.length,
                     align=(Align.CENTER, Align.CENTER, Align.MIN)),
            mode=Mode.SUBTRACT)

    thread = TrapezoidalThread(
                    diameter=threaded_connector.diameter,
                    pitch=threaded_connector.thread_pitch,
                    length=threaded_connector.length,
                    thread_angle = threaded_connector.thread_angle,
                    external=False,
                    hand="right",
                    align=(Align.CENTER, Align.CENTER, Align.MIN)
                    )
    thread.label = "thread"
    return Part(label="Connector Fitting", children=[
        Part(label="assembly", children=[assembly.part]),
        thread])

def taper_cut_connector_fitting(knob_length=15, tube_outer_diameter=6.4, tube_inner_diameter=3.4,
            taper_end_diameter=2.7, taper_length=4,
            threaded_connector:ThreadedConnector =
                ThreadedConnector(diameter=10.1, thread_pitch=0.874)) -> Part:
    """
    Returns a twist snap connector fitting with a tapered path for
    stepping between two internal tube diameters

    Args:
        knob_length: the length of the grip
        tube_outer_diameter: the outer diameter of the tube running through the connector 
                            (you'll want to leave some extra tolerance room)
        tube_inner_diameter: the inner diameter of the tube running through the connector
        taper_end_diameter: the diameter to leave at the end of the measured tube; should match
                            the inner diameter of the corresponding socket's tube
        taper_length: the length of the cone for the taper.
        threaded_connector: a ThreadedConnector object for the screw-in PTFE connector

    Returns:
        a Part ojbect which is a twist snap connector fitting with a tapered path 
        for stepping between two internal tube diameters
    """

    with BuildPart() as assembly:
        add(connector_fitting(knob_length))
        add(tapered_tube_path(external_radius=tube_outer_diameter/2,
                              taper_start_radius=tube_inner_diameter/2,
                              taper_end_radius=taper_end_diameter/2,
                              taper_length=taper_length,
                              length=knob_length+4), mode=Mode.SUBTRACT)
        add(Cylinder(radius=threaded_connector.diameter/2, height=threaded_connector.length,
                     align=(Align.CENTER, Align.CENTER, Align.MIN)),
            mode=Mode.SUBTRACT)

    thread = TrapezoidalThread(
                    diameter=threaded_connector.diameter,
                    pitch=threaded_connector.thread_pitch,
                    length=threaded_connector.length,
                    thread_angle = threaded_connector.thread_angle,
                    external=False,
                    hand="right",
                    align=(Align.CENTER, Align.CENTER, Align.MIN)
                    )
    thread.label = "thread"
    return Part(label="Connector Fitting", children=[
        Part(label="assembly", children=[assembly.part]),
        thread])

scc = straight_cut_connector_fitting()
scs = straight_cut_socket_fitting()
tcs_2mmID = taper_cut_socket_fitting(taper_end_diameter=2.2)
tcs = taper_cut_socket_fitting()

export_step(tcs,'../step/snap-socket-step-down-OD6ID3-OD4ID2.5.step')
export_step(tcs_2mmID,'../step/snap-socket-step-down-OD6ID3-OD4ID2.step')
export_step(scc,'../step/snap-connector-straight-OD4.step')
export_step(scs,'../step/snap-socket-straight-OD4.step')

export_stl(tcs,'../stl/snap-socket-step-down-OD6ID3-OD4ID2.5.stl')
export_stl(tcs_2mmID,'../stl/snap-socket-step-down-OD6ID3-OD4ID2.stl')
export_stl(scc,'../stl/snap-connector-straight-OD4.stl')
export_stl(scs,'../stl/snap-socket-straight-OD4.stl')
show(tcs)
