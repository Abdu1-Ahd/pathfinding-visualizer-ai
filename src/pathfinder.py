import tkinter as tk
from tkinter import ttk
from collections import deque
import heapq
import itertools
import math
import random
import time
import ctypes
import sys


# ═══════════════════════════════════════════════════════════════════════════════
# CELL STATES
# ═══════════════════════════════════════════════════════════════════════════════

EMPTY = 0
WALL  = 1
START = 2
GOAL  = 3

# ═══════════════════════════════════════════════════════════════════════════════
# APP CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

ROWS      = 20
COLS      = 20
DELAY     = 0.015
MET_FREQ  = 5
PANEL_W   = 320

BG_CLR    = "#0F172A"
PNL_BG    = "#1E293B"
TXT_CLR   = "#E2E8F0"
MUT_TXT   = "#94A3B8"
ACC_CLR   = "#2962FF"
BRD_CLR   = "#334155"
HOV_BG    = "#448AFF"
MUT_BTN   = "#334155"

CELL_CLR = {
    "empty":    "#334155",
    "wall":     "#64748B",
    "start":    "#00E676",
    "goal":     "#FF1744",
    "frontier": "#FFD600",
    "explored": "#1565C0",
    "path":     "#00C853",
}

ALGOS = [
    "BFS", "DFS", "UCS", "DLS", "IDDFS",
    "Bidirectional BFS", "A*", "GBFS",
]
HEURS = ["Manhattan", "Euclidean"]

# ═══════════════════════════════════════════════════════════════════════════════
# DIRECTIONS
# ═══════════════════════════════════════════════════════════════════════════════

DIRS_4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIRS_8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]


# ═══════════════════════════════════════════════════════════════════════════════
# GRID
# ═══════════════════════════════════════════════════════════════════════════════

class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cells = [[EMPTY] * cols for _ in range(rows)]
        self.start = None
        self.goal = None

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_wall(self, r, c):
        return self.in_bounds(r, c) and self.cells[r][c] == WALL

    def is_passable(self, r, c):
        return self.in_bounds(r, c) and self.cells[r][c] != WALL

    def place_start(self, r, c):
        if self.start:
            self.cells[self.start[0]][self.start[1]] = EMPTY
        self.start = (r, c)
        self.cells[r][c] = START

    def place_goal(self, r, c):
        if self.goal:
            self.cells[self.goal[0]][self.goal[1]] = EMPTY
        self.goal = (r, c)
        self.cells[r][c] = GOAL

    def get_nbrs(self, r, c, dirs=None):
        if dirs is None:
            dirs = DIRS_4
        nbrs = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if not self.is_passable(nr, nc):
                continue
            if dr != 0 and dc != 0:
                if self.is_wall(r + dr, c) or self.is_wall(r, c + dc):
                    continue
            nbrs.append((nr, nc))
        return nbrs

    def wall_count(self):
        return sum(1 for r in range(self.rows) for c in range(self.cols) if self.cells[r][c] == WALL)

    def reset(self):
        self.cells = [[EMPTY] * self.cols for _ in range(self.rows)]
        self.start = None
        self.goal = None


# ═══════════════════════════════════════════════════════════════════════════════
# HEURISTICS
# ═══════════════════════════════════════════════════════════════════════════════

def h_manhattan(r1, c1, r2, c2):
    return abs(r1 - r2) + abs(c1 - c2)

def h_euclidean(r1, c1, r2, c2):
    return math.hypot(r1 - r2, c1 - c2)


# ═══════════════════════════════════════════════════════════════════════════════
# PATH TRACER
# ═══════════════════════════════════════════════════════════════════════════════

def _trace(parent, target):
    path = []
    nd = target
    while nd in parent:
        path.append(nd)
        nd = parent[nd]
    path.reverse()
    return path


def _draw_path(gui, path, target):
    for r, c in path:
        if (r, c) != target:
            gui.update_cell(r, c, "path")
            gui.anim_step()


# ═══════════════════════════════════════════════════════════════════════════════
# BFS
# ═══════════════════════════════════════════════════════════════════════════════

def run_bfs(grid, gui):
    s, t = grid.start, grid.goal
    if not s or not t:
        gui.set_status("Start or goal not set.")
        return

    q = deque([s])
    vis = {s}
    par = {}
    found = False
    n_exp = 0
    gui.set_status("BFS: Searching...")

    while q and not found:
        r, c = q.popleft()
        n_exp += 1
        if (r, c) != s:
            gui.update_cell(r, c, "explored")
            gui.anim_step()
        for nr, nc in grid.get_nbrs(r, c):
            if (nr, nc) in vis:
                continue
            vis.add((nr, nc))
            par[(nr, nc)] = (r, c)
            if (nr, nc) == t:
                found = True
                break
            gui.update_cell(nr, nc, "frontier")
            gui.anim_step()
            q.append((nr, nc))

    if found:
        path = _trace(par, t)
        _draw_path(gui, path, t)
        gui.set_status(f"Done! Path length: {len(path)} steps.")
    else:
        gui.set_status("No path found.")
    
    return n_exp


