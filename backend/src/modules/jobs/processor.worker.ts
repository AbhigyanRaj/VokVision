import { Worker, Job } from 'bullmq';
import { config } from '../../shared/config';
import IORedis from 'ioredis';
import Project, { ProjectStatus } from '../projects/project.model';
import { FcmService } from '../../shared/services/fcm.service';

const connection = {
    url: config.redis.url,
    maxRetriesPerRequest: null,
};

export const setupWorker = () => {
    const worker = new Worker('reconstruction-processing', async (job: Job) => {
        const { projectId } = job.data;
        console.log(`Processing project: ${projectId}`);

        try {
            const project = await Project.findById(projectId);
            if (!project) {
                console.error(`Project ${projectId} not found`);
                return;
            }

            console.log(`Starting processing for project: ${projectId}`);
            
            // Simulate reconstruction pipeline (e.g., 10 seconds)
            await new Promise(resolve => setTimeout(resolve, 10000));

            const downloadUrl = `http://${config.network.localIp}:${config.port}/models/${projectId}/output.glb`;
            
            project.status = ProjectStatus.COMPLETED;
            project.modelUrl = downloadUrl;
            await project.save();

            if (project.fcmToken) {
                console.log(`Sending completion notification to device: ${project.fcmToken}`);
                try {
                    await FcmService.sendNotification(
                        project.fcmToken,
                        'Reconstruction Complete',
                        `Your 3D model for "${project.name}" is ready!`,
                        {
                            projectId,
                            downloadUrl,
                            type: 'RECONSTRUCTION_COMPLETE'
                        }
                    );
                    console.log('Notification sent successfully.');
                } catch (error) {
                    console.error('Failed to send FCM notification:', error);
                }
            } else {
                console.log(`No FCM token found for project ${projectId}. Skipping notification.`);
            }

            console.log(`Completed processing for project: ${projectId}`);
        } catch (error) {
            console.error(`Error processing job ${job.id}:`, error);
            throw error;
        }
    }, { connection });

    worker.on('completed', (job) => {
        console.log(`Job ${job.id} has completed!`);
    });

    worker.on('failed', (job, err) => {
        console.error(`Job ${job?.id} has failed with ${err.message}`);
    });

    return worker;
};
