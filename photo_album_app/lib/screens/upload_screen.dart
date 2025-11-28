import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import '../services/api_service.dart';
import '../models/album.dart';

class UploadScreen extends StatefulWidget {
  final Album album;

  const UploadScreen({super.key, required this.album});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  final _apiService = ApiService();
  final _imagePicker = ImagePicker();
  final List<String> _selectedFiles = [];
  bool _isUploading = false;
  double _uploadProgress = 0.0;
  int _uploadedCount = 0;

  Future<void> _pickFromCamera() async {
    final XFile? photo = await _imagePicker.pickImage(
      source: ImageSource.camera,
      imageQuality: 85,
    );

    if (photo != null) {
      setState(() => _selectedFiles.add(photo.path));
    }
  }

  Future<void> _pickFromGallery() async {
    final List<XFile> photos = await _imagePicker.pickMultiImage(
      imageQuality: 85,
    );

    if (photos.isNotEmpty) {
      setState(() {
        _selectedFiles.addAll(photos.map((p) => p.path));
      });
    }
  }

  Future<void> _pickFiles() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
      allowMultiple: true,
    );

    if (result != null) {
      setState(() {
        _selectedFiles.addAll(result.paths.whereType<String>());
      });
    }
  }

  void _removeFile(int index) {
    setState(() => _selectedFiles.removeAt(index));
  }

  Future<void> _uploadPhotos() async {
    if (_selectedFiles.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one photo')),
      );
      return;
    }

    setState(() {
      _isUploading = true;
      _uploadedCount = 0;
      _uploadProgress = 0.0;
    });

    for (int i = 0; i < _selectedFiles.length; i++) {
      final result = await _apiService.uploadPhoto(
        widget.album.id,
        _selectedFiles[i],
      );

      setState(() {
        _uploadedCount = i + 1;
        _uploadProgress = (_uploadedCount / _selectedFiles.length);
      });

      if (!result['success']) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to upload: ${_selectedFiles[i]}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }

    setState(() => _isUploading = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Uploaded $_uploadedCount of ${_selectedFiles.length} photos'),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.pop(context, true); // Return true to indicate photos were uploaded
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Upload to ${widget.album.title}'),
      ),
      body: Column(
        children: [
          // Selection buttons
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  onPressed: _isUploading ? null : _pickFromCamera,
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Camera'),
                ),
                ElevatedButton.icon(
                  onPressed: _isUploading ? null : _pickFromGallery,
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Gallery'),
                ),
                ElevatedButton.icon(
                  onPressed: _isUploading ? null : _pickFiles,
                  icon: const Icon(Icons.folder_open),
                  label: const Text('Files'),
                ),
              ],
            ),
          ),

          // Selected files grid
          Expanded(
            child: _selectedFiles.isEmpty
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.add_photo_alternate, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text('No photos selected'),
                        SizedBox(height: 8),
                        Text('Choose photos to upload', style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  )
                : GridView.builder(
                    padding: const EdgeInsets.all(16),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 3,
                      crossAxisSpacing: 8,
                      mainAxisSpacing: 8,
                    ),
                    itemCount: _selectedFiles.length,
                    itemBuilder: (context, index) {
                      return _buildFilePreview(_selectedFiles[index], index);
                    },
                  ),
          ),

          // Upload progress
          if (_isUploading) ...[
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  LinearProgressIndicator(value: _uploadProgress),
                  const SizedBox(height: 8),
                  Text('Uploading $_uploadedCount of ${_selectedFiles.length}...'),
                ],
              ),
            ),
          ],

          // Upload button
          Padding(
            padding: const EdgeInsets.all(16),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isUploading ? null : _uploadPhotos,
                icon: _isUploading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.cloud_upload),
                label: Text(_isUploading
                    ? 'Uploading...'
                    : 'Upload ${_selectedFiles.length} photo${_selectedFiles.length != 1 ? 's' : ''}'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilePreview(String filePath, int index) {
    return Stack(
      fit: StackFit.expand,
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: Image.file(
            File(filePath),
            fit: BoxFit.cover,
          ),
        ),
        // Remove button
        Positioned(
          top: 4,
          right: 4,
          child: GestureDetector(
            onTap: () => _removeFile(index),
            child: Container(
              padding: const EdgeInsets.all(4),
              decoration: const BoxDecoration(
                color: Colors.black54,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.close,
                color: Colors.white,
                size: 16,
              ),
            ),
          ),
        ),
      ],
    );
  }
}