# ═══════════════════════════════════════════════════════════════════════════════
# DFS
# ═══════════════════════════════════════════════════════════════════════════════

def run_dfs(grid, gui):
    s, t = grid.start, grid.goal
    if not s or not t:
        gui.set_status("Start or goal not set.")
        return

    stk = [s]
    vis = {s}
    par = {}
    found = False
    n_exp = 0
    gui.set_status("DFS: Searching...")

    while stk and not found:
        r, c = stk.pop()
        n_exp += 1
        if (r, c) != s:
            gui.update_cell(r, c, "explored")
            gui.anim_step()
        for nr, nc in grid.get_nbrs(r, c):
            if (nr, nc) in vis:
                continue
            vis.add((nr, nc))
            par[(nr, nc)] = (r, c)
            if (nr, nc) == t:
                found = True
                break
            gui.update_cell(nr, nc, "frontier")
            gui.anim_step()
            stk.append((nr, nc))

    if found:
        path = _trace(par, t)
        _draw_path(gui, path, t)
        gui.set_status(f"Done! Path length: {len(path)} steps.")
    else:
        gui.set_status("No path found.")

    return n_exp


# ═══════════════════════════════════════════════════════════════════════════════
# UCS
# ═══════════════════════════════════════════════════════════════════════════════

def run_ucs(grid, gui):
    s, t = grid.start, grid.goal
    if not s or not t:
        gui.set_status("Start or goal not set.")
        return

    heap = [(0, s[0], s[1])]
    vis = set()
    par = {}
    g_cost = {s: 0}
    found = False
    n_exp = 0
    gui.set_status("UCS: Searching...")

    while heap and not found:
        cost, r, c = heapq.heappop(heap)
        if (r, c) in vis:
            continue
        vis.add((r, c))
        n_exp += 1
        if (r, c) != s:
            gui.update_cell(r, c, "explored")
            gui.anim_step()
        for nr, nc in grid.get_nbrs(r, c):
            if (nr, nc) in vis:
                continue
            nc_cost = cost + 1
            if nc_cost < g_cost.get((nr, nc), float("inf")):
                g_cost[(nr, nc)] = nc_cost
                par[(nr, nc)] = (r, c)
                if (nr, nc) == t:
                    found = True
                    break
                gui.update_cell(nr, nc, "frontier")
                gui.anim_step()
                heapq.heappush(heap, (nc_cost, nr, nc))

    if found:
        path = _trace(par, t)
        _draw_path(gui, path, t)
        gui.set_status(f"Done! Path: {len(path)} steps. Cost: {g_cost[t]}.")
    else:
        gui.set_status("No path found.")

    return n_exp


# ═══════════════════════════════════════════════════════════════════════════════
# DLS
# ═══════════════════════════════════════════════════════════════════════════════

def run_dls(grid, gui, lim=40):
    s, t = grid.start, grid.goal
    if not s or not t:
        gui.set_status("Start or goal not set.")
        return

    vis = set()
    par = {}
    found = False
    cnt = 0
    n_exp = 0
    gui.set_status(f"DLS: Searching (limit={lim})...")
    stk = [(s[0], s[1], 0)]

    while stk and not found:
        r, c, d = stk.pop()
        if d > lim:
            continue
        if (r, c) in vis:
            continue
        vis.add((r, c))
        n_exp += 1
        if (r, c) != s:
            gui.update_cell(r, c, "explored")
            cnt += 1
            if cnt % 4 == 0:
                gui.anim_step()
            else:
                gui._root.update_idletasks()
        if (r, c) == t:
            found = True
            break
        if d == lim:
            continue
        for nr, nc in grid.get_nbrs(r, c):
            if (nr, nc) in vis:
                continue
            par[(nr, nc)] = (r, c)
            if (nr, nc) == t:
                found = True
                break
            gui.update_cell(nr, nc, "frontier")
            cnt += 1
            if cnt % 4 == 0:
                gui.anim_step()
            stk.append((nr, nc, d + 1))

    gui._root.update()
    if found:
        path = _trace(par, t)
        _draw_path(gui, path, t)
        gui.set_status(f"Done! Path: {len(path)} steps (limit={lim}).")
    else:
        gui.set_status(f"No path found within depth {lim}.")

    return n_exp


# ═══════════════════════════════════════════════════════════════════════════════
# IDDFS
# ═══════════════════════════════════════════════════════════════════════════════

def _dls_inner(grid, gui, lim):
    s, t = grid.start, grid.goal
    vis = set()
    par = {}
    found = False
    cnt = 0
    n_exp = 0
    stk = [(s[0], s[1], 0)]

    while stk and not found:
        r, c, d = stk.pop()
        if d > lim:
            continue
        if (r, c) in vis:
            continue
        vis.add((r, c))
        n_exp += 1
        if (r, c) != s:
            gui.update_cell(r, c, "explored")
            cnt += 1
            if cnt % 4 == 0:
                gui.anim_step()
            else:
                gui._root.update_idletasks()
        if (r, c) == t:
            found = True
            break
        if d == lim:
            continue
        for nr, nc in grid.get_nbrs(r, c):
            if (nr, nc) in vis:
                continue
            par[(nr, nc)] = (r, c)
            if (nr, nc) == t:
                found = True
                break
            gui.update_cell(nr, nc, "frontier")
            cnt += 1
            if cnt % 4 == 0:
                gui.anim_step()
            stk.append((nr, nc, d + 1))

    gui._root.update()
    return found, par, n_exp


