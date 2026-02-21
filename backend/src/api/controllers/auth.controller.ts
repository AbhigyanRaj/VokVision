import { Request, Response } from 'express';
import jwt from 'jsonwebtoken';
import { twilioService } from '../../services/twilio.service';
import { config } from '../../config';

export class AuthController {
    /**
     * Request an OTP for a phone number
     */
    static async requestOtp(req: Request, res: Response) {
        const { phoneNumber } = req.body;

        if (!phoneNumber) {
            return res.status(400).json({ message: 'Phone number is required' });
        }

        try {
            await twilioService.sendVerificationCode(phoneNumber);
            return res.status(200).json({ message: 'OTP sent successfully' });
        } catch (error: any) {
            return res.status(500).json({ message: error.message });
        }
    }

    /**
     * Verify an OTP and return a JWT
     */
    static async verifyOtp(req: Request, res: Response) {
        const { phoneNumber, code } = req.body;

        if (!phoneNumber || !code) {
            return res.status(400).json({ message: 'Phone number and code are required' });
        }

        try {
            const isValid = await twilioService.checkVerificationCode(phoneNumber, code);

            if (!isValid) {
                return res.status(401).json({ message: 'Invalid or expired OTP' });
            }

            // Generate JWT
            const token = jwt.sign(
                { phoneNumber },
                config.jwt.secret,
                { expiresIn: config.jwt.expiresIn as any }
            );

            return res.status(200).json({
                message: 'Authentication successful',
                token,
                user: { phoneNumber }
            });
        } catch (error: any) {
            return res.status(500).json({ message: error.message });
        }
    }
}
