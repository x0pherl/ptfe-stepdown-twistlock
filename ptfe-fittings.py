from build123d import (export_step, export_stl, add,
    BuildPart, Cylinder, Mode, Axis, Circle, Plane, BuildSketch,
    loft, Align, Location, Locations
    )
from bd_warehouse.thread import TrapezoidalThread
from ocp_vscode import show
from twist_snap import TwistSnapConnector

def littlepipe():
    with BuildPart() as small_assembly:
        with BuildPart() as cone:
            with BuildSketch(Plane(origin=(0,0,0), z_dir=(0,0,1))):
                Circle(radius=6)
            with BuildSketch(Plane(origin=(0,0,13), z_dir=(0,0,1))):
                Circle(radius=6.5)
            loft()
        with BuildPart(cone.faces().sort_by(Axis.Z)[-1]) as connector:
            with Locations(Location((0,0,4),(0,180,0))):
                add(TwistSnapConnector(4.5,2).twist_snap_connector.part)
        
        Cylinder(radius=2.25, height=100, mode=Mode.SUBTRACT)
        with BuildPart(cone.faces().sort_by(Axis.Z, reverse=True)[-1], mode=Mode.SUBTRACT) as threadsocket:
            Cylinder(radius=5, height=6.5, align=(Align.CENTER, Align.CENTER, Align.MAX))
        
        with BuildPart(threadsocket.faces().sort_by(Axis.Z)[-1]) as threads:
            TrapezoidalThread(
                diameter=10,
                pitch=1,
                length=6.5,
                thread_angle = 30.0,
                external=False,
                hand="right",
                align=(Align.CENTER, Align.CENTER, Align.MAX)
                )
    return small_assembly

def fatpipe():
    with BuildPart() as large_assembly:
        with BuildPart() as solid:
            with BuildPart() as socket:
                add(TwistSnapConnector(4.5,2).twist_snap_socket.part)

            with BuildPart(socket.faces().sort_by(Axis.Z)[-1]) as cone:
                with BuildSketch(Plane(origin=(0,0,0), z_dir=(0,0,1))):
                    Circle(radius=4.5+4*2/3)
                with BuildSketch(Plane(origin=(0,0,-15), z_dir=(0,0,1))):
                    Circle(radius=6)
                loft()
        with BuildPart(mode=Mode.SUBTRACT):
            with BuildSketch(Plane(origin=(0,0,2), z_dir=(0,0,1))):
                Circle(radius=1.4)
            with BuildSketch(Plane(origin=(0,0,0), z_dir=(0,0,1))):
                Circle(radius=1.7)
            loft()
        with BuildPart(solid.faces().sort_by(Axis.Z, reverse=True)[-1], mode=Mode.SUBTRACT):
            Cylinder(radius=3.25, height=16, align=(Align.CENTER, Align.CENTER, Align.MAX))
        
        with BuildPart(solid.faces().sort_by(Axis.Z, reverse=True)[-1], mode=Mode.SUBTRACT) as threadsocket:
            Cylinder(radius=5.05, height=6.5, align=(Align.CENTER, Align.CENTER, Align.MAX))

        with BuildPart(threadsocket.faces().sort_by(Axis.Z)[-1]) as threads:
            TrapezoidalThread(
                diameter=10.1,
                pitch=0.874,
                length=6.5,
                thread_angle = 30.0,
                external=False,
                hand="right",
                align=(Align.CENTER, Align.CENTER, Align.MAX)
                )
    return large_assembly

big_guy = fatpipe()
little_guy = littlepipe()

show(little_guy)
#show(big_guy)

# export_step(ts.twist_snap_connector.part,'snap-connector.step')
# export_stl(ts.twist_snap_connector.part,'snap-connector.stl')
export_step(big_guy.part,'step/snap-socket.step')
export_stl(big_guy.part,'stl/snap-socket.stl')
export_step(little_guy.part,'step/snap-connector.step')
export_stl(little_guy.part,'stl/snap-connector.stl')
