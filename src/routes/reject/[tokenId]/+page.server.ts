import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { getApprovalRequest, updateApprovalRequestStatus } from '$lib/server/approvalDb';
import { getCustomerByIdFromFirebase } from '$lib/server/firebaseDb';

export const load: PageServerLoad = async ({ params }) => {
    const { tokenId } = params;
    const request = await getApprovalRequest(tokenId);
    
    if (!request) throw error(404, 'Invalid or expired approval link');

    let message = '';
    
    if (request.status === 'PENDING') {
        await updateApprovalRequestStatus(tokenId, 'REJECTED');
        message = 'You have successfully rejected the transaction attempt. The person at the ATM has been denied access.';
    } else if (request.status === 'REJECTED') {
        message = 'This transaction attempt was already rejected.';
    } else {
        message = `This request cannot be rejected because it is currently ${request.status}.`;
    }
    
    return {
        message
    };
};
