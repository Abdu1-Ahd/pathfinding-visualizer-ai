# 🧭 Pathfinding Visualizer — AI Search Algorithms

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Built with](https://img.shields.io/badge/Built%20with-Tkinter-orange)

> **Watch how AI finds the shortest path, step by step!**

This is an interactive **Pathfinding Algorithm Visualizer** built with Python. It lets you draw walls on a grid, pick a search algorithm, and then watch it explore the map in real time to find the best route from the **start node** to the **goal node**.

Think of it like a maze solver — but you get to see every decision the AI makes along the way. The explored cells light up, the frontier expands, and when the algorithm is done, the shortest path glows on screen. It's a great way to understand how AI search actually works under the hood.

---

## 🤖 Algorithms Implemented

### A\* (A-Star) Algorithm

A\* is one of the smartest pathfinding algorithms out there. It combines two things:

- **How far you've already walked** (the actual cost from the start)
- **How far you think you still need to go** (a heuristic estimate to the goal)

By adding both together, A\* always picks the most promising cell to explore next. That's why it finds the **shortest path** and does it efficiently.

### Greedy Best-First Search (GBFS)

GBFS is simpler — it only cares about **how close a cell looks to the goal** (the heuristic). It doesn't track how far it has already traveled. This makes it faster in some cases, but it doesn't always find the shortest path. It's "greedy" because it rushes toward the goal without looking back.

Both algorithms support two heuristic functions:

| Heuristic | How It Works                                             |
| --------- | -------------------------------------------------------- |
| Manhattan | Counts horizontal + vertical distance (like city blocks) |
| Euclidean | Measures straight-line distance (as the crow flies)      |

---

## ✨ Features

- 🎨 **Interactive Grid** — Click to place walls, drag to draw them fast
- 🟢 **Start & Goal Nodes** — Clearly marked on the grid
- 🔍 **Live Visualization** — Watch the algorithm explore cells in real time
- 🛤️ **Path Highlighting** — See the final shortest path glow green
- 🗺️ **Map Generator** — Instantly create Sparse, Moderate, or Dense mazes
- 🔄 **Reset Grid** — Clear everything and start fresh
- 📊 **Metrics Panel** — Track visited nodes, path cost, and execution time
- ⚡ **Dynamic Mode** — Re-runs the search live as you draw walls
- 🎯 **Heuristic Selection** — Switch between Manhattan and Euclidean distance

---

## 📸 Screenshots

### A\* Algorithm — Manhattan Heuristic (Best Case)

![A* Manhattan Best Case](screenshots/Best%20case_Astar_Man.png)

### A\* Algorithm — Euclidean Heuristic (Best Case)

![A* Euclidean Best Case](screenshots/Best%20case_Astar_Euc.png)

### GBFS — Manhattan Heuristic (Best Case)

![GBFS Manhattan Best Case](screenshots/Best%20case_GBFS_Man.png)

### GBFS — Euclidean Heuristic (Best Case)

![GBFS Euclidean Best Case](screenshots/Best%20case_GBFS_Euc.png)

### A\* Algorithm — Manhattan Heuristic (Worst Case)

![A* Manhattan Worst Case](screenshots/Worst%20case_Astar_Man.png)

### GBFS — Manhattan Heuristic (Worst Case)

![GBFS Manhattan Worst Case](screenshots/Worst%20case_GBFS_Man.png)

---

## 🚀 How to Run the Project

Follow these simple steps:

**1. Clone the repository**

```bash
git clone https://github.com/Abdu1-Ahd/pathfinding-visualizer-ai.git
```

**2. Go into the project folder**

```bash
cd pathfinding-visualizer-ai
```

**3. Run the program**

```bash
python src/pathfinder.py
```

That's it! A window will open with the grid. Draw some walls, pick an algorithm, and hit **Start Search**.

> **Note:** This project only uses Python's built-in libraries (`tkinter`, `heapq`, `math`, etc.), so there's nothing extra to install. Just make sure you have **Python 3.7+** installed.

---

## 📦 Dependencies

| Library       | Included With Python? |
| ------------- | --------------------- |
| `tkinter`     | ✅ Yes                |
| `heapq`       | ✅ Yes                |
| `math`        | ✅ Yes                |
| `collections` | ✅ Yes                |
| `random`      | ✅ Yes                |
| `time`        | ✅ Yes                |

**No external packages needed.** Everything runs with a standard Python installation.

---

## 📁 Project Structure

```
pathfinding-visualizer-ai/
│
├── src/
│   └── pathfinder.py        # Main application — all algorithms, GUI, and logic
│
├── screenshots/              # Images showing the algorithms in action
│   ├── Best case_Astar_Man.png
│   ├── Best case_Astar_Euc.png
│   ├── Best case_GBFS_Man.png
│   ├── Best case_GBFS_Euc.png
│   ├── Worst case_Astar_Man.png
│   ├── Worst case_GBFS_Man.png
│   └── ...
│
├── README.md                 # You're reading it right now!
├── requirements.txt          # Lists dependencies (all built-in)
└── .gitignore                # Keeps the repo clean
```

---

## 📚 Learning Purpose

This project was built as a university assignment to help students understand how **AI search algorithms** work in practice. Instead of just reading about A\* or GBFS in a textbook, you can actually _see_ them in action — watching how they explore the grid, make decisions, and eventually find the path.

It's a hands-on way to learn:

- How **informed search** uses heuristics to make smarter choices
- The difference between **A\*** (optimal) and **GBFS** (fast but not always optimal)
- How **Manhattan** vs **Euclidean** distance affects the search behavior
- What the **frontier**, **explored set**, and **path** look like during a real search

---

## 🙌 Credits

Built with ❤️ using **Python** and **Tkinter**.

---
