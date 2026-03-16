import mongoose, { Schema, Document } from 'mongoose';

export enum ProjectStatus {
    PENDING = 'PENDING',
    PROCESSING = 'PROCESSING',
    COMPLETED = 'COMPLETED',
    FAILED = 'FAILED'
}

export interface IProject extends Document {
    name: string;
    description?: string;
    ownerPhone: string;
    status: ProjectStatus;
    fcmToken?: string;
    imageUrls: string[];
    modelUrl?: string;
    error?: string;
    createdAt: Date;
    updatedAt: Date;
}

const ProjectSchema: Schema = new Schema({
    name: { type: String, required: true },
    description: { type: String },
    ownerPhone: { type: String, required: true },
    status: {
        type: String,
        enum: Object.values(ProjectStatus),
        default: ProjectStatus.PENDING
    },
    fcmToken: { type: String },
    imageUrls: [{ type: String }],
    modelUrl: { type: String },
    error: { type: String }
}, {
    timestamps: true
});

export default mongoose.model<IProject>('Project', ProjectSchema);
