/**
 * GridGuard Main Application Logic & API Controller
 * Connects UI widgets, REST endpoints, and Graph Visualizer.
 */

// Application State
const state = {
  network: null,
  selectedNodeId: null,
  activeSimulation: null,
  scenarios: []
};

// Graph Controller Instance
let graphCtrl = null;

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  setupGraph();
  bindUIEvents();
  await loadNetworkData();
  await loadScenarios();
}

function setupGraph() {
  graphCtrl = new GridGraphController('cy', handleNodeSelection);
  graphCtrl.init();
}

function bindUIEvents() {
  // Node Selector dropdown change
  const nodeSelect = document.getElementById('nodeSelect');
  nodeSelect.addEventListener('change', (e) => {
    const val = e.target.value;
    if (val) {
      selectNode(val);
    } else {
      clearSelection();
    }
  });

  // Simulate Disruption Button
  const btnSimulate = document.getElementById('btnSimulate');
  btnSimulate.addEventListener('click', () => {
    if (state.selectedNodeId) {
      runSimulation(state.selectedNodeId);
    }
  });

  // Inspector Action Button (Disable Node)
  const btnInspectorAction = document.getElementById('btnInspectorAction');
  btnInspectorAction.addEventListener('click', () => {
    if (state.selectedNodeId) {
      runSimulation(state.selectedNodeId);
    }
  });

  // Global Reset Button
  const btnReset = document.getElementById('btnResetNetwork');
  btnReset.addEventListener('click', () => {
    resetNetwork();
  });

  // Layout Controls
  const layoutBtns = document.querySelectorAll('.layout-controls .tool-btn');
  layoutBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      layoutBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const layoutName = btn.getAttribute('data-layout');
      if (graphCtrl) {
        graphCtrl.applyLayout(layoutName);
      }
    });
  });

  // Zoom & Viewport Controls
  document.getElementById('btnZoomIn').addEventListener('click', () => graphCtrl && graphCtrl.zoomIn());
  document.getElementById('btnZoomOut').addEventListener('click', () => graphCtrl && graphCtrl.zoomOut());
  document.getElementById('btnFitGraph').addEventListener('click', () => graphCtrl && graphCtrl.fit());
}

// -------------------------------------------------------------
// API Communications
// -------------------------------------------------------------

async function loadNetworkData() {
  try {
    const res = await fetch('/api/network');
    const json = await res.json();
    if (json.success && json.data) {
      state.network = json.data;
      populateNodeSelector(state.network.nodes);
      graphCtrl.loadNetwork(state.network.nodes, state.network.edges);
      updateTotalNodeCountBadge(state.network.nodes.length, state.network.edges.length);
      resetMetricsToBaseline();
    } else {
      console.error('Failed to load network:', json.message);
    }
  } catch (err) {
    console.error('Error fetching network:', err);
  }
}

async function loadScenarios() {
  try {
    const res = await fetch('/api/scenarios');
    const json = await res.json();
    if (json.success && json.scenarios) {
      state.scenarios = json.scenarios;
      renderScenarios(state.scenarios);
    }
  } catch (err) {
    console.error('Error fetching scenarios:', err);
  }
}

async function runSimulation(nodeId) {
  if (!nodeId) return;

  try {
    const btnSim = document.getElementById('btnSimulate');
    btnSim.disabled = true;
    btnSim.innerHTML = `<span class="status-dot"></span> Simulating...`;

    const res = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ disabled_node: nodeId })
    });

    const json = await res.json();
    btnSim.innerHTML = `
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
      Simulate Disruption
    `;
    btnSim.disabled = false;

    if (json.success && json.simulation) {
      state.activeSimulation = json.simulation;
      applySimulationResults(json.simulation);
    } else {
      alert(`Simulation Error: ${json.message || 'Unknown failure'}`);
    }
  } catch (err) {
    console.error('Error running simulation:', err);
    alert('Failed to execute simulation. Check server connection.');
  }
}

async function resetNetwork() {
  try {
    const res = await fetch('/api/reset', { method: 'POST' });
    const json = await res.json();
    if (json.success) {
      state.activeSimulation = null;
      state.selectedNodeId = null;

      // Reset UI widgets
      document.getElementById('nodeSelect').value = '';
      document.getElementById('btnSimulate').disabled = true;
      clearSelection();
      resetMetricsToBaseline();

      // Reset Graph Visuals
      graphCtrl.resetAllVisuals();
      if (json.data) {
        graphCtrl.loadNetwork(json.data.nodes, json.data.edges);
      }
    }
  } catch (err) {
    console.error('Error resetting network:', err);
  }
}

