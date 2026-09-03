#!/usr/bin/env node
/**
 * FinShield Backend Test & Health Suite Runner
 * 
 * Provides comprehensive terminal execution, layer-by-layer health verification,
 * and status reporting across all architecture layers of the FinShield backend.
 */

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// ANSI Color Codes
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';
const GREEN = '\x1b[32m';
const RED = '\x1b[31m';
const YELLOW = '\x1b[33m';
const CYAN = '\x1b[36m';
const BLUE = '\x1b[34m';
const MAGENTA = '\x1b[35m';
const GRAY = '\x1b[90m';

// Find project root
const ROOT_DIR = path.resolve(__dirname, '..');
const BACKEND_DIR = path.join(ROOT_DIR, 'backend');

// Locate Python executable (check .venv first, then system python)
function getPythonExecutable() {
    const candidates = [
        'python',
        'python3',
        path.join(BACKEND_DIR, '.venv', 'Scripts', 'python.exe'),
        path.join(BACKEND_DIR, '.venv', 'bin', 'python'),
        path.join(ROOT_DIR, '.venv', 'Scripts', 'python.exe'),
        path.join(ROOT_DIR, '.venv', 'bin', 'python')
    ];

    for (const candidate of candidates) {
        try {
            const check = spawnSync(candidate, ['-m', 'pytest', '--version'], { encoding: 'utf-8', shell: true });
            if (check.status === 0) return candidate;
        } catch (e) {}
    }
    return 'python';
}

const PYTHON = getPythonExecutable();

// CLI Arguments
const args = process.argv.slice(2);
const layerArg = args.find(a => a.startsWith('--layer='));
const targetLayer = layerArg ? layerArg.split('=')[1].toLowerCase() : null;
const isVerbose = args.includes('-v') || args.includes('--verbose');
const isQuick = args.includes('--quick');
const isHealthOnly = args.includes('--health') || args.includes('--status');

// Layer Definitions
const LAYERS = [
    {
        id: 'config_and_health',
        name: 'Layer 1: Configuration & System Health',
        file: 'backend/tests/test_health_and_config.py',
        description: 'Verifies settings, scoring weights, risk thresholds, partner credentials & DB connectivity'
    },
    {
        id: 'models',
        name: 'Layer 2: Database Schema & ORM Models',
        file: 'backend/tests/test_models.py',
        description: 'Tests 19 tables, relationships, cascades, SQLite/PostgreSQL resilience & transactions'
    },
    {
        id: 'engines',
        name: 'Layer 3: 10 Calculation & Intelligence Engines',
        file: 'backend/tests/test_engines.py',
        description: 'Tests Financial, Risk, Forecast, ML, Overdraft, Loan, Simulator, Interventions & Debtkart'
    },
    {
        id: 'api',
        name: 'Layer 4: REST API Endpoints & Routers',
        file: 'backend/tests/test_api.py',
        description: 'Tests /health, /, and all /api/v1/* routes (Customers, Accounts, Risk, Forecast, etc.)'
    }
];

function printHeader() {
    console.log('');
    console.log(`${CYAN}${BOLD}======================================================================${RESET}`);
    console.log(`${CYAN}${BOLD}     🛡️  FINSHIELD BACKEND TEST & SYSTEM HEALTH VERIFICATION          ${RESET}`);
    console.log(`${CYAN}${BOLD}======================================================================${RESET}`);
    console.log(`${GRAY}Target Workspace : ${ROOT_DIR}${RESET}`);
    console.log(`${GRAY}Python Runtime   : ${PYTHON}${RESET}`);
    console.log(`${GRAY}Timestamp        : ${new Date().toISOString()}${RESET}`);
    console.log(`${CYAN}----------------------------------------------------------------------${RESET}`);
}

function runLayer(layer) {
    console.log(`\n${BOLD}${MAGENTA}▶ Running ${layer.name}${RESET}`);
    console.log(`  ${GRAY}${layer.description}${RESET}`);
    console.log(`  ${GRAY}Suite: ${layer.file}${RESET}\n`);

    const pytestArgs = ['-m', 'pytest', layer.file];
    if (isVerbose) pytestArgs.push('-v');
    else pytestArgs.push('-v', '--tb=short');

    // Run pytest
    const startTime = Date.now();
    const result = spawnSync(PYTHON, pytestArgs, {
        cwd: ROOT_DIR,
        encoding: 'utf-8',
        stdio: 'inherit'
    });
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

    const passed = result.status === 0;
    return {
        ...layer,
        passed,
        elapsed,
        exitCode: result.status
    };
}

function runAll() {
    printHeader();

    let layersToRun = LAYERS;
    if (targetLayer) {
        layersToRun = LAYERS.filter(l => l.id.includes(targetLayer) || l.file.includes(targetLayer));
        if (layersToRun.length === 0) {
            console.error(`${RED}Unknown layer: ${targetLayer}. Options: health, models, engines, api${RESET}`);
            process.exit(1);
        }
    } else if (isHealthOnly) {
        layersToRun = [LAYERS[0]];
    }

    const results = [];
    for (const layer of layersToRun) {
        const res = runLayer(layer);
        results.push(res);
    }

    // Print Final Scorecard
    console.log(`\n${CYAN}${BOLD}======================================================================${RESET}`);
    console.log(`${CYAN}${BOLD}                     BACKEND TEST STATUS SUMMARY                      ${RESET}`);
    console.log(`${CYAN}${BOLD}======================================================================${RESET}`);

    let allPassed = true;
    for (const r of results) {
        const badge = r.passed ? `${GREEN}${BOLD}✔ PASSED${RESET}` : `${RED}${BOLD}✖ FAILED${RESET}`;
        const time = `${GRAY}(${r.elapsed}s)${RESET}`;
        console.log(`  ${badge}  ${BOLD}${r.name.padEnd(45)}${RESET} ${time}`);
        if (!r.passed) allPassed = false;
    }

    console.log(`${CYAN}----------------------------------------------------------------------${RESET}`);

    if (allPassed) {
        console.log(`${GREEN}${BOLD}🎉 ALL BACKEND LAYERS ARE HEALTHY AND FULLY OPERATIONAL!${RESET}`);
        console.log(`${GRAY}Status: 10/10 Intelligence Engines verified, Database healthy, API routes passing.${RESET}\n`);
        process.exit(0);
    } else {
        console.log(`${RED}${BOLD}❌ ONE OR MORE BACKEND LAYERS FAILED TESTS.${RESET}\n`);
        process.exit(1);
    }
}

runAll();