def run_iddfs(grid, gui, max_d=50):
    s, t = grid.start, grid.goal
    if not s or not t:
        gui.set_status("Start or goal not set.")
        return
    
    total_exp = 0

    for lim in range(max_d + 1):
        gui.set_status(f"IDDFS: depth limit = {lim}...")
        for r in range(grid.rows):
            for c in range(grid.cols):
                st = gui._grid_state[r][c]
                if st in ("explored", "frontier", "path"):
                    gui.update_cell(r, c, "empty")
        gui.update_cell(*s, "start")
        gui.update_cell(*t, "goal")
        gui.anim_step()

        found, par, n_exp = _dls_inner(grid, gui, lim)
        total_exp += n_exp
        if found:
            path = _trace(par, t)
            _draw_path(gui, path, t)
            gui.set_status(f"Done! Path: {len(path)} steps (depth={lim}).")
            return total_exp

    gui.set_status(f"No path found within max depth {max_d}.")
    return total_exp


# ═══════════════════════════════════════════════════════════════════════════════
# BIDIRECTIONAL BFS
# ═══════════════════════════════════════════════════════════════════════════════

def run_bidir_bfs(grid, gui):
    s, t = grid.start, grid.goal
    if not s or not t:
        gui.set_status("Start or goal not set.")
        return
    if s == t:
        gui.set_status("Start and goal are the same.")
        return

    fq = deque([s])
    fv = {s: None}
    bq = deque([t])
    bv = {t: None}
    meet = None
    found = False
    n_exp = 0
    gui.set_status("Bidirectional BFS: Searching...")

    while (fq or bq) and not found:
        if fq and not found:
            r, c = fq.popleft()
            n_exp += 1
            if (r, c) != s:
                gui.update_cell(r, c, "explored")
                gui.anim_step()
            for nr, nc in grid.get_nbrs(r, c):
                if (nr, nc) in fv:
                    continue
                fv[(nr, nc)] = (r, c)
                if (nr, nc) in bv:
                    meet = (nr, nc)
                    found = True
                    break
                gui.update_cell(nr, nc, "frontier")
                gui.anim_step()
                fq.append((nr, nc))

        if bq and not found:
            r, c = bq.popleft()
            n_exp += 1
            if (r, c) != t:
                gui.update_cell(r, c, "explored")
                gui.anim_step()
            for nr, nc in grid.get_nbrs(r, c):
                if (nr, nc) in bv:
                    continue
                bv[(nr, nc)] = (r, c)
                if (nr, nc) in fv:
                    meet = (nr, nc)
                    found = True
                    break
                gui.update_cell(nr, nc, "frontier")
                gui.anim_step()
                bq.append((nr, nc))

    if not found:
        gui.set_status("No path found.")
        return n_exp

    gui.update_cell(*meet, "path")
    gui.anim_step()

    fp = []
    nd = meet
    while fv.get(nd) is not None:
        nd = fv[nd]
        fp.append(nd)
    fp.reverse()

    bp = []
    nd = meet
    while bv.get(nd) is not None:
        nd = bv[nd]
        bp.append(nd)

    full = fp + [meet] + bp
    for r, c in full:
        if (r, c) in (s, t):
            continue
        gui.update_cell(r, c, "path")
        gui.anim_step()

    gui.set_status(f"Done! Path: {len(full) - 1} steps. Meeting: {meet}.")
    return n_exp


# ═══════════════════════════════════════════════════════════════════════════════
# A* SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

def run_astar(grid, heur_fn, dirs, on_exp, on_frt):
    s, t = grid.start, grid.goal
    if not s or not t:
        return None, 0
    if s == t:
        return [s], 0

    gr, gc = t
    g_cost = {s: 0.0}
    par = {}
    closed = set()
    ctr = itertools.count()
    heap = [(heur_fn(s[0], s[1], gr, gc), next(ctr), s[0], s[1])]
    n_exp = 0

    while heap:
        _, _, r, c = heapq.heappop(heap)
        nd = (r, c)
        if nd in closed:
            continue
        closed.add(nd)
        n_exp += 1
        if on_exp and nd != s:
            on_exp(r, c)
        if nd == t:
            path = []
            cur = t
            while cur in par:
                path.append(cur)
                cur = par[cur]
            path.append(s)
            path.reverse()
            return path, n_exp
        gn = g_cost[nd]
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            nb = (nr, nc)
            if nb in closed or not grid.is_passable(nr, nc):
                continue
            if dr != 0 and dc != 0:
                if grid.is_wall(r + dr, c) or grid.is_wall(r, c + dc):
                    continue
            tg = gn + math.hypot(dr, dc)
            if tg < g_cost.get(nb, math.inf):
                g_cost[nb] = tg
                par[nb] = nd
                h = heur_fn(nr, nc, gr, gc)
                heapq.heappush(heap, (tg + h, next(ctr), nr, nc))
                if on_frt and nb != t:
                    on_frt(nr, nc)
    return None, n_exp


