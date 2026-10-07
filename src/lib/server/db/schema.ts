import { mysqlTable, serial, text, int, timestamp, varchar, bigint } from 'drizzle-orm/mysql-core';
import { relations } from 'drizzle-orm';

// EXISTING TABLES FROM LEGACY DATABASE (DO NOT MODIFY UNNECESSARILY)

export const admin = mysqlTable('admin', {
    username: varchar('username', { length: 20 }).notNull().primaryKey(),
    password: varchar('password', { length: 20 }).notNull(),
    amount: int('amount').notNull(),
    email: varchar('email', { length: 40 }).notNull()
});

export const register = mysqlTable('register', {
    id: int('id').notNull().primaryKey(),
    name: varchar('name', { length: 20 }).notNull(),
    address: varchar('address', { length: 200 }).notNull(),
    mobile: bigint('mobile', { mode: 'number' }).notNull(),
    email: varchar('email', { length: 50 }).notNull(),
    accno: varchar('accno', { length: 20 }).notNull(),
    card: varchar('card', { length: 20 }).notNull(),
    bank: varchar('bank', { length: 20 }).notNull(),
    branch: varchar('branch', { length: 20 }).notNull(),
    deposit: int('deposit').notNull(),
    username: varchar('username', { length: 20 }).notNull(),
    password: varchar('password', { length: 20 }).notNull(),
    rdate: varchar('rdate', { length: 20 }).notNull(),
    aadhar1: varchar('aadhar1', { length: 20 }).notNull(),
    aadhar2: varchar('aadhar2', { length: 20 }).notNull(),
    aadhar3: varchar('aadhar3', { length: 20 }).notNull(),
    face_st: int('face_st').notNull(),
    fimg: varchar('fimg', { length: 30 }).notNull(),
    otp: varchar('otp', { length: 20 }).notNull(),
    allow_st: int('allow_st').notNull(),
    pinno: varchar('pinno', { length: 20 }).notNull()
});

export const user_account = mysqlTable('user_account', {
    id: int('id').notNull().primaryKey(),
    rid: int('rid').notNull().references(() => register.id),
    bank: varchar('bank', { length: 200 }).notNull(),
    account: varchar('account', { length: 200 }).notNull(),
    ifsc_code: varchar('ifsc_code', { length: 200 }).notNull(),
    branch: varchar('branch', { length: 200 }).notNull(),
    deposit: varchar('deposit', { length: 200 }).notNull()
});

export const event = mysqlTable('event', {
    id: int('id').notNull().primaryKey(),
    name: varchar('name', { length: 50 }).notNull(),
    accno: varchar('accno', { length: 20 }).notNull(),
    amount: int('amount').notNull(),
    rdate: varchar('rdate', { length: 50 }).notNull(),
    user_id: int('user_id').notNull().references(() => register.id)
});

export const vt_face = mysqlTable('vt_face', {
    id: serial('id').primaryKey(),
    vid: int('vid').notNull().references(() => register.id),
    vface: text('vface').notNull(),
    embedding: text('embedding')
});

export const numbers = mysqlTable('numbers', {
    id: int('id').notNull().primaryKey(),
    number: int('number').notNull()
});

// NEW TABLES: Minimum required additions for the new Security Workflow
// (Security Incidents, Approvals, and Complaints)

export const security_incidents = mysqlTable('security_incidents', {
    id: serial('id').primaryKey(),
    rid: int('rid').notNull().references(() => register.id),
    card: varchar('card', { length: 20 }).notNull(),
    atmId: varchar('atm_id', { length: 20 }).notNull(),
    attemptNumber: int('attempt_number').notNull().default(1),
    capturedImage: text('captured_image'),
    status: varchar('status', { length: 50 }).notNull().default('PENDING'),
    authorizedAmount: int('authorized_amount'),
    createdAt: timestamp('created_at').defaultNow().notNull()
});

export const complaints = mysqlTable('complaints', {
    id: serial('id').primaryKey(),
    rid: int('rid').notNull().references(() => register.id),
    incidentId: int('incident_id').references(() => security_incidents.id),
    description: text('description').notNull(),
    status: varchar('status', { length: 20 }).notNull().default('PENDING'),
    adminNotes: text('admin_notes'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    resolvedAt: timestamp('resolved_at')
});

// Relations Map
export const relationsConfig = {
    register: relations(register, ({ many }) => ({
        accounts: many(user_account),
        events: many(event),
        faces: many(vt_face),
        incidents: many(security_incidents),
        complaints: many(complaints)
    })),
    user_account: relations(user_account, ({ one }) => ({
        user: one(register, { fields: [user_account.rid], references: [register.id] })
    })),
    event: relations(event, ({ one }) => ({
        user: one(register, { fields: [event.user_id], references: [register.id] })
    })),
    vt_face: relations(vt_face, ({ one }) => ({
        user: one(register, { fields: [vt_face.vid], references: [register.id] })
    })),
    security_incidents: relations(security_incidents, ({ one, many }) => ({
        user: one(register, { fields: [security_incidents.rid], references: [register.id] }),
        complaints: many(complaints)
    })),
    complaints: relations(complaints, ({ one }) => ({
        user: one(register, { fields: [complaints.rid], references: [register.id] }),
        incident: one(security_incidents, { fields: [complaints.incidentId], references: [security_incidents.id] })
    }))
};
