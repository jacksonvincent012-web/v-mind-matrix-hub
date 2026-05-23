// ================= V-MIND MATRIX BACKEND CLUSTER ENGINE =================
// Production Grade: Handles Local Images, Form Manifests, and Prevents Lockouts
// =========================================================================

const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = 3500;
const DATA_PATH = path.join(__dirname, "data.json");

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname)); // Automatically serves locally hosted PNG assets!

app.get("/images.html", (req, res) => {
  res.sendFile(path.join(__dirname, "images.html"));
});

const readClusterData = () => {
  try {
    if (!fs.existsSync(DATA_PATH)) return [];
    const fileContent = fs.readFileSync(DATA_PATH, "utf8");
    return fileContent.trim() ? JSON.parse(fileContent) : [];
  } catch (err) {
    console.error("Database reading fault:", err);
    return [];
  }
};

// GET: Fetch matrix nodes
app.get("/api/nodes", (req, res) => {
  res.json(readClusterData());
});

// POST: Manifest new custom nodes smoothly via the modal form
app.post("/api/nodes", (req, res) => {
  try {
    const nodes = readClusterData();
    const nextNum = nodes.length + 1;
    const formattedId = `${nextNum < 10 ? "0" + nextNum : nextNum}_NEW`;

    const newNode = {
      id: formattedId,
      name: req.body.name || "Unassigned Entity",
      tag: req.body.tag || "GLS",
      src: req.body.src || "mountain.png",
      desc:
        req.body.desc || "System parameters pending initial sync deployment.",
      m1: "50.0%",
      m2: "2.00λ",
      bar1: 50,
      bar2: 42.5,
    };

    nodes.push(newNode);
    fs.writeFileSync(DATA_PATH, JSON.stringify(nodes, null, 2));
    res.status(201).json({ success: true, node: newNode });
  } catch (err) {
    res.status(500).json({ success: false, message: "Internal server error." });
  }
});

// PUT: Modify specific metrics
app.put("/api/nodes/:id", (req, res) => {
  try {
    let nodes = readClusterData();
    const index = nodes.findIndex((n) => n.id === req.params.id);

    if (index !== -1) {
      nodes[index] = { ...nodes[index], ...req.body, id: req.params.id };
      fs.writeFileSync(DATA_PATH, JSON.stringify(nodes, null, 2));
      res.json({ success: true });
    } else {
      res
        .status(404)
        .json({ success: false, message: "Node target not located." });
    }
  } catch (err) {
    res.status(500).json({ success: false, message: "Update routine failed." });
  }
});

// ================= TELEMETRY INTEGRITY HEARTBEAT =================
// Only alters float parameters; will never touch image strings or lock you out
// =================================================================
setInterval(() => {
  if (!fs.existsSync(DATA_PATH)) return;
  try {
    let nodes = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));
    if (!nodes.length) return;

    nodes = nodes.map((node) => {
      let currentM1 = parseFloat(node.m1) || 50;
      let flux = Math.random() * 4 - 2;
      let nextM1 = Math.min(Math.max(currentM1 + flux, 10), 100).toFixed(1);

      let currentM2 = parseFloat(node.m2) || 2.0;
      let nextM2 = Math.min(
        Math.max(currentM2 + flux * 0.02, 0.5),
        5.0,
      ).toFixed(2);

      return {
        ...node, // Spreads path and strings completely intact without mutations
        m1: `${nextM1}%`,
        m2: `${nextM2}λ`,
        bar1: parseFloat(nextM1),
        bar2: Math.min(parseFloat(nextM1) * 0.85, 98),
      };
    });

    fs.writeFileSync(DATA_PATH, JSON.stringify(nodes, null, 2));
  } catch (err) {
    // Safe bypass
  }
}, 3000);

app.listen(PORT, () => {
  console.log(
    `[V-MIND CLUSTER ACCESS GRANTED]: http://localhost:${PORT}/images.html`,
  );
});
