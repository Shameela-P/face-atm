import { fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getComplaintsFromFirebase, updateComplaintInFirebase, createComplaintInFirebase } from '$lib/server/firebaseDb';

export const load: PageServerLoad = async () => {
    try {
        const complaints = await getComplaintsFromFirebase();
        return { complaints };
    } catch (e) {
        console.error('[Firebase Complaints Load Error]:', e);
        return { complaints: [] };
    }
};

export const actions: Actions = {
    updateComplaint: async ({ request }) => {
        const formData = await request.formData();
        const complaintId = formData.get('complaintId')?.toString();
        const status = formData.get('status')?.toString() as 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
        const priority = formData.get('priority')?.toString() as 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
        const adminResponse = formData.get('adminResponse')?.toString();

        if (!complaintId || !status) {
            return fail(400, { error: 'Complaint ID and Status are required.' });
        }

        const success = await updateComplaintInFirebase({
            complaintId,
            status,
            priority,
            adminResponse
        });

        if (!success) {
            return fail(500, { error: 'Failed to update complaint record in Firebase.' });
        }

        return { success: true, message: `Complaint ${complaintId} updated successfully.` };
    }
};
