import streamlit as st
import networkx as nx
import pandas as pd
import json
import streamlit.components.v1 as components
import engine

st.set_page_config(page_title="Community Detection Demo", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        background-color: #007bff;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.6rem;
        font-weight: 600;
    }
    .stButton>button:hover { background-color: #0056b3; color: white; }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace; font-size: 14px; }
    h1, h2, h3 { color: #343a40; font-family: 'Segoe UI', sans-serif; }
    @media (max-width: 768px) {
        .stTextArea textarea { height: 200px !important; }
        h1 { font-size: 1.8rem !important; }
        h2, h3 { font-size: 1.3rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Phát hiện cộng đồng trong mạng lưới")
st.write("Sử dụng tối ưu hóa Modularity Q để phân tích cấu trúc đồ thị.")

DATASETS = {
    "Tùy chỉnh (Nhập tay)": "",
    "Zachary's Karate Club (n=34)": "2 1\n3 1\n4 1\n5 1\n6 1\n7 1\n8 1\n9 1\n11 1\n12 1\n13 1\n14 1\n18 1\n20 1\n22 1\n32 1\n3 2\n4 2\n8 2\n14 2\n18 2\n20 2\n22 2\n31 2\n4 3\n8 3\n9 3\n10 3\n14 3\n28 3\n29 3\n33 3\n8 4\n13 4\n14 4\n7 5\n11 5\n7 6\n11 6\n17 6\n17 7\n31 9\n33 9\n34 9\n34 10\n34 14\n33 15\n34 15\n33 16\n34 16\n33 19\n34 19\n34 20\n33 21\n34 21\n33 23\n34 23\n26 24\n28 24\n30 24\n33 24\n34 24\n26 25\n28 25\n32 25\n32 26\n30 27\n34 27\n34 28\n32 29\n34 29\n33 30\n34 30\n33 31\n34 31\n33 32\n34 32\n34 33",
    "Dolphins Social Network (n=62)": "1 11\n1 15\n1 16\n1 41\n1 43\n1 48\n2 18\n2 20\n2 27\n2 28\n2 29\n2 37\n2 42\n2 55\n3 11\n3 43\n3 45\n3 62\n4 9\n4 15\n4 60\n5 52\n6 10\n6 14\n6 57\n6 58\n7 10\n7 14\n7 18\n7 55\n7 57\n7 58\n8 20\n8 28\n8 31\n8 41\n8 55\n9 21\n9 29\n9 38\n9 46\n9 60\n10 14\n10 18\n10 33\n10 42\n10 58\n11 30\n11 43\n11 48\n12 52\n13 34\n14 18\n14 33\n14 42\n14 55\n14 58\n15 17\n15 25\n15 34\n15 35\n15 38\n15 39\n15 41\n15 44\n15 51\n15 53\n16 19\n16 25\n16 41\n16 46\n16 56\n16 60\n17 21\n17 34\n17 38\n17 39\n17 51\n18 23\n18 26\n18 28\n18 32\n18 58\n19 21\n19 22\n19 25\n19 30\n19 46\n19 52\n20 31\n20 55\n21 29\n21 37\n21 39\n21 45\n21 48\n21 51\n22 30\n22 34\n22 38\n22 46\n22 52\n24 37\n24 46\n24 52\n25 30\n25 46\n25 52\n26 27\n26 28\n27 28\n29 31\n29 48\n30 36\n30 44\n30 46\n30 52\n30 53\n31 43\n31 48\n33 61\n34 35\n34 38\n34 39\n34 41\n34 44\n34 51\n35 38\n35 45\n35 50\n37 38\n37 40\n37 41\n37 60\n38 41\n38 44\n38 46\n38 62\n39 44\n39 45\n39 53\n39 59\n40 58\n41 53\n42 55\n42 58\n43 48\n43 51\n44 47\n44 54\n46 51\n46 52\n46 60\n47 50\n49 58\n51 52\n52 56\n54 62\n55 58",
    "College Football (n=115)": "1 2\n1 3\n1 4\n1 5\n1 6\n1 7\n1 8\n1 9\n1 10\n1 11\n1 12\n1 13\n2 14\n2 15\n2 7\n2 16\n2 17\n2 18\n2 19\n2 20\n2 21\n2 22\n2 23\n24 25\n24 26\n24 27\n24 28\n24 29\n24 30\n24 31\n24 32\n24 33\n24 34\n24 35\n24 36\n25 37\n25 38\n25 39\n25 40\n25 41\n25 42\n25 33\n25 34\n25 43\n25 44\n25 45\n3 37\n3 4\n3 5\n3 6\n3 46\n3 9\n3 47\n3 12\n3 13\n3 48\n37 49\n37 38\n37 41\n37 34\n37 43\n37 44\n37 11\n37 50\n37 51\n37 52\n26 53\n26 54\n26 55\n26 30\n26 56\n26 42\n26 31\n26 32\n26 57\n26 35\n26 36\n53 58\n53 59\n53 60\n53 40\n53 61\n53 62\n53 63\n53 64\n53 65\n53 48\n53 66\n58 4\n58 59\n58 60\n58 9\n58 67\n58 61\n58 63\n58 64\n58 11\n58 66\n4 5\n4 60\n4 6\n4 9\n4 32\n4 12\n4 13\n4 48\n49 38\n49 31\n49 33\n49 34\n49 43\n49 44\n49 51\n49 45\n49 52\n38 68\n38 46\n38 69\n38 47\n38 11\n38 50\n38 13\n70 27\n70 28\n70 71\n70 72\n70 39\n70 73\n70 74\n70 75\n70 76\n70 57\n27 29\n27 54\n27 55\n27 17\n27 31\n27 32\n27 35\n27 36\n27 77\n28 29\n28 39\n28 75\n28 76\n28 78\n28 79\n28 57\n28 80\n29 54\n29 55\n29 30\n29 31\n29 61\n29 81\n29 35\n29 36\n29 82\n5 71\n5 6\n5 75\n5 9\n5 83\n5 43\n5 12\n5 13\n71 84\n71 15\n71 42\n71 85\n71 10\n71 86\n71 87\n71 88\n71 89\n72 90\n72 91\n72 73\n72 74\n72 75\n72 92\n72 78\n72 93\n72 79\n72 80\n90 94\n90 95\n90 7\n90 8\n90 74\n90 96\n90 56\n90 97\n90 98\n90 20\n84 59\n84 74\n84 85\n84 10\n84 99\n84 100\n84 101\n84 86\n84 88\n84 89\n59 60\n59 54\n59 102\n59 67\n59 61\n59 63\n59 48\n59 66\n60 6\n60 30\n60 67\n60 61\n60 63\n60 64\n60 48\n6 9\n6 64\n6 11\n6 12\n6 13\n6 66\n68 14\n68 46\n68 69\n68 103\n68 47\n68 44\n68 86\n68 11\n68 77\n14 7\n14 16\n14 17\n14 104\n14 19\n14 21\n14 22\n14 36\n14 23\n39 15\n39 73\n39 75\n39 92\n39 76\n39 93\n39 57\n15 105\n15 85\n15 106\n15 10\n15 99\n15 101\n15 87\n15 88\n46 75\n46 69\n46 47\n46 64\n46 11\n46 89\n94 95\n94 8\n94 92\n94 56\n94 97\n94 107\n94 65\n94 108\n94 98\n94 20\n95 8\n95 96\n95 69\n95 56\n95 97\n95 65\n95 98\n95 20\n95 23\n91 54\n91 73\n91 76\n91 78\n91 56\n91 93\n91 79\n91 97\n91 57\n91 80\n54 55\n54 30\n54 109\n54 32\n54 35\n54 36\n7 16\n7 17\n7 19\n7 21\n7 22\n7 23\n73 8\n73 92\n73 78\n73 93\n73 79\n73 98\n73 80\n8 96\n8 56\n8 97\n8 81\n8 98\n8 20\n74 16\n74 76\n74 42\n74 110\n16 17\n16 107\n16 19\n16 87\n16 21\n16 22\n16 23\n75 55\n75 76\n75 78\n75 79\n75 57\n55 30\n55 78\n55 31\n55 65\n55 35\n55 36\n40 9\n40 67\n40 41\n40 33\n40 34\n40 43\n40 51\n40 45\n40 52\n9 83\n9 12\n9 13\n92 76\n92 18\n92 106\n76 93\n76 99\n76 97\n76 57\n96 17\n96 111\n96 18\n96 103\n96 100\n96 112\n96 108\n96 113\n17 85\n17 19\n17 21\n17 22\n17 23\n102 30\n102 109\n102 104\n102 83\n102 62\n102 114\n102 115\n102 77\n102 66\n102 82\n30 31\n30 93\n30 32\n30 35\n111 109\n111 104\n111 18\n111 103\n111 100\n111 112\n111 108\n111 81\n111 88\n111 51\n109 104\n109 83\n109 62\n109 114\n109 44\n109 115\n109 77\n109 82\n69 67\n69 61\n69 47\n69 64\n69 11\n67 61\n67 63\n67 64\n67 20\n67 48\n67 66\n41 104\n41 33\n41 34\n41 44\n41 51\n41 45\n41 113\n104 83\n104 62\n104 114\n104 112\n104 115\n104 77\n104 82\n78 56\n78 93\n78 79\n78 80\n56 97\n56 19\n56 98\n56 20\n105 18\n105 85\n105 10\n105 99\n105 101\n105 86\n105 87\n105 88\n105 36\n18 100\n18 112\n18 108\n18 81\n18 113\n42 110\n42 106\n42 115\n42 50\n42 20\n42 82\n110 31\n110 106\n110 103\n110 101\n110 50\n110 89\n31 32\n31 79\n31 36\n93 85\n93 79\n93 81\n93 80\n85 99\n85 101\n85 86\n85 87\n85 22\n106 32\n106 10\n106 50\n106 23\n106 113\n32 35\n32 36\n32 66\n10 103\n10 99\n10 86\n10 88\n10 89\n103 100\n103 101\n103 112\n103 108\n103 81\n103 113\n83 61\n83 62\n83 114\n83 115\n83 13\n83 77\n83 82\n61 64\n61 48\n61 66\n47 99\n47 114\n47 115\n47 11\n47 108\n47 87\n99 101\n99 87\n99 21\n99 89\n79 33\n79 80\n33 34\n33 43\n33 45\n33 13\n33 52\n62 34\n62 63\n62 114\n62 115\n62 77\n62 82\n34 65\n34 44\n34 45\n100 101\n100 112\n100 81\n100 52\n100 113\n101 87\n101 88\n101 89\n63 64\n63 65\n63 51\n63 48\n63 66\n64 48\n64 66\n97 107\n97 98\n97 20\n97 23\n107 65\n107 57\n107 112\n107 108\n107 12\n107 98\n107 22\n107 77\n43 65\n43 114\n43 44\n43 51\n43 52\n65 12\n65 98\n65 35\n114 44\n114 115\n114 77\n114 82\n44 51\n44 52\n57 80\n112 86\n112 108\n112 81\n112 50\n86 87\n86 88\n86 13\n86 89\n115 19\n115 52\n115 77\n115 82\n19 80\n19 21\n19 22\n19 23\n108 81\n108 12\n108 113\n81 36\n81 113\n12 13\n98 20\n87 89\n88 113\n88 89\n50 51\n50 113\n51 45\n51 52\n80 35\n35 45\n45 21\n45 52\n21 22\n21 23\n13 82\n22 23\n48 66\n77 82"
}

PALETTE = [
    "#e6194B", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
    "#911eb4", "#42d4f4", "#f032e6", "#bfef45", "#fabed4",
    "#469990", "#dcbeff", "#9A6324", "#fffac8"
]


def parse_graph(text):
    G = nx.Graph()
    lines = text.strip().split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            G.add_edge(parts[0], parts[1])
        elif len(parts) == 1:
            G.add_node(parts[0])
    return G


def _remove_overlaps(pos, node_list, min_dist, iterations=60):
    """Push nodes apart until no two are closer than min_dist."""
    p = {n: [float(pos[n][0]), float(pos[n][1])] for n in node_list}
    nl = list(node_list)
    for _ in range(iterations):
        moved = False
        for i in range(len(nl)):
            for j in range(i + 1, len(nl)):
                a, b = nl[i], nl[j]
                dx = p[b][0] - p[a][0]
                dy = p[b][1] - p[a][1]
                d2 = dx * dx + dy * dy
                if d2 < min_dist * min_dist and d2 > 1e-12:
                    d = d2 ** 0.5
                    push = (min_dist - d) * 0.5 / d
                    p[a][0] -= dx * push
                    p[a][1] -= dy * push
                    p[b][0] += dx * push
                    p[b][1] += dy * push
                    moved = True
        if not moved:
            break
    return {n: (p[n][0], p[n][1]) for n in node_list}


def generate_vis_html(G, partition):
    if G.number_of_nodes() == 0:
        return "<p style='padding:20px;color:#888'>Chưa có nút nào để hiển thị.</p>"

    has_communities = len(set(partition.values())) > 1

    SCALE = 500
    NODE_R = 14          # vis.js node radius (px)
    MIN_DIST = (NODE_R * 2 + 6) / SCALE   # minimum centre-to-centre in layout space

    pos = nx.spring_layout(G, seed=42, k=1.6, iterations=150)
    pos = _remove_overlaps(pos, list(G.nodes()), min_dist=MIN_DIST)

    nodes_js = []
    for node in G.nodes():
        comm_id = partition.get(node, 0)
        color = PALETTE[comm_id % len(PALETTE)] if has_communities else "#4878d8"
        degree = G.degree(node)
        nx_x, nx_y = pos.get(node, (0.0, 0.0))
        nodes_js.append({
            "id": str(node),
            "label": str(node),
            # tooltipHtml is a custom field — vis.js ignores it; we read it manually
            "tooltipHtml": f"<b>Node {node}</b><br>Cộng đồng: {comm_id}<br>Degree: {degree}",
            "x": round(float(nx_x) * SCALE, 1),
            "y": round(float(nx_y) * SCALE, 1),
            "color": {
                "background": color,
                "border": "#222222",
                "highlight": {"background": color, "border": "#000000"},
                "hover": {"background": color, "border": "#444444"},
            },
            "size": NODE_R,
        })

    edges_js = [{"id": i, "from": str(u), "to": str(v)} for i, (u, v) in enumerate(G.edges())]

    nodes_json = json.dumps(nodes_js)
    edges_json = json.dumps(edges_js)

    html = (
        """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #ffffff; font-family: 'Segoe UI', sans-serif; overflow: hidden; }
  #graph { width: 100%; height: 575px; background: #fafafa; }
  #hint {
    text-align: center; font-size: 11px; color: #888;
    padding: 4px 0 0; user-select: none;
  }
  #tooltip {
    position: fixed; background: rgba(30,30,30,0.88); color: #fff;
    padding: 6px 10px; border-radius: 6px; font-size: 12px; line-height: 1.6;
    pointer-events: none; display: none; z-index: 9999; white-space: nowrap;
  }
</style>
</head>
<body>
<div id="graph"></div>
<div id="hint">Scroll to zoom &nbsp;·&nbsp; Drag canvas to pan &nbsp;·&nbsp; Drag node — release to snap back</div>
<div id="tooltip"></div>
<script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<script>
  var nodesData = """
        + nodes_json
        + """;
  var nodes = new vis.DataSet(nodesData);
  var edges = new vis.DataSet("""
        + edges_json
        + """);

  // Store original (home) positions keyed by node id
  var home = {};
  nodesData.forEach(function(n) { home[n.id] = { x: n.x, y: n.y }; });

  var network = new vis.Network(
    document.getElementById('graph'),
    { nodes: nodes, edges: edges },
    {
      nodes: {
        shape: 'dot',
        font: { size: 13, color: '#222', strokeWidth: 2, strokeColor: '#ffffff' },
        borderWidth: 2,
        shadow: { enabled: true, size: 4, x: 1, y: 2, color: 'rgba(0,0,0,0.12)' }
      },
      edges: {
        color: { color: '#b0b8c1', highlight: '#6c757d', hover: '#6c757d' },
        width: 1.3,
        smooth: { enabled: true, type: 'continuous', roundness: 0.1 },
        hoverWidth: 2.5,
        selectionWidth: 2.5
      },
      physics: { enabled: false },
      interaction: {
        dragNodes: true,
        dragView: true,
        zoomView: true,
        zoomSpeed: 0.55,
        hover: true,
        tooltipDelay: 99999,
        navigationButtons: false,
        keyboard: { enabled: true, speed: { x: 10, y: 10, zoom: 0.02 } }
      }
    }
  );

  network.once('afterDrawing', function() {
    network.fit({ animation: { duration: 400, easingFunction: 'easeInOutQuad' } });
  });

  // ── Custom HTML tooltip ──────────────────────────────────────────────────
  var tip = document.getElementById('tooltip');
  var graphEl = document.getElementById('graph');

  network.on('hoverNode', function(params) {
    var data = nodes.get(params.node);
    if (data && data.tooltipHtml) {
      tip.innerHTML = data.tooltipHtml;
      tip.style.display = 'block';
    }
  });
  network.on('blurNode', function() { tip.style.display = 'none'; });

  graphEl.addEventListener('mousemove', function(e) {
    tip.style.left = (e.clientX + 14) + 'px';
    tip.style.top  = (e.clientY - 10) + 'px';
  });

  // ── Bungee spring animation ──────────────────────────────────────────────
  var springs = {};   // nodeId → { x, y, vx, vy, raf }

  function cancelSpring(id) {
    if (springs[id]) {
      cancelAnimationFrame(springs[id].raf);
      delete springs[id];
    }
  }

  network.on('dragStart', function(params) {
    if (params.nodes.length > 0) cancelSpring(params.nodes[0]);
  });

  network.on('dragEnd', function(params) {
    if (params.nodes.length === 0) return;
    var id   = params.nodes[0];
    var orig = home[id];
    if (!orig) return;

    var cur = network.getPositions([id])[id];
    var state = { x: cur.x, y: cur.y, vx: 0, vy: 0, raf: null };
    springs[id] = state;

    var K       = 0.10;   // spring stiffness  (higher = snappier)
    var DAMPING = 0.82;   // velocity kept each frame (lower = less bounce)
    var STOP    = 0.4;    // px threshold to snap-to-home

    function step() {
      state.vx = (state.vx - K * (state.x - orig.x)) * DAMPING;
      state.vy = (state.vy - K * (state.y - orig.y)) * DAMPING;
      state.x += state.vx;
      state.y += state.vy;

      nodes.update({ id: id, x: state.x, y: state.y });

      var dx = state.x - orig.x, dy = state.y - orig.y;
      if (Math.sqrt(dx*dx + dy*dy) < STOP && Math.abs(state.vx) < STOP && Math.abs(state.vy) < STOP) {
        nodes.update({ id: id, x: orig.x, y: orig.y });
        delete springs[id];
      } else {
        state.raf = requestAnimationFrame(step);
      }
    }
    state.raf = requestAnimationFrame(step);
  });
</script>
</body>
</html>"""
    )
    return html


col_input, col_viz = st.columns([1, 2])

with col_input:
    st.subheader("Cấu hình dữ liệu")
    selected_template = st.selectbox("Chọn mạng mẫu để demo", list(DATASETS.keys()))

    input_text = st.text_area(
        label="Dữ liệu cạnh (Graph Data)",
        value=DATASETS[selected_template],
        height=400,
    )

    G = parse_graph(input_text)
    st.write(f"Trạng thái: **{G.number_of_nodes()}** nút, **{G.number_of_edges()}** cạnh.")

with col_viz:
    st.subheader("Trực quan hóa tương tác")
    run_btn = st.button("Bắt đầu phát hiện cộng đồng")

    partition = {node: 0 for node in G.nodes()}
    if run_btn:
        if G.number_of_edges() > 0:
            with st.spinner("Leiden đang tính toán..."):
                partition = engine.run_leiden(G)
                q = engine.calculate_modularity(G, partition)
                st.success(f"Chỉ số Modularity Q: {q:.4f}")

    html_content = generate_vis_html(G, partition)
    components.html(html_content, height=610)

st.info("Mẹo: Scroll để zoom · Kéo nền để pan · Kéo nút để di chuyển · Hover để xem chi tiết.")
