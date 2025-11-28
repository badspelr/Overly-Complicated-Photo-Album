import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io' show Platform;
import 'package:photo_view/photo_view.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:share_plus/share_plus.dart';
import '../models/photo.dart';
import '../models/album.dart';
import '../services/api_service.dart';

class PhotoDetailScreen extends StatefulWidget {
  final Photo photo;
  final List<Photo> allPhotos;
  final int initialIndex;
  final Album album;

  const PhotoDetailScreen({
    super.key,
    required this.photo,
    required this.allPhotos,
    required this.initialIndex,
    required this.album,
  });

  @override
  State<PhotoDetailScreen> createState() => _PhotoDetailScreenState();
}

class _PhotoDetailScreenState extends State<PhotoDetailScreen> {
  final ApiService _apiService = ApiService();
  late Photo _currentPhoto;
  late int _currentIndex;

  @override
  void initState() {
    super.initState();
    _currentPhoto = widget.photo;
    _currentIndex = widget.initialIndex;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black.withOpacity(0.5),
        foregroundColor: Colors.white,
        title: Text(_currentPhoto.title),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () => _showShareDialog(context),
          ),
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () => _showEditDialog(context),
          ),
          IconButton(
            icon: const Icon(Icons.photo_album),
            onPressed: () => _setAsAlbumCover(context),
          ),
          IconButton(
            icon: const Icon(Icons.info_outline),
            onPressed: () => _showPhotoInfo(context),
          ),
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: () => _confirmDelete(context),
          ),
        ],
      ),
      body: PageView.builder(
        controller: PageController(initialPage: widget.initialIndex),
        itemCount: widget.allPhotos.length,
        onPageChanged: (index) {
          setState(() {
            _currentIndex = index;
            _currentPhoto = widget.allPhotos[index];
          });
        },
        itemBuilder: (context, index) {
          return _buildPhotoView(widget.allPhotos[index]);
        },
      ),
    );
  }

  Widget _buildPhotoView(Photo currentPhoto) {
    // For videos, show thumbnail with play button message
    if (currentPhoto.isVideo) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (currentPhoto.thumbnailUrl != null)
              Expanded(
                child: CachedNetworkImage(
                  imageUrl: currentPhoto.thumbnailUrl!,
                  fit: BoxFit.contain,
                  placeholder: (context, url) => const Center(
                    child: CircularProgressIndicator(),
                  ),
                  errorWidget: (context, url, error) => const Icon(
                    Icons.video_library,
                    size: 120,
                    color: Colors.white54,
                  ),
                ),
              )
            else
              const Icon(
                Icons.video_library,
                size: 120,
                color: Colors.white54,
              ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  const Icon(
                    Icons.play_circle_outline,
                    size: 48,
                    color: Colors.white,
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Video playback coming soon',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Video: ${currentPhoto.title}',
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 48),
          ],
        ),
      );
    }
    
    // For photos, use PhotoView for zoom/pan
    return PhotoView(
      imageProvider: CachedNetworkImageProvider(currentPhoto.imageUrl),
      minScale: PhotoViewComputedScale.contained,
      maxScale: PhotoViewComputedScale.covered * 3,
      initialScale: PhotoViewComputedScale.contained,
      heroAttributes: PhotoViewHeroAttributes(tag: 'photo-${currentPhoto.id}'),
      loadingBuilder: (context, event) {
        return Center(
          child: CircularProgressIndicator(
            value: event == null
                ? 0
                : event.cumulativeBytesLoaded / (event.expectedTotalBytes ?? 1),
          ),
        );
      },
      errorBuilder: (context, error, stackTrace) {
        return const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 64, color: Colors.white),
              SizedBox(height: 16),
              Text(
                'Failed to load image',
                style: TextStyle(color: Colors.white),
              ),
            ],
          ),
        );
      },
    );
  }

  void _showPhotoInfo(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _currentPhoto.title,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              if (_currentPhoto.description != null) ...[
                const SizedBox(height: 12),
                Text(
                  _currentPhoto.description!,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
              const SizedBox(height: 16),
              _buildInfoRow(
                Icons.calendar_today,
                'Uploaded',
                _formatDate(_currentPhoto.uploadedAt),
              ),
              const SizedBox(height: 8),
              _buildInfoRow(
                Icons.photo_size_select_actual,
                'ID',
                '#${_currentPhoto.id}',
              ),
            ],
          ),
        );
      },
    );
  }

  void _confirmDelete(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Delete ${_currentPhoto.isVideo ? 'Video' : 'Photo'}?'),
        content: Text(
          'Are you sure you want to delete "${_currentPhoto.title}"? This cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              _deletePhoto(context);
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  Future<void> _deletePhoto(BuildContext context) async {
    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );

    final result = await _apiService.deletePhoto(
      _currentPhoto.id,
      _currentPhoto.isVideo,
    );

    if (!mounted) return;
    Navigator.pop(context); // Close loading dialog

    if (result['success']) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${_currentPhoto.isVideo ? 'Video' : 'Photo'} deleted'),
        ),
      );
      // Go back to photos screen with refresh flag
      Navigator.pop(context, true);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to delete: ${result['error']}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _showEditDialog(BuildContext context) {
    final titleController = TextEditingController(text: _currentPhoto.title);
    final descriptionController = TextEditingController(
      text: _currentPhoto.description ?? '',
    );

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit Details'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: titleController,
                decoration: const InputDecoration(
                  labelText: 'Title',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _updatePhoto(
                context,
                titleController.text,
                descriptionController.text,
              );
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  Future<void> _updatePhoto(
    BuildContext context,
    String title,
    String description,
  ) async {
    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );

    final result = await _apiService.updatePhoto(
      photoId: _currentPhoto.id,
      isVideo: _currentPhoto.isVideo,
      title: title,
      description: description.isEmpty ? null : description,
    );

    if (!mounted) return;
    Navigator.pop(context); // Close loading dialog

    if (result['success']) {
      setState(() {
        _currentPhoto = Photo(
          id: _currentPhoto.id,
          title: title,
          description: description.isEmpty ? null : description,
          imageUrl: _currentPhoto.imageUrl,
          thumbnailUrl: _currentPhoto.thumbnailUrl,
          uploadedAt: _currentPhoto.uploadedAt,
          isOwner: _currentPhoto.isOwner,
          isVideo: _currentPhoto.isVideo,
          albumId: _currentPhoto.albumId,
          category: _currentPhoto.category,
        );
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Updated successfully')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to update: ${result['error']}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _setAsAlbumCover(BuildContext context) async {
    if (_currentPhoto.isVideo) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Cannot use video as album cover'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );

    final result = await _apiService.setAlbumCover(widget.album.id, _currentPhoto.id);

    if (!mounted) return;
    Navigator.pop(context); // Close loading dialog

    if (result['success']) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Album cover updated')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to set cover: ${result['error']}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _showShareDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Share Photo'),
        content: const Text('Generate a shareable link for this photo?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _generateShareLink(context);
            },
            child: const Text('Generate Link'),
          ),
        ],
      ),
    );
  }

  Future<void> _generateShareLink(BuildContext context) async {
    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );

    final result = await _apiService.createPhotoShareLink(_currentPhoto.id);

    if (!mounted) return;
    Navigator.pop(context); // Close loading dialog

    if (result['success']) {
      final shareUrl = result['data']['share_url'];
      
      // Check if we're on a mobile platform
      final bool isMobile = !kIsWeb && (Platform.isAndroid || Platform.isIOS);
      
      if (isMobile) {
        // Use native share on mobile
        try {
          await Share.share(
            shareUrl,
            subject: 'Check out this photo: ${_currentPhoto.title ?? 'Photo'}',
          );
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Share link created')),
          );
        } catch (e) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to share: $e')),
          );
        }
      } else {
        // Show copy dialog on desktop/web
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Share Link Created'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Share this link:'),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: SelectableText(
                    shareUrl,
                    style: const TextStyle(fontSize: 12),
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Link expires in 7 days',
                  style: TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Close'),
              ),
              TextButton(
                onPressed: () {
                  // Copy to clipboard
                  Clipboard.setData(ClipboardData(text: shareUrl));
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Link copied to clipboard')),
                  );
                },
                child: const Text('Copy Link'),
              ),
            ],
          ),
        );
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to create share link: ${result['error']}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.grey),
        const SizedBox(width: 8),
        Text(
          '$label: ',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        Text(value),
      ],
    );
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }
}
