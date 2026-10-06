# quake2

id Software's Quake 2 ported to silver, drawn by trinity.

The game and engine logic come from id's GPL release of the
Quake 2 source (December 21, 2001), copyright id Software.
This port is released under the same license, the GNU General
Public License version 2: see LICENSE.

The renderer is not ported: trinity does all 3D and UX, called
directly from the app. The game assets (pak files) are not in
this repository; the app reads them from an installed copy of
Quake 2 (`--game <path to baseq2>`).

Build and run with silver from this folder:

    silver quake2
    silver quake2 --map base1
    silver quake2 --spawn "x y z yaw pitch"

INVENTORY.md lists what is ported, what is dropped, and the file
formats and assets involved.