// -------------------------------------------------------------
// UI Rendering & Updates
// -------------------------------------------------------------

function populateNodeSelector(nodes) {
  const select = document.getElementById('nodeSelect');
  select.innerHTML = '<option value="">-- Choose Node to Disable --</option>';

  const typeGroups = {
    supplier: document.createElement('optgroup'),
    transmission: document.createElement('optgroup'),
    distribution: document.createElement('optgroup'),
    destination: document.createElement('optgroup')
  };

  typeGroups.supplier.label = '⚡ Power Plants (Suppliers)';
  typeGroups.transmission.label = '🗼 Substations / Transmission';
  typeGroups.distribution.label = '🏢 Distribution Hubs';
  typeGroups.destination.label = '🏙️ Destination Cities / Industrial';

  nodes.forEach(n => {
    const opt = document.createElement('option');
    opt.value = n.id;
    opt.textContent = `${n.id} — ${n.name} (${n.type})`;
    if (typeGroups[n.type]) {
      typeGroups[n.type].appendChild(opt);
    }
  });

  Object.values(typeGroups).forEach(group => {
    if (group.children.length > 0) {
      select.appendChild(group);
    }
  });
}

function handleNodeSelection(nodeData) {
  if (!nodeData || !nodeData.id) return;
  selectNode(nodeData.id);
}

function selectNode(nodeId) {
  state.selectedNodeId = nodeId;
  document.getElementById('nodeSelect').value = nodeId;
  document.getElementById('btnSimulate').disabled = false;

  const node = state.network?.nodes.find(n => n.id === nodeId);
  if (!node) return;

  // Update Inspector Card
  document.getElementById('inspectorEmptyState').classList.add('hidden');
  document.getElementById('inspectorDetails').classList.remove('hidden');

  document.getElementById('inspectorName').textContent = node.name;
  document.getElementById('inspectorId').textContent = node.id;

  const typeEl = document.getElementById('inspectorType');
  typeEl.textContent = node.type.toUpperCase();
  typeEl.className = `value type-${node.type}`;

  document.getElementById('inspectorLocation').textContent = node.location || 'Regional Grid';

  const supplyRow = document.getElementById('inspectorSupplyRow');
  const demandRow = document.getElementById('inspectorDemandRow');

  if (node.type === 'supplier') {
    supplyRow.classList.remove('hidden');
    document.getElementById('inspectorSupply').textContent = `${node.supply} MW`;
    demandRow.classList.add('hidden');
  } else if (node.type === 'destination') {
    demandRow.classList.remove('hidden');
    document.getElementById('inspectorDemand').textContent = `${node.demand} MW`;
    supplyRow.classList.add('hidden');
  } else {
    supplyRow.classList.add('hidden');
    demandRow.classList.add('hidden');
  }

  const isFailed = state.activeSimulation && state.activeSimulation.disabled_node.id === nodeId;
  const statusPill = document.getElementById('inspectorStatusPill');
  const actionBtn = document.getElementById('btnInspectorAction');

  if (isFailed) {
    statusPill.textContent = 'FAILED / OFFLINE';
    statusPill.className = 'pill pill-failed';
    actionBtn.textContent = 'Node is Disabled';
    actionBtn.disabled = true;
  } else {
    statusPill.textContent = 'Operational';
    statusPill.className = 'pill pill-operational';
    actionBtn.textContent = `Disable ${node.id}`;
    actionBtn.disabled = false;
  }

  graphCtrl.highlightNodeSelection(nodeId);
}

function clearSelection() {
  state.selectedNodeId = null;
  document.getElementById('inspectorEmptyState').classList.remove('hidden');
  document.getElementById('inspectorDetails').classList.add('hidden');
  document.getElementById('btnSimulate').disabled = true;
  if (graphCtrl) {
    graphCtrl.clearNodeSelection();
  }
}

function renderScenarios(scenarios) {
  const container = document.getElementById('scenariosContainer');
  container.innerHTML = '';

  scenarios.forEach(sc => {
    const card = document.createElement('div');
    card.className = 'scenario-card';
    card.innerHTML = `
      <div class="scenario-card-title">
        <span>${sc.title}</span>
        <span class="scenario-card-badge">Target: ${sc.node_id}</span>
      </div>
      <div class="scenario-card-desc">${sc.description}</div>
    `;

    card.addEventListener('click', () => {
      selectNode(sc.node_id);
      runSimulation(sc.node_id);
    });

    container.appendChild(card);
  });
}

