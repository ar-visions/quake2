# Quake 2 inventory (Oct 5 2026)

Reference: /src/Quake-2, id's GPL release of Dec 21 2001
(github id-Software/Quake-2, commit 372afde). Port target:
/src/quake2, a silver app module `quake2` that imports trinity
and calls it directly. No renderer module, no software or GL
renderer, no 3dfx / PowerVR paths. Trinity does all 3D and UX.

Assets: Steam, /home/kalen/.steam/debian-installation/steamapps/
common/Quake 2. The assets are not in any repo.

## Source, by what we do with it

Port (game and engine logic, 97k lines of C):

| folder   | lines  | what it is                                   |
|----------|--------|----------------------------------------------|
| game/    | 46,874 | the game dll: 48 .c, 26 .h                   |
| ctf/     | 30,462 | the CTF game dll (a variant of game/)        |
| client/  | 24,689 | prediction, entities, effects, sound, input   |
| qcommon/ |  9,085 | files, cvars, commands, net channel, pmove   |
| server/  |  5,939 | the server: world, entities, send, user cmds |

Drop (renderers and platform layers, 56k lines):
ref_soft/ 16,441 (and 22 .s/.asm files), ref_gl/ 10,468,
win32/ 11,994, linux/ 9,706, irix/ 6,687, solaris/ 1,238,
null/ 486. Devices owns the window, input, sound device.

### game/ in detail
- 24 monsters: actor berserk boss2 boss3 boss31 boss32 brain
  chick flash flipper float flyer gladiator gunner hover
  infantry insane medic mutant parasite soldier supertank tank,
  plus m_move.c (monster locomotion).
- AI: g_ai.c (1,117), g_monster.c, m_move.c. This is where the
  new AI goes.
- Rules: g_items (2,216) g_func (2,048, doors, platforms,
  trains) g_misc (1,876) p_client (1,805) p_weapon (1,434)
  p_view (1,087) g_cmds g_spawn g_phys (961) g_weapon g_combat
  g_target g_trigger g_turret g_chase g_save g_utils g_main
  g_svcmds p_hud p_trail, q_shared.c (shared math, 1,418).
- Interface game.h: game_import_t 59 functions (engine
  services the game calls), game_export_t 59 functions (what
  the engine calls into the game). In silver this is one
  module, no dll boundary.

### client/ in detail
cl_main cl_parse cl_ents (1,500) cl_pred cl_fx (2,298)
cl_newfx (1,323) cl_tent (1,745) cl_view cl_scrn (1,401)
cl_input cl_inv cl_cin (cinematics) snd_dma (1,214) snd_mem
snd_mix keys console (682) menu (4,016) qmenu x86.c.
- menu.c, qmenu.c, console.c, cl_scrn.c draw with the old 2D
  pic calls: rebuilt as trinity elements and styles.
- snd_*: the 8-channel software mixer; spectra's AudioMixer
  replaces it, the spatialization math is kept.
- x86.c: drop.

### qcommon/ and server/
cmodel.c (1,770: BSP collision, PVS/PHS) common.c cmd.c
cvar.c files.c (pak reading) net_chan.c pmove.c (1,360:
player movement, shared with the game) crc.c md4.c;
sv_main sv_ccmds sv_ents sv_user sv_world sv_send sv_init
sv_game sv_null. Protocol version 34, 26 svc/clc message ids.
Single player and local games run the server in-process;
the network layer (net_udp) comes with it for multiplayer.

## File formats (qcommon/qfiles.h)
- PAK  "PACK": 64-byte entries, 56-char names.
- BSP  "IBSP" version 38, 19 lumps, lightmaps baked in.
- MD2  "IDP2" version 8: vertex-frame animated models.
- SP2  "IDS2" version 2: sprites.
- WAL: 8-bit paletted wall textures with 4 mip levels; the
  palette is pics/colormap.pcx.
- PCX 8-bit pictures (HUD, menus, console), TGA for a few.
- WAV 8/16-bit, 11/22 kHz. CIN: cinematics (8-bit, with sound).
- DM2 demos, .lst map list, .cfg.
Trinity has gltf, png/jpg, Canvas text and shapes; img reads
images. Readers for PAK, BSP, MD2, SP2, WAL, PCX, CIN and the
palette are new silver code.

## Assets in the Steam install
| dir    | files | MB  | maps | notes                          |
|--------|-------|-----|------|--------------------------------|
| baseq2 | 3,588 | 197 | 47   | 39 campaign + 8 q2dm; 3 paks   |
| xatrix |   832 |  93 | 25   | The Reckoning                  |
| rogue  | 1,983 | 109 | 32   | Ground Zero                    |
| ctf    |   169 |  12 |  5   | CTF                            |
baseq2 by type: 2,378 wal, 546 wav (40 MB), 387 pcx, 119 md2,
60 tga, 47 bsp (104 MB), 8 sp2. Also baseq2/video: 11 .cin
(intro, idlog, 8 unit ends, end); baseq2/players: male female
cyborg crakhor skins and models.
Campaign maps in order: base1 base2 base3 train bunk1 ware1
ware2 jail1-5 security mintro mine1-4 fact1-3 power1 power2
cool1 waste1-3 biggun hangar1 hangar2 lab command strike space
city1-3 boss1 boss2.
The rerelease folder (Q2Game.kpf, quake2ex) is the 2023 KEX
version: not used.

## Trinity owners
- World: BSP faces as trinity meshes, lightmaps as textures,
  PVS culling kept from cmodel; sky box; water/warp surfaces
  as a shader; dynamic lights.
- Models: MD2 frame interpolation in a vertex shader; skins.
- Particles, beams, sprites: trinity instanced draws.
- 2D: HUD, console, menus, inventory as trinity elements.
- Sound: spectra AudioMixer, 3D positions from the client.
- Input, window, timing: devices (via trinity media_app).