# ═══════════════════════════════════════════════════════════════════════════════
# GBFS SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

def run_gbfs(grid, heur_fn, on_exp, on_frt):
    s, t = grid.start, grid.goal
    if not s or not t:
        return None, 0
    if s == t:
        return [s], 0

    gr, gc = t
    ctr = itertools.count()
    heap = [(heur_fn(s[0], s[1], gr, gc), next(ctr), s[0], s[1])]
    in_heap = {s}
    vis = set()
    par = {s: None}
    n_exp = 0

    while heap:
        _, _, r, c = heapq.heappop(heap)
        nd = (r, c)
        if nd in vis:
            continue
        vis.add(nd)
        n_exp += 1
        if on_exp and nd != s:
            on_exp(r, c)
        if nd == t:
            path = []
            cur = t
            while cur is not None:
                path.append(cur)
                cur = par.get(cur)
            path.reverse()
            return path, n_exp
        for dr, dc in DIRS_4:
            nr, nc = r + dr, c + dc
            nb = (nr, nc)
            if nb in vis or nb in in_heap or not grid.is_passable(nr, nc):
                continue
            in_heap.add(nb)
            par[nb] = nd
            h = heur_fn(nr, nc, gr, gc)
            heapq.heappush(heap, (h, next(ctr), nr, nc))
            if on_frt and nb != t:
                on_frt(nr, nc)
    return None, n_exp


# ═══════════════════════════════════════════════════════════════════════════════
# ALGORITHM REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

UNINFORMED = {
    "BFS":                run_bfs,
    "DFS":                run_dfs,
    "UCS":                run_ucs,
    "DLS":                run_dls,
    "IDDFS":              run_iddfs,
    "Bidirectional BFS":  run_bidir_bfs,
}


# ═══════════════════════════════════════════════════════════════════════════════
# MAP GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

_MAX_DENS = 0.65
_MAX_TRIES = 10
_DENS_DECAY = 0.10

def _connected(grid):
    s, t = grid.start, grid.goal
    if not s or not t:
        return False
    q = deque([s])
    vis = {s}
    while q:
        r, c = q.popleft()
        if (r, c) == t:
            return True
        for dr, dc in DIRS_4:
            nr, nc = r + dr, c + dc
            nb = (nr, nc)
            if nb not in vis and grid.is_passable(nr, nc):
                vis.add(nb)
                q.append(nb)
    return False

def _gen_map(grid, dens, seed=None):
    if not grid.start or not grid.goal:
        return False
    dens = min(max(0.0, dens), _MAX_DENS)
    rng = random.Random(seed)
    fixed = {grid.start, grid.goal}
    cands = [(r, c) for r in range(grid.rows) for c in range(grid.cols) if (r, c) not in fixed]
    if not cands:
        return True
    best = None
    eff = dens
    for _ in range(_MAX_TRIES):
        for r, c in cands:
            grid.cells[r][c] = EMPTY
        wc = round(len(cands) * eff)
        rng.shuffle(cands)
        for r, c in cands[:wc]:
            grid.cells[r][c] = WALL
        if _connected(grid):
            return True
        if best is None:
            best = [row[:] for row in grid.cells]
        eff = max(0.0, eff - _DENS_DECAY)
    if best:
        for r in range(grid.rows):
            for c in range(grid.cols):
                grid.cells[r][c] = best[r][c]
    return False

def gen_sparse(grid, seed=None):
    return _gen_map(grid, 0.20, seed)

def gen_moderate(grid, seed=None):
    return _gen_map(grid, 0.40, seed)

def gen_dense(grid, seed=None):
    return _gen_map(grid, 0.60, seed)


# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMIC SPAWNER
# ═══════════════════════════════════════════════════════════════════════════════

_MAX_SPAWN_P = 0.30
_DEF_SPAWN_P = 0.05

class DynSpawner:
    def __init__(self, grid, prob=_DEF_SPAWN_P, draw_fn=None, seed=None, on=True):
        self._g = grid
        self._rng = random.Random(seed)
        self._draw = draw_fn or (lambda r, c: None)
        self._spawned = set()
        self.prob = min(max(0.0, prob), _MAX_SPAWN_P)
        self.on = on

    def tick(self, agent_pos):
        if not self.on or self._rng.random() >= self.prob:
            return None
        cands = self._cands(agent_pos)
        if not cands:
            return None
        r, c = self._rng.choice(cands)
        self._g.cells[r][c] = WALL
        self._spawned.add((r, c))
        self._draw(r, c)
        return (r, c)

    def clear(self):
        for r, c in self._spawned:
            if self._g.cells[r][c] == WALL:
                self._g.cells[r][c] = EMPTY
        self._spawned.clear()

    def _cands(self, agent_pos):
        bad = {agent_pos}
        if self._g.goal:
            bad.add(self._g.goal)
        if self._g.start:
            bad.add(self._g.start)
        return [(r, c) for r in range(self._g.rows) for c in range(self._g.cols)
                if self._g.cells[r][c] == EMPTY and (r, c) not in bad]


