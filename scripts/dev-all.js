import { spawn } from 'child_process';
import path from 'path';

console.log('=== Starting Secure ATM System Development Environment ===');

// 1. Spawn Python FastAPI Microservice
const isWin = process.platform === 'win32';
const pythonCmd = isWin ? 'python' : 'python3';
const mainPyPath = path.join(process.cwd(), 'fastapi_service', 'main.py');

console.log(`[Process] Launching FastAPI ML Service: ${pythonCmd} ${mainPyPath}`);
const fastapiProc = spawn(pythonCmd, [mainPyPath], {
    cwd: process.cwd(),
    stdio: 'inherit',
    shell: true
});

// 2. Spawn SvelteKit Development Server
const npmCmd = isWin ? 'npm.cmd' : 'npm';
console.log(`[Process] Launching SvelteKit Dev Server: ${npmCmd} run dev`);
const svelteProc = spawn(npmCmd, ['run', 'dev'], {
    cwd: process.cwd(),
    stdio: 'inherit',
    shell: true
});

const cleanup = () => {
    console.log('\nStopping development services...');
    fastapiProc.kill();
    svelteProc.kill();
    process.exit();
};

process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);
