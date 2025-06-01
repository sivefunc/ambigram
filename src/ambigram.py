import cadquery as cq
from cadquery.vis import show

from _version import __version__

def main():
    show(cq.Workplane("XY").text(f"{__version__}", 10, 2))

if __name__ == "__main__":
    main()
