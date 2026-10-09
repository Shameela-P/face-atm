import fs from 'fs';
import path from 'path';

const testImage = path.resolve('legacy', 'test_capture.jpg');
const b64Img = fs.readFileSync(testImage, { encoding: 'base64' });

async function run() {
    console.log("Testing SvelteKit face validation endpoint...");
    try {
        const res = await fetch('http://localhost:5173/api/face/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ imageB64: b64Img })
        });
        
        console.log(`Status: ${res.status}`);
        const data = await res.json();
        console.log("Response:", data);
    } catch (e) {
        console.error("Fetch error:", e);
    }
}

run();
