import { drizzle } from 'drizzle-orm/mysql2';
import mysql from 'mysql2/promise';
import * as schema from './schema';
import { env } from '$env/dynamic/private';

// Assuming XAMPP/WAMP default MySQL if no ENV is set
const dbUrl = env.DATABASE_URL || 'mysql://root:@localhost:3306/atm_face_multi';

const poolConnection = mysql.createPool(dbUrl);
export const db = drizzle(poolConnection, { mode: 'default', schema });
