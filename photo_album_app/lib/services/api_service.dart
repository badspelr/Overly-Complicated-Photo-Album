import 'dart:convert';
import 'dart:io' show Platform;
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // Automatically detect platform and use correct URL
  // Android emulator: 10.0.2.2:8000 (maps to host's localhost)
  // iOS simulator: localhost:8000
  // Linux/Desktop: localhost:8000
  static String get baseUrl {
    if (Platform.isAndroid) {
      return 'http://10.0.2.2:8000';
    } else {
      return 'http://localhost:8000';
    }
  }
  
  String? _authToken;
  
  // Singleton pattern
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  // Initialize and load saved token
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _authToken = prefs.getString('auth_token');
  }

  // Save token to local storage
  Future<void> _saveToken(String token) async {
    _authToken = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  // Clear token (logout)
  Future<void> clearToken() async {
    _authToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }

  // Check if user is logged in
  bool get isLoggedIn => _authToken != null;

  // Get headers with authentication
  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    if (_authToken != null) 'Authorization': 'Token $_authToken',
  };

  // Login
  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['token'] != null) {
          await _saveToken(data['token']);
        }
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Login failed: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Register
  Future<Map<String, dynamic>> register(
    String username,
    String email,
    String password,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/register/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Registration failed: ${response.body}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Get albums
  Future<Map<String, dynamic>> getAlbums() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/albums/'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Failed to load albums: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Get albums page (for pagination)
  Future<Map<String, dynamic>> getAlbumsPage(String url) async {
    try {
      final response = await http.get(
        Uri.parse(url),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Failed to load albums: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Create album
  Future<Map<String, dynamic>> createAlbum({
    required String title,
    String? description,
    bool isPublic = false,
    int? categoryId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/albums/'),
        headers: _headers,
        body: jsonEncode({
          'title': title,
          'description': description ?? '',
          'is_public': isPublic,
          if (categoryId != null) 'category': categoryId,
        }),
      );

      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Failed to create album: ${response.body}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Update album
  Future<Map<String, dynamic>> updateAlbum({
    required int albumId,
    required String title,
    String? description,
    bool? isPublic,
    int? categoryId,
  }) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/api/albums/$albumId/'),
        headers: _headers,
        body: jsonEncode({
          'title': title,
          'description': description ?? '',
          if (isPublic != null) 'is_public': isPublic,
          if (categoryId != null) 'category': categoryId,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Failed to update album: ${response.body}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Delete album
  Future<Map<String, dynamic>> deleteAlbum(int albumId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/api/albums/$albumId/'),
        headers: _headers,
      );

      if (response.statusCode == 204) {
        return {'success': true};
      } else {
        return {
          'success': false,
          'error': 'Failed to delete album: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Get photos from an album
  Future<Map<String, dynamic>> getPhotos(int albumId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/albums/$albumId/media/'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Failed to load photos: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Get photos by full URL (for pagination)
  Future<Map<String, dynamic>> getPhotosPage(String url) async {
    try {
      final response = await http.get(
        Uri.parse(url),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Failed to load photos: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Upload photo
  Future<Map<String, dynamic>> uploadPhoto(
    int albumId,
    String filePath,
  ) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/api/upload/'),
      );

      if (_authToken != null) {
        request.headers['Authorization'] = 'Token $_authToken';
      }

      request.fields['album_id'] = albumId.toString();
      request.files.add(await http.MultipartFile.fromPath('file', filePath));

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Upload failed: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Delete photo or video
  Future<Map<String, dynamic>> deletePhoto(int photoId, bool isVideo) async {
    try {
      final endpoint = isVideo ? 'videos' : 'photos';
      final response = await http.delete(
        Uri.parse('$baseUrl/api/$endpoint/$photoId/'),
        headers: _headers,
      );

      if (response.statusCode == 204) {
        return {'success': true};
      } else {
        return {
          'success': false,
          'error': 'Failed to delete: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Update photo or video metadata
  Future<Map<String, dynamic>> updatePhoto({
    required int photoId,
    required bool isVideo,
    String? title,
    String? description,
    String? dateTaken,
  }) async {
    try {
      final endpoint = isVideo ? 'videos' : 'photos';
      final body = <String, dynamic>{};
      
      if (title != null) body['title'] = title;
      if (description != null) body['description'] = description;
      if (dateTaken != null) body['date_taken'] = dateTaken;

      final response = await http.patch(
        Uri.parse('$baseUrl/api/$endpoint/$photoId/'),
        headers: _headers,
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Failed to update: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Set album cover photo
  Future<Map<String, dynamic>> setAlbumCover(int albumId, int photoId) async {
    try {
      final response = await http.patch(
        Uri.parse('$baseUrl/api/albums/$albumId/'),
        headers: _headers,
        body: jsonEncode({'cover_photo': photoId}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Failed to set cover: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Create photo share link
  Future<Map<String, dynamic>> createPhotoShareLink(int photoId, {int expiresDays = 7}) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/photos/$photoId/share/'),
        headers: _headers,
        body: jsonEncode({'expires_days': expiresDays}),
      );

      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Failed to create share link: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
}
