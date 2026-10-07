import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions = {
    default: async ({ request, cookies }) => {
        const data = await request.formData();
        const username = data.get('username')?.toString().trim();
        const password = data.get('password')?.toString().trim();

        if (!username || !password) {
            return fail(400, { error: 'Email and password are required', username });
        }

        // Fixed Admin Credential Check
        if (username === 'sham@gmail.com' && password === 'sham@123') {
            cookies.set('admin_auth', 'true', {
                path: '/',
                httpOnly: true,
                sameSite: 'lax',
                maxAge: 60 * 60 * 8 // 8 hours
            });
            cookies.set('admin_user', 'sham@gmail.com', {
                path: '/',
                httpOnly: true,
                sameSite: 'lax',
                maxAge: 60 * 60 * 8
            });

            throw redirect(303, '/admin');
        } else {
            return fail(401, { error: 'Invalid Admin credentials. Access denied.', username });
        }
    }
} satisfies Actions;
