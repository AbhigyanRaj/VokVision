import { Router } from 'express';
import { ProjectController } from './project.controller';
import { upload } from '../../shared/middleware/upload.middleware';

const router = Router();

router.post('/', ProjectController.createProject);
router.get('/', ProjectController.getProjects);
router.get('/:id', ProjectController.getProjectById);
router.post('/:id/upload', upload.array('images', 50), ProjectController.uploadPhotos);

export default router;
