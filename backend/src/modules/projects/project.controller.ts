import { Request, Response } from 'express';
import Project, { ProjectStatus } from './project.model';

export class ProjectController {
    static async createProject(req: Request, res: Response) {
        try {
            const { name, description, ownerPhone, fcmToken } = req.body;

            const project = new Project({
                name,
                description,
                ownerPhone,
                fcmToken,
                status: ProjectStatus.PENDING
            });

            await project.save();
            console.log(`Project created: ${project._id} for phone: ${ownerPhone} with FCM Token: ${fcmToken || 'None'}`);
            return res.status(201).json(project);
        } catch (error: any) {
            return res.status(500).json({ message: error.message });
        }
    }

    static async getProjects(req: Request, res: Response) {
        try {
            const { ownerPhone } = req.query;
            const filter = ownerPhone ? { ownerPhone } : {};
            const projects = await Project.find(filter).sort({ createdAt: -1 });
            return res.status(200).json(projects);
        } catch (error: any) {
            return res.status(500).json({ message: error.message });
        }
    }

    static async getProjectById(req: Request, res: Response) {
        try {
            const project = await Project.findById(req.params.id);
            if (!project) {
                return res.status(404).json({ message: 'Project not found' });
            }
            return res.status(200).json(project);
        } catch (error: any) {
            return res.status(500).json({ message: error.message });
        }
    }

    static async uploadPhotos(req: Request, res: Response) {
        try {
            const project = await Project.findById(req.params.id);
            if (!project) {
                return res.status(404).json({ message: 'Project not found' });
            }

            const files = req.files as Express.Multer.File[];
            console.log(`Received ${files?.length || 0} files for project ${req.params.id}`);

            if (!files || files.length === 0) {
                return res.status(400).json({ message: 'No files uploaded' });
            }

            // Update project with image paths
            const imageUrls = files.map(file => `/uploads/${project._id}/${file.filename}`);
            project.imageUrls.push(...imageUrls);
            project.status = ProjectStatus.PROCESSING;
            await project.save();

            // Trigger processing job via BullMQ
            console.log(`Adding project ${project._id} to processing queue...`);
            const { addJobToQueue } = require('../../shared/utils/queue');
            await addJobToQueue(project._id.toString());
            console.log('Job added successfully.');
            
            return res.status(200).json({ 
                message: 'Photos uploaded successfully. Processing started.',
                project 
            });
        } catch (error: any) {
            return res.status(500).json({ message: error.message });
        }
    }
}