# ═══════════════════════════════════════════════════════════════════════════════
# RE-PLANNER
# ═══════════════════════════════════════════════════════════════════════════════

class RePlanner:
    def __init__(self, grid, algo="astar", heur="manhattan"):
        self._g = grid
        self._algo = algo.lower().strip()
        self._heur = heur.lower().strip()
        self._path = []
        self._pset = set()

    def plan(self):
        path, nodes = self._search(self._g.start)
        self._set_path(path)
        return path, nodes

    def obstacle_hit(self, wall, agent_pos):
        if wall not in self._pset:
            return self._path, False, 0
        path, nodes = self._search(agent_pos)
        self._set_path(path)
        return path, True, nodes

    def advance(self, pos):
        if pos not in self._pset:
            return
        try:
            idx = self._path.index(pos)
        except ValueError:
            return
        rm = self._path[:idx + 1]
        self._path = self._path[idx + 1:]
        self._pset.difference_update(rm)

    def set_algo(self, algo):
        self._algo = algo.lower().strip()

    def set_heur(self, heur):
        self._heur = heur.lower().strip()

    def _set_path(self, path):
        if path:
            self._path = list(path)
            self._pset = set(path)
        else:
            self._path = []
            self._pset = set()

    def _search(self, src):
        if not src or not self._g.goal:
            return None, 0
        hfn = h_manhattan if self._heur == "manhattan" else h_euclidean
        orig_s = self._g.start
        orig_c = self._g.cells[src[0]][src[1]]
        try:
            self._g.start = src
            if orig_c != START:
                self._g.cells[src[0]][src[1]] = START
            if self._algo in ("astar", "a*"):
                dirs = DIRS_8 if self._heur == "euclidean" else DIRS_4
                return run_astar(self._g, hfn, dirs, None, None)
            else:
                return run_gbfs(self._g, hfn, None, None)
        finally:
            self._g.start = orig_s
            if orig_c != START:
                self._g.cells[src[0]][src[1]] = orig_c
            if orig_s and orig_s != src:
                self._g.cells[orig_s[0]][orig_s[1]] = START


# ═══════════════════════════════════════════════════════════════════════════════
# METRICS PANEL
# ═══════════════════════════════════════════════════════════════════════════════

