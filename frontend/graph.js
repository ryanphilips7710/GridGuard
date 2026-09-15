/**
 * GridGuard Cytoscape.js Graph Visualization Controller
 * Handles topology rendering, layout physics, interactive node clicks,
 * and animated failure/reroute states.
 */

class GridGraphController {
  constructor(containerId, onNodeSelect) {
    this.container = document.getElementById(containerId);
    this.onNodeSelect = onNodeSelect;
    this.cy = null;
    this.currentLayout = 'breadthfirst';
    this.activeSimulation = null;
  }

  init() {
    if (!window.cytoscape) {
      console.error('Cytoscape.js is not loaded.');
      return;
    }

    this.cy = cytoscape({
      container: this.container,
      boxSelectionEnabled: false,
      autounselectify: false,
      style: this.getGraphStyles(),
      minZoom: 0.3,
      maxZoom: 3.0,
      wheelSensitivity: 0.25
    });

    // Node click and hover event listeners
    this.cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const nodeData = node.data();
      if (this.onNodeSelect) {
        this.onNodeSelect(nodeData);
      }
      this.highlightNodeSelection(node.id());
    });

    this.cy.on('tap', (evt) => {
      if (evt.target === this.cy) {
        // Clicked background canvas
        this.clearNodeSelection();
      }
    });

    // Handle window resize
    window.addEventListener('resize', () => {
      if (this.cy) {
        this.cy.resize();
        this.cy.fit(null, 40);
      }
    });
  }

  getGraphStyles() {
    return [
      // Base Node Style
      {
        selector: 'node',
        style: {
          'label': 'data(label)',
          'font-family': 'Outfit, sans-serif',
          'font-size': '11px',
          'font-weight': 600,
          'color': '#f8fafc',
          'text-valign': 'bottom',
          'text-margin-y': 6,
          'text-outline-color': '#070b12',
          'text-outline-width': 3,
          'width': 44,
          'height': 44,
          'border-width': 2,
          'border-color': 'rgba(255, 255, 255, 0.4)',
          'transition-property': 'background-color, border-color, width, height, opacity, border-width',
          'transition-duration': '0.35s'
        }
      },

      // Node Types
      {
        selector: 'node[type="supplier"]',
        style: {
          'shape': 'diamond',
          'background-color': '#00f2fe',
          'border-color': '#38bdf8',
          'width': 50,
          'height': 50
        }
      },
      {
        selector: 'node[type="transmission"]',
        style: {
          'shape': 'hexagon',
          'background-color': '#a855f7',
          'border-color': '#c084fc',
          'width': 42,
          'height': 42
        }
      },
      {
        selector: 'node[type="distribution"]',
        style: {
          'shape': 'round-rectangle',
          'background-color': '#f59e0b',
          'border-color': '#fbbf24',
          'width': 40,
          'height': 40
        }
      },
      {
        selector: 'node[type="destination"]',
        style: {
          'shape': 'ellipse',
          'background-color': '#10b981',
          'border-color': '#34d399',
          'width': 46,
          'height': 46
        }
      },

      // Selected / Active Node
      {
        selector: 'node:selected, node.selected-node',
        style: {
          'border-width': 4,
          'border-color': '#ffffff',
          'shadow-blur': 25,
          'shadow-color': '#00f2fe',
          'shadow-opacity': 0.8
        }
      },

      // Disruption States
      {
        selector: 'node.state-failed',
        style: {
          'background-color': '#f43f5e',
          'border-color': '#ff0033',
          'border-width': 4,
          'shadow-blur': 30,
          'shadow-color': '#f43f5e',
          'shadow-opacity': 1.0
        }
      },
      {
        selector: 'node.state-affected',
        style: {
          'background-color': '#ea580c',
          'border-color': '#fb923c',
          'border-width': 3,
          'border-style': 'dashed'
        }
      },
      {
        selector: 'node.state-rerouted',
        style: {
          'background-color': '#84cc16',
          'border-color': '#bef264',
          'border-width': 3.5,
          'shadow-blur': 15,
          'shadow-color': '#84cc16',
          'shadow-opacity': 0.7
        }
      },
      {
        selector: 'node.dimmed',
        style: {
          'opacity': 0.25
        }
      },

      // Base Edge Style
      {
        selector: 'edge',
        style: {
          'width': 2.2,
          'line-color': 'rgba(56, 189, 248, 0.4)',
          'target-arrow-color': 'rgba(56, 189, 248, 0.6)',
          'target-arrow-shape': 'triangle',
          'arrow-scale': 1.1,
          'curve-style': 'bezier',
          'label': 'data(edgeLabel)',
          'font-family': 'JetBrains Mono, monospace',
          'font-size': '8px',
          'color': '#94a3b8',
          'text-rotation': 'autorotate',
          'text-outline-color': '#070b12',
          'text-outline-width': 2,
          'text-margin-y': -6,
          'opacity': 0.75,
          'transition-property': 'line-color, target-arrow-color, width, opacity',
          'transition-duration': '0.35s'
        }
      },

      // Edge States
      {
        selector: 'edge.edge-failed',
        style: {
          'line-color': '#f43f5e',
          'target-arrow-color': '#f43f5e',
          'line-style': 'dashed',
          'width': 2.5,
          'opacity': 0.85
        }
      },
      {
        selector: 'edge.edge-rerouted',
        style: {
          'line-color': '#84cc16',
          'target-arrow-color': '#84cc16',
          'width': 4.5,
          'opacity': 1.0,
          'shadow-blur': 12,
          'shadow-color': '#84cc16',
          'shadow-opacity': 0.8
        }
      },
      {
        selector: 'edge.edge-highlighted',
        style: {
          'line-color': '#00f2fe',
          'target-arrow-color': '#00f2fe',
          'width': 5.0,
          'opacity': 1.0,
          'shadow-blur': 16,
          'shadow-color': '#00f2fe',
          'shadow-opacity': 0.9
        }
      },
      {
        selector: 'edge.dimmed',
        style: {
          'opacity': 0.12
        }
      }
    ];
  }

  loadNetwork(nodes, edges) {
    if (!this.cy) return;

    const elements = [];

    // Add Nodes
    nodes.forEach(n => {
      let label = `${n.id}\n${n.name}`;
      if (n.type === 'supplier') {
        label = `${n.id} [${n.supply}MW]\n${n.name}`;
      } else if (n.type === 'destination') {
        label = `${n.id} [${n.demand}MW]\n${n.name}`;
      }

      elements.push({
        group: 'nodes',
        data: {
          id: n.id,
          label: label,
          name: n.name,
          type: n.type,
          supply: n.supply,
          demand: n.demand,
          location: n.location || '',
          enabled: n.enabled
        }
      });
    });

    // Add Edges
    edges.forEach((e, idx) => {
      const edgeLabel = `${e.capacity}MW • ₹${e.cost}`;
      elements.push({
        group: 'edges',
        data: {
          id: `e_${e.from}_${e.to}_${idx}`,
          source: e.from,
          target: e.to,
          capacity: e.capacity,
          cost: e.cost,
          delay: e.delay,
          edgeLabel: edgeLabel,
          enabled: e.enabled
        }
      });
    });

    this.cy.elements().remove();
    this.cy.add(elements);
    this.applyLayout(this.currentLayout);
  }

  applyLayout(layoutName = 'breadthfirst') {
    this.currentLayout = layoutName;
    if (!this.cy) return;

    let layoutOptions = {};

    if (layoutName === 'breadthfirst') {
      // Top-down hierarchical layout from suppliers down to destinations
      layoutOptions = {
        name: 'breadthfirst',
        directed: true,
        roots: ['P1', 'P2', 'P3'],
        padding: 40,
        spacingFactor: 1.25,
        animate: true,
        animationDuration: 500
      };
    } else if (layoutName === 'cose') {
      // Force-directed organic physics layout
      layoutOptions = {
        name: 'cose',
        animate: true,
        animationDuration: 600,
        nodeOverlap: 20,
        idealEdgeLength: 100,
        edgeElasticity: 100,
        nodeRepulsion: 400000,
        padding: 40
      };
    } else if (layoutName === 'concentric') {
      layoutOptions = {
        name: 'concentric',
        concentric: (node) => {
          const type = node.data('type');
          if (type === 'supplier') return 4;
          if (type === 'transmission') return 3;
          if (type === 'distribution') return 2;
          return 1;
        },
        levelWidth: () => 1,
        padding: 40,
        animate: true
      };
    }

    const layout = this.cy.layout(layoutOptions);
    layout.run();
  }

  applySimulationResult(simData) {
    if (!this.cy || !simData) return;
    this.activeSimulation = simData;

    // Reset classes
    this.cy.elements().removeClass(
      'state-failed state-affected state-rerouted dimmed edge-failed edge-rerouted edge-highlighted'
    );

    const failedNodeId = simData.disabled_node.id;
    const affectedNodes = simData.affected_nodes || [];
    const reroutedNodes = simData.rerouted_nodes || [];
    const reroutedEdges = simData.rerouted_edges || [];

    // 1. Mark Failed Node
    const failedEl = this.cy.getElementById(failedNodeId);
    if (failedEl.length) {
      failedEl.addClass('state-failed');
    }

    // 2. Mark Failed Edges connected directly to failed node
    this.cy.edges().forEach(edge => {
      if (edge.source().id() === failedNodeId || edge.target().id() === failedNodeId) {
        edge.addClass('edge-failed');
      }
    });

    // 3. Mark Affected Nodes
    affectedNodes.forEach(nodeId => {
      const el = this.cy.getElementById(nodeId);
      if (el.length && nodeId !== failedNodeId) {
        el.addClass('state-affected');
      }
    });

    // 4. Mark Rerouted Flow Nodes and Edges
    reroutedNodes.forEach(nodeId => {
      const el = this.cy.getElementById(nodeId);
      if (el.length && nodeId !== failedNodeId) {
        el.removeClass('state-affected');
        el.addClass('state-rerouted');
      }
    });

    reroutedEdges.forEach(re => {
      this.cy.edges().forEach(edge => {
        if (edge.source().id() === re.from && edge.target().id() === re.to) {
          edge.addClass('edge-rerouted');
        }
      });
    });
  }

  highlightRoute(nodePath) {
    if (!this.cy || !nodePath || nodePath.length < 2) return;

    // Dim all elements first
    this.cy.elements().addClass('dimmed');

    // Highlight specific nodes and edges along path
    for (let i = 0; i < nodePath.length; i++) {
      const nodeId = nodePath[i];
      const nodeEl = this.cy.getElementById(nodeId);
      if (nodeEl.length) {
        nodeEl.removeClass('dimmed');
        nodeEl.addClass('state-rerouted');
      }

      if (i < nodePath.length - 1) {
        const nextId = nodePath[i + 1];
        this.cy.edges().forEach(edge => {
          if (edge.source().id() === nodeId && edge.target().id() === nextId) {
            edge.removeClass('dimmed');
            edge.addClass('edge-highlighted');
          }
        });
      }
    }
  }

  clearRouteHighlight() {
    if (!this.cy) return;
    this.cy.elements().removeClass('dimmed edge-highlighted');
    if (this.activeSimulation) {
      this.applySimulationResult(this.activeSimulation);
    }
  }

  highlightNodeSelection(nodeId) {
    if (!this.cy) return;
    this.cy.nodes().removeClass('selected-node');
    const target = this.cy.getElementById(nodeId);
    if (target.length) {
      target.addClass('selected-node');
    }
  }

  clearNodeSelection() {
    if (!this.cy) return;
    this.cy.nodes().removeClass('selected-node');
  }

  resetAllVisuals() {
    if (!this.cy) return;
    this.activeSimulation = null;
    this.cy.elements().removeClass(
      'state-failed state-affected state-rerouted dimmed edge-failed edge-rerouted edge-highlighted selected-node'
    );
  }

  zoomIn() {
    if (!this.cy) return;
    this.cy.zoom(this.cy.zoom() * 1.25);
  }

  zoomOut() {
    if (!this.cy) return;
    this.cy.zoom(this.cy.zoom() * 0.8);
  }

  fit() {
    if (!this.cy) return;
    this.cy.fit(null, 40);
  }
}