function applySimulationResults(sim) {
  // Update Header Status Badge
  const statusBadge = document.getElementById('systemStatusBadge');
  const statusText = document.getElementById('systemStatusText');
  statusBadge.className = 'status-badge disrupted';
  statusText.textContent = `SIMULATION ACTIVE (${sim.disabled_node.id} FAILED)`;

  // Update Graph Visuals
  graphCtrl.applySimulationResult(sim);

  // Update Health Gauge
  updateHealthGauge(sim.network_health, sim.total_demand, sim.total_available_supply, sim.total_shortage);

  // Update Impact Metrics
  document.getElementById('metricAffectedNodes').textContent = sim.affected_nodes_count;
  document.getElementById('metricAffectedDest').textContent = sim.affected_destinations_count;
  document.getElementById('metricTotalShortage').innerHTML = `${sim.total_shortage} <small>MW</small>`;
  document.getElementById('metricRecoveredSupply').innerHTML = `${sim.total_available_supply} <small>MW</small>`;
  document.getElementById('metricAdditionalCost').textContent = `+₹${sim.total_additional_cost}`;
  document.getElementById('metricAdditionalDelay').innerHTML = `+${sim.total_additional_delay} <small>hrs</small>`;

  // Update Disruption Pipeline Breadcrumb
  const pipeline = document.getElementById('pipelineExplanation');
  pipeline.classList.remove('hidden');
  document.getElementById('pipelineFailedNode').textContent = `${sim.disabled_node.id} (${sim.disabled_node.name})`;
  document.getElementById('pipelineBfsCount').textContent = `${sim.algorithm_summary.bfs_nodes_traversed} Nodes Traversed`;
  document.getElementById('pipelineShortageMW').textContent = `${sim.total_shortage} MW Deficit`;
  document.getElementById('pipelineDijkstraRuns').textContent = `${sim.algorithm_summary.dijkstra_runs} Dijkstra Runs`;
  document.getElementById('pipelineHealthScore').textContent = `${sim.network_health}% Grid Health`;

  // Render Alternative Routes
  renderAlternativeRoutes(sim.alternatives_by_destination, sim.destination_impacts);

  // Refresh Inspector if viewing the failed node
  if (state.selectedNodeId) {
    selectNode(state.selectedNodeId);
  }
}

function renderAlternativeRoutes(alternativesByDest, destImpacts) {
  const container = document.getElementById('reroutesContainer');
  const emptyState = document.getElementById('reroutesEmptyState');

  const destEntries = Object.entries(alternativesByDest);
  if (destEntries.length === 0) {
    emptyState.innerHTML = '<p>No alternative routes were required or none exist.</p>';
    emptyState.classList.remove('hidden');
    container.classList.add('hidden');
    return;
  }

  emptyState.classList.add('hidden');
  container.classList.remove('hidden');
  container.innerHTML = '';

  destEntries.forEach(([destId, routes]) => {
    const impactInfo = destImpacts.find(d => d.destination === destId) || {};
    const group = document.createElement('div');
    group.className = 'dest-reroute-group';

    const groupHeader = document.createElement('div');
    groupHeader.className = 'dest-group-header';
    groupHeader.innerHTML = `
      <span class="dest-group-title">${impactInfo.name || destId} (${destId})</span>
      <span class="dest-group-demand">Demand: ${impactInfo.demand || 0} MW • Coverage: ${impactInfo.coverage || 0}%</span>
    `;
    group.appendChild(groupHeader);

    if (routes.length === 0) {
      const noRouteMsg = document.createElement('div');
      noRouteMsg.className = 'empty-state';
      noRouteMsg.innerHTML = '<span style="color:#f43f5e">⚠ No feasible alternative path available</span>';
      group.appendChild(noRouteMsg);
    } else {
      routes.forEach(r => {
        const card = document.createElement('div');
        card.className = `route-card ${r.is_best ? 'best-route' : ''}`;
        
        card.innerHTML = `
          <div class="route-card-header">
            <span class="route-rank-tag ${r.is_best ? 'best-tag' : 'alt-tag'}">
              ${r.is_best ? '★ BEST ALTERNATIVE (Rank 1)' : `Rank ${r.rank}`}
            </span>
            <span style="font-size:0.68rem; font-family:var(--font-mono); color:var(--accent-cyan)">
              Score: ${r.score}
            </span>
          </div>
          <div class="route-path-chain">${r.path_str}</div>
          <div class="route-metrics-row">
            <span>Supply: <strong>${r.recovered_supply} MW</strong></span>
            <span>Cost: <strong>+₹${r.additional_cost}</strong></span>
            <span>Delay: <strong>+${r.additional_delay}h</strong></span>
            <span>Bottleneck: <strong>${r.bottleneck_capacity} MW</strong></span>
          </div>
          <div class="route-explanation">${r.rank_explanation}</div>
          <button class="btn-view-route" data-path='${JSON.stringify(r.path)}'>
            🔍 Highlight Route on Graph
          </button>
        `;

        // Highlight route button event
        const btnView = card.querySelector('.btn-view-route');
        btnView.addEventListener('click', (e) => {
          e.stopPropagation();
          const path = JSON.parse(btnView.getAttribute('data-path'));
          graphCtrl.highlightRoute(path);
        });

        group.appendChild(card);
      });
    }

    container.appendChild(group);
  });
}