class MetricsPanel(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=PNL_BG, **kw)
        self._nv = tk.StringVar(value="—")
        self._cv = tk.StringVar(value="—")
        self._tv = tk.StringVar(value="—")
        self._build()

    def _build(self):
        tk.Label(self, text="📊 Metrics", fg=TXT_CLR, bg=PNL_BG,
                 font=("Segoe UI", 11, "bold"), anchor="w").pack(fill=tk.X, pady=(0, 6))
        tk.Frame(self, bg=BRD_CLR, height=2).pack(fill=tk.X, pady=(0, 8))
        self._row("Nodes Visited", self._nv, CELL_CLR["explored"])
        self._row("Path Cost", self._cv, CELL_CLR["path"])
        self._row("Time (ms)", self._tv, "#FF6F00")

    def _row(self, lbl, var, dot_clr):
        f = tk.Frame(self, bg=PNL_BG)
        f.pack(fill=tk.X, pady=3)
        tk.Label(f, text="●", fg=dot_clr, bg=PNL_BG, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(f, text=lbl, fg=MUT_TXT, bg=PNL_BG, font=("Segoe UI", 9), anchor="w").pack(side=tk.LEFT)
        tk.Label(f, textvariable=var, fg=TXT_CLR, bg=PNL_BG, font=("Segoe UI", 9, "bold"), anchor="e").pack(side=tk.RIGHT)

    def set_nodes(self, n):
        self._nv.set(f"{n:,}")

    def set_cost(self, c):
        self._cv.set(str(c) if c is not None else "—")

    def set_time(self, ms):
        self._tv.set(f"{ms:.1f}")

    def reset(self):
        self._nv.set("—")
        self._cv.set("—")
        self._tv.set("—")


# ═══════════════════════════════════════════════════════════════════════════════
# PATHFINDER APP
# ═══════════════════════════════════════════════════════════════════════════════

class PathfinderApp:
    def __init__(self, root):
        self._root = root
        self._root.title("AI Pathfinder — Search Algorithm Visualizer")
        self._root.configure(bg=BG_CLR)
        self._root.resizable(True, True)

        scr_w = self._root.winfo_screenwidth()
        scr_h = self._root.winfo_screenheight()
        use_w = int(scr_w * 0.85) - PANEL_W - 16
        use_h = int(scr_h * 0.85) - 60
        self._csz = max(min(use_w // COLS, use_h // ROWS), 10)

        self._grid = Grid(ROWS, COLS)
        self._grid.place_start(0, 0)
        self._grid.place_goal(ROWS - 1, COLS - 1)

        self._grid_state = [["empty"] * COLS for _ in range(ROWS)]
        self._cells = {}
        self._running = False
        self._rsz_flag = False
        self._n_vis = 0
        self._step_ctr = 0
        self._t0 = 0.0
        self._last_path = None

        main = tk.Frame(self._root, bg=BG_CLR)
        main.pack(fill=tk.BOTH, expand=True)

        self._build_panel(main)
        self._build_canvas(main)

        self._canvas.bind("<Button-1>", self._on_click)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<Configure>", self._on_canvas_rsz)
        self._repaint()

    # ── Canvas ────────────────────────────────────────────────────────────────

    def _build_canvas(self, parent):
        fr = tk.Frame(parent, bg=BG_CLR, padx=8, pady=8)
        fr.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._canvas = tk.Canvas(fr, width=COLS * self._csz, height=ROWS * self._csz,
                                 bg=BG_CLR, highlightthickness=2, highlightbackground=BRD_CLR)
        self._canvas.pack(fill=tk.BOTH, expand=True)
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c * self._csz, r * self._csz
                rid = self._canvas.create_rectangle(x1, y1, x1 + self._csz, y1 + self._csz,
                                                    fill=CELL_CLR["empty"], outline=BG_CLR, width=1)
                self._cells[(r, c)] = rid

    # ── Side Panel ────────────────────────────────────────────────────────────

    def _build_panel(self, parent):
        pnl = tk.Frame(parent, bg=PNL_BG, width=PANEL_W)
        pnl.pack(side=tk.RIGHT, fill=tk.Y)
        pnl.pack_propagate(False)

        px = dict(padx=14)

        tk.Label(pnl, text="⚙  Controls", fg=TXT_CLR, bg=PNL_BG,
                 font=("Segoe UI", 14, "bold"), anchor="w").pack(fill=tk.X, pady=(16, 0), **px)
        tk.Frame(pnl, bg=BRD_CLR, height=2).pack(fill=tk.X, pady=(10, 12), **px)

        tk.Label(pnl, text="Algorithm", fg=MUT_TXT, bg=PNL_BG,
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill=tk.X, pady=(0, 3), **px)
        self._algo_var = tk.StringVar(value="BFS")
        self._algo_cb = ttk.Combobox(pnl, textvariable=self._algo_var, values=ALGOS,
                                     state="readonly", font=("Segoe UI", 10))
        self._algo_cb.pack(fill=tk.X, pady=(0, 10), **px)
        self._algo_cb.bind("<<ComboboxSelected>>", self._on_algo_change)

        tk.Label(pnl, text="Heuristic", fg=MUT_TXT, bg=PNL_BG,
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill=tk.X, pady=(0, 3), **px)
        self._heur_var = tk.StringVar(value="Manhattan")
        self._heur_cb = ttk.Combobox(pnl, textvariable=self._heur_var, values=HEURS,
                                     state="disabled", font=("Segoe UI", 10))
        self._heur_cb.pack(fill=tk.X, pady=(0, 10), **px)

        tk.Frame(pnl, bg=BRD_CLR, height=2).pack(fill=tk.X, pady=(0, 10), **px)

        self._dyn_var = tk.BooleanVar(value=False)
        tk.Checkbutton(pnl, text="Dynamic Mode", variable=self._dyn_var,
                       fg=TXT_CLR, bg=PNL_BG, activeforeground=TXT_CLR, activebackground=PNL_BG,
                       selectcolor=BRD_CLR, font=("Segoe UI", 9), anchor="w", cursor="hand2",
                       relief="flat").pack(fill=tk.X, pady=(0, 2), **px)
        tk.Label(pnl, text="Re-runs search live as you draw walls.",
                 fg=MUT_TXT, bg=PNL_BG, font=("Segoe UI", 8, "italic"),
                 anchor="w").pack(fill=tk.X, pady=(0, 10), **px)

        tk.Frame(pnl, bg=BRD_CLR, height=2).pack(fill=tk.X, pady=(0, 10), **px)

        btn_pr = dict(bg=ACC_CLR, fg="#FFF", activebackground=HOV_BG, activeforeground="#FFF",
                      font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=12, pady=8)
        self._btn_start = tk.Button(pnl, text="▶  Start Search", command=self._run_search, **btn_pr)
        self._btn_start.pack(fill=tk.X, pady=(0, 8), **px)

        btn_mt = dict(bg=MUT_BTN, fg=TXT_CLR, activebackground="#475569", activeforeground=TXT_CLR,
                      font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=6, pady=5)
        gf = tk.Frame(pnl, bg=PNL_BG)
        gf.pack(fill=tk.X, pady=(0, 6), **px)
        for lbl, fn in [("Sparse", gen_sparse), ("Moderate", gen_moderate), ("Dense", gen_dense)]:
            tk.Button(gf, text=lbl, command=lambda f=fn: self._apply_map(f), **btn_mt
                      ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        self._btn_reset = tk.Button(pnl, text="↺  Reset Grid", command=self._reset_grid, **btn_mt)
        self._btn_reset.pack(fill=tk.X, pady=(0, 10), **px)

        tk.Frame(pnl, bg=BRD_CLR, height=2).pack(fill=tk.X, pady=(0, 10), **px)

        self._metrics = MetricsPanel(pnl)
        self._metrics.pack(fill=tk.X, pady=(0, 10), **px)

        tk.Frame(pnl, bg=BRD_CLR, height=2).pack(fill=tk.X, pady=(0, 6), **px)

        tk.Label(pnl, text="Legend", fg=MUT_TXT, bg=PNL_BG,
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill=tk.X, pady=(0, 4), **px)
        for txt, key in [("Start", "start"), ("Goal", "goal"), ("Wall", "wall"),
                         ("Frontier", "frontier"), ("Explored", "explored"), ("Path", "path")]:
            rf = tk.Frame(pnl, bg=PNL_BG)
            rf.pack(fill=tk.X, pady=2, **px)
            tk.Label(rf, bg=CELL_CLR[key], width=2, height=1, relief="flat").pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(rf, text=txt, fg=TXT_CLR, bg=PNL_BG, font=("Segoe UI", 9), anchor="w").pack(side=tk.LEFT)

        spacer = tk.Frame(pnl, bg=PNL_BG)
        spacer.pack(expand=True, fill=tk.BOTH)
        tk.Frame(pnl, bg=BRD_CLR, height=2).pack(fill=tk.X, pady=(0, 6), **px)
        self._status_var = tk.StringVar(value="Select algorithm, then press Start.")
        tk.Label(pnl, textvariable=self._status_var, fg=MUT_TXT, bg=PNL_BG,
                 font=("Segoe UI", 8), wraplength=PANEL_W - 36, justify="left",
                 anchor="w").pack(fill=tk.X, pady=(0, 14), **px)

        self._apply_cb_style()

    def _on_algo_change(self, e=None):
        if self._algo_var.get() in ("A*", "GBFS"):
            self._heur_cb.config(state="readonly")
        else:
            self._heur_cb.config(state="disabled")

    @staticmethod
    def _apply_cb_style():
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TCombobox", fieldbackground=BRD_CLR, background=BRD_CLR,
                    foreground=TXT_CLR, selectbackground=ACC_CLR, selectforeground="#FFF",
                    bordercolor=BRD_CLR, arrowcolor=TXT_CLR)
        s.map("TCombobox", fieldbackground=[("readonly", BRD_CLR)], foreground=[("readonly", TXT_CLR)])

    # ── Paint helpers ─────────────────────────────────────────────────────────

    def update_cell(self, r, c, state):
        self._grid_state[r][c] = state
        self._canvas.itemconfig(self._cells[(r, c)], fill=CELL_CLR[state])

    def anim_step(self):
        self._root.update()
        time.sleep(DELAY)

    def set_status(self, txt):
        self._status_var.set(txt)
        self._root.update()

    def _repaint(self):
        sm = {EMPTY: "empty", WALL: "wall", START: "start", GOAL: "goal"}
        for r in range(ROWS):
            for c in range(COLS):
                st = sm.get(self._grid.cells[r][c], "empty")
                self._grid_state[r][c] = st
                self._canvas.itemconfig(self._cells[(r, c)], fill=CELL_CLR[st])

    # ── Metrics helpers ───────────────────────────────────────────────────────

    def _reset_metrics(self):
        self._n_vis = 0
        self._step_ctr = 0
        self._t0 = 0.0
        self._metrics.reset()

    def _flush_metrics(self, ms, nodes):
        self._metrics.set_nodes(nodes)
        self._metrics.set_time(ms)

    # ── Search visuals ────────────────────────────────────────────────────────

    def _clear_visuals(self):
        sm = {EMPTY: "empty", WALL: "wall", START: "start", GOAL: "goal"}
        for r in range(ROWS):
            for c in range(COLS):
                if self._grid_state[r][c] in ("explored", "frontier", "path"):
                    st = sm.get(self._grid.cells[r][c], "empty")
                    self._grid_state[r][c] = st
                    self._canvas.itemconfig(self._cells[(r, c)], fill=CELL_CLR[st])
        self._reset_metrics()

    # ── Wall editing ──────────────────────────────────────────────────────────

    def _px_to_cell(self, x, y):
        r, c = y // self._csz, x // self._csz
        if 0 <= r < ROWS and 0 <= c < COLS:
            return r, c
        return None

    def _toggle_wall(self, r, c):
        if (r, c) in (self._grid.start, self._grid.goal):
            return
        if self._grid.cells[r][c] == WALL:
            self._grid.cells[r][c] = EMPTY
            self._grid_state[r][c] = "empty"
            self._canvas.itemconfig(self._cells[(r, c)], fill=CELL_CLR["empty"])
        else:
            self._grid.cells[r][c] = WALL
            self._grid_state[r][c] = "wall"
            self._canvas.itemconfig(self._cells[(r, c)], fill=CELL_CLR["wall"])
        if self._dyn_var.get() and not self._running:
            self._run_search()

    def _place_wall(self, r, c):
        if (r, c) in (self._grid.start, self._grid.goal):
            return
        if self._grid.cells[r][c] != WALL:
            self._grid.cells[r][c] = WALL
            self._grid_state[r][c] = "wall"
            self._canvas.itemconfig(self._cells[(r, c)], fill=CELL_CLR["wall"])
            if self._dyn_var.get() and not self._running:
                self._run_search()

    def _on_click(self, e):
        if self._running:
            return
        cell = self._px_to_cell(e.x, e.y)
        if cell:
            self._toggle_wall(*cell)

    def _on_drag(self, e):
        if self._running:
            return
        cell = self._px_to_cell(e.x, e.y)
        if cell:
            self._place_wall(*cell)

    def _on_canvas_rsz(self, e):
        if self._rsz_flag:
            return
        self._rsz_flag = True
        self._root.after(120, lambda: self._do_rsz(e.width, e.height))

    def _do_rsz(self, w, h):
        self._rsz_flag = False
        nsz = max(min(w // COLS, h // ROWS), 10)
        if nsz == self._csz:
            return
        self._csz = nsz
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c * self._csz, r * self._csz
                self._canvas.coords(self._cells[(r, c)], x1, y1, x1 + self._csz, y1 + self._csz)

    # ── Grid ops ──────────────────────────────────────────────────────────────

    def _apply_map(self, fn):
        if self._running:
            return
        fn(self._grid)
        self._repaint()
        self._reset_metrics()
        self._last_path = None
        self._status_var.set("Map generated. Press Start.")

    def _reset_grid(self):
        if self._running:
            return
        self._grid.reset()
        self._grid.place_start(0, 0)
        self._grid.place_goal(ROWS - 1, COLS - 1)
        self._grid_state = [["empty"] * COLS for _ in range(ROWS)]
        self._repaint()
        self._reset_metrics()
        self._last_path = None
        self._status_var.set("Grid reset. Draw walls and press Start.")

    def _set_ctrls(self, on):
        st = tk.NORMAL if on else tk.DISABLED
        self._btn_start.config(state=st)
        self._btn_reset.config(state=st)
        
        cb = "readonly" if on else "disabled"
        self._algo_cb.config(state=cb)
        
        if on and self._algo_var.get() in ("A*", "GBFS"):
            self._heur_cb.config(state="readonly")
        else:
            self._heur_cb.config(state="disabled")

    # ── Search execution ──────────────────────────────────────────────────────

    def _run_search(self):
        if self._running:
            return
        self._running = True
        self._clear_visuals()
        self._set_ctrls(False)

        algo = self._algo_var.get()
        heur = self._heur_var.get()
        hfn = h_manhattan if heur == "Manhattan" else h_euclidean
        dirs = DIRS_8 if (algo == "A*" and heur == "Euclidean") else DIRS_4

        n_exp = [0]
        s_ctr = [0]
        t0 = time.perf_counter()

        def on_exp(r, c):
            cur = self._grid_state[r][c]
            if cur not in ("start", "goal"):
                self._grid_state[r][c] = "explored"
                self._canvas.itemconfig(self._cells[(r, c)], fill=CELL_CLR["explored"])
            n_exp[0] += 1
            s_ctr[0] += 1
            if s_ctr[0] % MET_FREQ == 0:
                self._metrics.set_nodes(n_exp[0])
                self._metrics.set_time((time.perf_counter() - t0) * 1000)
            self._root.update()
            time.sleep(DELAY)

        def on_frt(r, c):
            cur = self._grid_state[r][c]
            if cur not in ("explored", "start", "goal", "frontier"):
                self._grid_state[r][c] = "frontier"
                self._canvas.itemconfig(self._cells[(r, c)], fill=CELL_CLR["frontier"])

        self._status_var.set(f"Running {algo}...")
        self._root.update_idletasks()

        if algo in UNINFORMED:
            try:
                n_exp_total = UNINFORMED[algo](self._grid, self)
            finally:
                elapsed = (time.perf_counter() - t0) * 1000
                self._flush_metrics(elapsed, n_exp_total or 0)
                self._running = False
                self._set_ctrls(True)
            return

        if algo == "A*":
            path, total = run_astar(self._grid, hfn, dirs, on_exp, on_frt)
        else:
            path, total = run_gbfs(self._grid, hfn, on_exp, on_frt)

        elapsed = (time.perf_counter() - t0) * 1000
        self._last_path = path
        self._flush_metrics(elapsed, total)

        if path:
            pcost = len(path) - 1
            self._metrics.set_cost(pcost)
            for r, c in path:
                if (r, c) not in (self._grid.start, self._grid.goal):
                    self._grid_state[r][c] = "path"
                    self._canvas.itemconfig(self._cells[(r, c)], fill=CELL_CLR["path"])
                    self._root.update()
                    time.sleep(DELAY)
            self._status_var.set(f"Done!  Cost: {pcost}  |  Nodes: {total}  |  Time: {elapsed:.1f} ms")
        else:
            self._metrics.set_cost(None)
            self._status_var.set(f"No path found.  Nodes: {total}  |  Time: {elapsed:.1f} ms")

        self._running = False
        self._set_ctrls(True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", root.winfo_fpixels("1i") / 72.0)
    except Exception:
        pass
    PathfinderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
