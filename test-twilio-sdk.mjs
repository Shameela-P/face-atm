import dotenv from 'dotenv';
import twilio from 'twilio';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.resolve(__dirname, '.env') });

const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const fromPhoneNumber = process.env.TWILIO_PHONE_NUMBER;
const mobile = '6383649156';

const otp = Math.floor(100000 + Math.random() * 900000).toString(); // 6-digit OTP

async function testOtpSms() {
    console.log('Testing SMS API using the Twilio Node.js SDK...');
    
    if (!accountSid || !authToken || !fromPhoneNumber) {
        console.error('Error: Missing Twilio credentials in .env');
        process.exit(1);
    }

    const client = twilio(accountSid, authToken);
    const formattedTo = `+91${mobile}`;

    try {
        const message = await client.messages.create({
            body: `Hello from twilio-node`,
            to: formattedTo,
            from: fromPhoneNumber,
        });

        console.log('API connection successful. OTP SMS accepted by the provider.');
        console.log('Delivery SID:', message.sid);
        console.log('Status:', message.status);
        console.log(`\n(For the purpose of this test, the generated OTP is: ${otp})`);
        console.log('Please check your mobile phone to see if it arrived.');
        
    } catch (e) {
        console.error('Error connecting to SMS API:');
        console.error(e);
        process.exit(1);
    }
}

testOtpSms();