function updateHealthGauge(healthPercent, totalDemand, totalDelivered, totalShortage) {
  const percentEl = document.getElementById('healthPercent');
  const barEl = document.getElementById('healthBar');
  const ringEl = document.getElementById('healthRingBar');
  const narrativeEl = document.getElementById('healthStatusNarrative');

  percentEl.textContent = `${healthPercent}%`;
  barEl.style.width = `${healthPercent}%`;

  // Stroke dashoffset for SVG ring (Circumference ~ 314.15 for r=50)
  const circumference = 2 * Math.PI * 50;
  const offset = circumference - (healthPercent / 100) * circumference;
  ringEl.style.strokeDashoffset = offset;

  // Color dynamic gradient based on health
  if (healthPercent >= 90) {
    ringEl.style.stroke = '#10b981';
    barEl.style.background = 'linear-gradient(90deg, #10b981 0%, #00f2fe 100%)';
    narrativeEl.textContent = 'Nominal / Resilient: Grid demand successfully satisfied.';
  } else if (healthPercent >= 60) {
    ringEl.style.stroke = '#f59e0b';
    barEl.style.background = 'linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)';
    narrativeEl.textContent = `Moderate Stress: ${totalShortage} MW unmet deficit under capacity bottleneck.`;
  } else {
    ringEl.style.stroke = '#f43f5e';
    barEl.style.background = 'linear-gradient(90deg, #f43f5e 0%, #e11d48 100%)';
    narrativeEl.textContent = `Critical Outage: ${totalShortage} MW severe energy deficit across destinations.`;
  }

  document.getElementById('healthTotalDemand').textContent = `${totalDemand} MW`;
  document.getElementById('healthTotalDelivered').textContent = `${totalDelivered} MW`;
}

function resetMetricsToBaseline() {
  // Reset Header Badge
  const statusBadge = document.getElementById('systemStatusBadge');
  const statusText = document.getElementById('systemStatusText');
  statusBadge.className = 'status-badge operational';
  statusText.textContent = 'SYSTEM OPERATIONAL';

  // Reset Health Gauge
  updateHealthGauge(100, 250, 250, 0);

  // Reset Metrics Grid
  document.getElementById('metricAffectedNodes').textContent = '0';
  document.getElementById('metricAffectedDest').textContent = '0';
  document.getElementById('metricTotalShortage').innerHTML = '0 <small>MW</small>';
  document.getElementById('metricRecoveredSupply').innerHTML = '250 <small>MW</small>';
  document.getElementById('metricAdditionalCost').textContent = '₹0';
  document.getElementById('metricAdditionalDelay').innerHTML = '+0.0 <small>hrs</small>';

  // Hide Pipeline Breadcrumb
  document.getElementById('pipelineExplanation').classList.add('hidden');

  // Reset Alternative Routes
  document.getElementById('reroutesEmptyState').classList.remove('hidden');
  document.getElementById('reroutesContainer').classList.add('hidden');
  document.getElementById('reroutesContainer').innerHTML = '';
}

function updateTotalNodeCountBadge(nodeCount, edgeCount) {
  const badge = document.getElementById('graphNodeCountBadge');
  if (badge) {
    badge.textContent = `${nodeCount} Nodes • ${edgeCount} Directed Transmission Lines`;
  }
}
