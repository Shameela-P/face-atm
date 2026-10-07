import type { PageServerLoad } from './$types';
import { 
    getCustomersFromFirebase, 
    getCardsCountFromFirebase, 
    getAllTransactionsFromFirebase, 
    getSecurityIncidentsFromFirebase,
    getFaceVerificationsFromFirebase,
    getComplaintsFromFirebase
} from '$lib/server/firebaseDb';
import { checkMlServiceHealth } from '$lib/server/mlService';

export const load: PageServerLoad = async () => {
    try {
        const [customers, cardsCount, transactions, incidents, verifications, complaints, mlHealth] = await Promise.all([
            getCustomersFromFirebase().catch(() => []),
            getCardsCountFromFirebase().catch(() => 0),
            getAllTransactionsFromFirebase().catch(() => []),
            getSecurityIncidentsFromFirebase().catch(() => []),
            getFaceVerificationsFromFirebase().catch(() => []),
            getComplaintsFromFirebase().catch(() => []),
            checkMlServiceHealth().catch(() => ({ online: false }))
        ]);

        const totalCustomers = customers.length;
        const totalCards = cardsCount || customers.length;
        const totalTransactions = transactions.length;

        const matchVerifications = verifications.filter(v => v.result === 'MATCH').length;
        const mismatchVerifications = verifications.filter(v => v.result === 'MISMATCH' || v.result === 'SPOOF').length;

        const successfulVerificationsCount = matchVerifications;
        const failedVerificationsCount = Math.max(mismatchVerifications, incidents.length);
        const securityIncidentsCount = incidents.length;

        const pendingComplaintsCount = complaints.filter(c => c.status === 'OPEN' || c.status === 'IN_PROGRESS').length;
        const resolvedComplaintsCount = complaints.filter(c => c.status === 'RESOLVED' || c.status === 'CLOSED').length;

        // Recent Security Alerts (latest 5)
        const recentAlerts = incidents.slice(0, 5).map(inc => {
            const rawCard = inc.cardNumber || '0000000000';
            const maskedCard = rawCard.length >= 4 ? `**** **** ${rawCard.slice(-4)}` : '**** **** ****';
            
            return {
                id: inc.id,
                account: maskedCard,
                type: inc.incidentType || 'UNAUTHORIZED_ATTEMPT',
                status: inc.status || 'UNAUTHORIZED_ATTEMPT',
                time: formatRelativeTime(inc.timestamp)
            };
        });

        return {
            stats: {
                totalCustomers,
                totalCards,
                totalTransactions,
                successfulVerificationsCount,
                failedVerificationsCount,
                securityIncidentsCount,
                pendingComplaintsCount,
                resolvedComplaintsCount
            },
            recentAlerts,
            systemStatus: {
                firebaseRtdb: true,
                firebaseStorage: true,
                fastApiMlService: mlHealth.online
            }
        };
    } catch (err) {
        console.error('[Admin Dashboard Load Error]:', err);
        return {
            stats: {
                totalCustomers: 0,
                totalCards: 0,
                totalTransactions: 0,
                successfulVerificationsCount: 0,
                failedVerificationsCount: 0,
                securityIncidentsCount: 0,
                pendingComplaintsCount: 0,
                resolvedComplaintsCount: 0
            },
            recentAlerts: [],
            systemStatus: {
                firebaseRtdb: false,
                firebaseStorage: false,
                fastApiMlService: false
            }
        };
    }
};

function formatRelativeTime(timestampStr: string): string {
    if (!timestampStr) return 'Recently';
    try {
        const date = new Date(timestampStr);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays === 1) return 'Yesterday';
        return `${diffDays} days ago`;
    } catch (e) {
        return 'Recently';
    }
}
