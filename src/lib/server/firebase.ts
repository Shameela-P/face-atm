import { initializeApp, getApps, getApp } from 'firebase/app';
import { getStorage, ref, uploadString, getDownloadURL } from 'firebase/storage';
import fs from 'fs';
import path from 'path';

// Firebase configuration for project: face-76a11
const firebaseConfig = {
  apiKey: "AIzaSyAedUN6B2xOjgJsvpEL1R_aiXY4pV12JBA",
  authDomain: "face-76a11.firebaseapp.com",
  databaseURL: "https://face-76a11-default-rtdb.firebaseio.com",
  projectId: "face-76a11",
  storageBucket: "face-76a11.firebasestorage.app",
  messagingSenderId: "981118590426",
  appId: "1:981118590426:web:c05f36b38fc65fee0834e3",
  measurementId: "G-V6BCDE1BK1"
};

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
export const firebaseStorage = getStorage(app);

/**
 * Uploads a base64 image string to Firebase Storage and returns its download URL or reference path.
 * Standard path structures required by project rules:
 * - Registered Original Face: `face-images/registered/{customerId}/original-face.jpg`
 * - Attempted Unauthorized Face: `face-images/security-incidents/{customerId}/{incidentId}/attempted-face.jpg`
 */
export async function uploadImageToFirebaseStorage(base64DataUrl: string, storagePath: string): Promise<string> {
    try {
        const storageRef = ref(firebaseStorage, storagePath);
        // Clean base64 header if present
        const cleanB64 = base64DataUrl.includes(',') ? base64DataUrl : `data:image/jpeg;base64,${base64DataUrl}`;
        
        await uploadString(storageRef, cleanB64, 'data_url');
        const downloadUrl = await getDownloadURL(storageRef);
        console.log(`[Firebase Storage] Uploaded image successfully to ${storagePath} -> ${downloadUrl}`);
        return downloadUrl;
    } catch (err) {
        console.warn(`[Firebase Storage Warning] Could not upload directly to Firebase Storage (${storagePath}):`, err);
        // Local fallback preservation
        const fallbackPath = `/uploads/${storagePath.replace(/\//g, '_')}`;
        return downloadUrlFallback(base64DataUrl, storagePath);
    }
}

function downloadUrlFallback(base64DataUrl: string, storagePath: string): string {
    try {
        const cleanB64 = base64DataUrl.replace(/^data:image\/\w+;base64,/, '');
        const buffer = Buffer.from(cleanB64, 'base64');
        const filename = storagePath.replace(/\//g, '_');
        const localDir = path.join(process.cwd(), 'static', 'uploads');
        if (!fs.existsSync(localDir)) {
            fs.mkdirSync(localDir, { recursive: true });
        }
        const filePath = path.join(localDir, filename);
        fs.writeFileSync(filePath, buffer);
        return `/uploads/${filename}`;
    } catch (e) {
        return '';
    }
}
