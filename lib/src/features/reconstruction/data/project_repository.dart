import 'package:dio/dio.dart';
import 'package:camera/camera.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path/path.dart' as p;
import '../../authentication/data/auth_repository.dart';

class ProjectRepository {
  final Dio _dio;
  
  // Update this to your local server IP (retrieved earlier: 192.168.123.84)
  static const String _baseUrl = 'http://192.168.43.69:3000/api/v1/projects';

  ProjectRepository(this._dio);

  Future<String> createProject({
    required String name,
    required String description,
    required String ownerPhone,
    String? fcmToken,
  }) async {
    try {
      final response = await _dio.post(
        _baseUrl,
        data: {
          'name': name,
          'description': description,
          'ownerPhone': ownerPhone,
          'fcmToken': fcmToken,
        },
      );
      return response.data['_id'];
    } on DioException catch (e) {
      throw Exception(e.response?.data['message'] ?? 'Failed to create project');
    }
  }

  Future<void> uploadPhotos(String projectId, List<XFile> images) async {
    try {
      final formData = FormData();
      
      for (var image in images) {
        formData.files.add(MapEntry(
          'images',
          await MultipartFile.fromFile(
            image.path,
            filename: p.basename(image.path),
          ),
        ));
      }

      await _dio.post(
        '$_baseUrl/$projectId/upload',
        data: formData,
        onSendProgress: (count, total) {
          print('Upload progress: ${count / total}');
        },
      );
    } on DioException catch (e) {
      throw Exception(e.response?.data['message'] ?? 'Failed to upload photos');
    }
  }
}

final projectRepositoryProvider = Provider<ProjectRepository>((ref) {
  return ProjectRepository(ref.watch(dioProvider));
});
