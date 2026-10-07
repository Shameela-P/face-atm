import { fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getSettingsFromFirebase, updateSettingsInFirebase, getAuditLogsFromFirebase } from '$lib/server/firebaseDb';

export const load: PageServerLoad = async () => {
    try {
        const [settings, auditLogs] = await Promise.all([
            getSettingsFromFirebase().catch(() => ({
                appName: 'Secure ATM Facial Verification System',
                mlServiceUrl: 'http://localhost:8000',
                sessionTimeoutMins: 15,
                maxFailedAttempts: 3,
                emailAlertsEnabled: true,
                incidentNotificationsEnabled: true
            })),
            getAuditLogsFromFirebase().catch(() => [])
        ]);

        return {
            settings,
            auditLogs
        };
    } catch (e) {
        console.error('[Firebase Settings Load Error]:', e);
        return {
            settings: {
                appName: 'Secure ATM Facial Verification System',
                mlServiceUrl: 'http://localhost:8000',
                sessionTimeoutMins: 15,
                maxFailedAttempts: 3,
                emailAlertsEnabled: true,
                incidentNotificationsEnabled: true
            },
            auditLogs: []
        };
    }
};

export const actions: Actions = {
    updateSettings: async ({ request }) => {
        const formData = await request.formData();
        const appName = formData.get('appName')?.toString() || 'Secure ATM Facial Verification System';
        const mlServiceUrl = formData.get('mlServiceUrl')?.toString() || 'http://localhost:8000';
        const sessionTimeoutMins = parseInt(formData.get('sessionTimeoutMins')?.toString() || '15', 10);
        const maxFailedAttempts = parseInt(formData.get('maxFailedAttempts')?.toString() || '3', 10);
        const emailAlertsEnabled = formData.get('emailAlertsEnabled') === 'on';

        const success = await updateSettingsInFirebase({
            appName,
            mlServiceUrl,
            sessionTimeoutMins,
            maxFailedAttempts,
            emailAlertsEnabled
        });

        if (!success) {
            return fail(500, { error: 'Failed to save configuration settings to Firebase.' });
        }

        return { success: true, message: 'Application configuration settings updated successfully.' };
    }
};
