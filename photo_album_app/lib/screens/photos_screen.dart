import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../services/api_service.dart';
import '../models/album.dart';
import '../models/photo.dart';
import 'photo_detail_screen.dart';
import 'upload_screen.dart';

class PhotosScreen extends StatefulWidget {
  final Album album;

  const PhotosScreen({super.key, required this.album});

  @override
  State<PhotosScreen> createState() => _PhotosScreenState();
}

class _PhotosScreenState extends State<PhotosScreen> {
  final _apiService = ApiService();
  final _scrollController = ScrollController();
  List<Photo> _photos = [];
  bool _isLoading = true;
  bool _isLoadingMore = false;
  String? _error;
  String? _nextPageUrl;
  int _currentPage = 1;
  
  // Bulk selection state
  bool _isSelectionMode = false;
  Set<int> _selectedPhotoIds = {};

  @override
  void initState() {
    super.initState();
    _loadPhotos();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 200) {
      // Load more when user is 200 pixels from bottom
      if (!_isLoadingMore && _nextPageUrl != null) {
        _loadMorePhotos();
      }
    }
  }

  Future<void> _loadPhotos({bool isRefresh = false}) async {
    setState(() {
      _isLoading = true;
      _error = null;
      if (isRefresh) {
        _photos = [];
        _currentPage = 1;
        _nextPageUrl = null;
      }
    });

    try {
      final result = await _apiService.getPhotos(widget.album.id);

      if (!mounted) return;

      setState(() {
        _isLoading = false;
        if (result['success']) {
          // Handle both paginated and non-paginated responses
          final dynamic data = result['data'];
          List<dynamic> photosJson;
          
          if (data is Map && data.containsKey('results')) {
            // Paginated response
            photosJson = data['results'] as List<dynamic>;
            _nextPageUrl = data['next'];
            _currentPage = 1;
          } else if (data is List) {
            // Direct list response
            photosJson = data;
            _nextPageUrl = null;
          } else {
            _error = 'Unexpected response format: ${data.runtimeType}';
            return;
          }
          
          _photos = photosJson.map((json) => Photo.fromJson(json as Map<String, dynamic>)).toList();
        } else {
          _error = result['error'];
        }
      });
    } catch (e, stackTrace) {
      print('Error loading photos: $e');
      print('Stack trace: $stackTrace');
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _error = 'Error: $e';
      });
    }
  }

  Future<void> _loadMorePhotos() async {
    if (_isLoadingMore || _nextPageUrl == null) return;

    setState(() => _isLoadingMore = true);

    try {
      final result = await _apiService.getPhotosPage(_nextPageUrl!);

      if (!mounted) return;

      setState(() {
        _isLoadingMore = false;
        if (result['success']) {
          final dynamic data = result['data'];
          
          if (data is Map && data.containsKey('results')) {
            final List<dynamic> photosJson = data['results'] as List<dynamic>;
            final newPhotos = photosJson.map((json) => Photo.fromJson(json as Map<String, dynamic>)).toList();
            _photos.addAll(newPhotos);
            _nextPageUrl = data['next'];
            _currentPage++;
          }
        }
      });
    } catch (e) {
      print('Error loading more photos: $e');
      if (!mounted) return;
      setState(() => _isLoadingMore = false);
    }
  }

  Future<void> _navigateToUpload() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => UploadScreen(album: widget.album),
      ),
    );

    // Reload photos if upload was successful
    if (result == true) {
      _loadPhotos(isRefresh: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isSelectionMode 
          ? '${_selectedPhotoIds.length} selected' 
          : widget.album.title
        ),
        leading: _isSelectionMode
          ? IconButton(
              icon: const Icon(Icons.close),
              onPressed: _cancelSelection,
              tooltip: 'Exit selection mode',
            )
          : null,
        actions: _isSelectionMode
          ? [
              IconButton(
                icon: const Icon(Icons.select_all),
                onPressed: _selectAll,
              ),
              IconButton(
                icon: const Icon(Icons.delete),
                onPressed: _selectedPhotoIds.isEmpty ? null : _bulkDelete,
              ),
            ]
          : [
              IconButton(
                icon: const Icon(Icons.checklist),
                onPressed: _enterSelectionMode,
                tooltip: 'Select multiple items',
              ),
              IconButton(
                icon: const Icon(Icons.refresh),
                onPressed: () => _loadPhotos(isRefresh: true),
                tooltip: 'Refresh',
              ),
            ],
      ),
      body: _buildBody(),
      floatingActionButton: _isSelectionMode ? null : FloatingActionButton(
        onPressed: _navigateToUpload,
        child: const Icon(Icons.add_a_photo),
      ),
    );
  }

  void _enterSelectionMode() {
    setState(() {
      _isSelectionMode = true;
      _selectedPhotoIds.clear();
    });
  }

  void _cancelSelection() {
    setState(() {
      _isSelectionMode = false;
      _selectedPhotoIds.clear();
    });
  }

  void _selectAll() {
    setState(() {
      if (_selectedPhotoIds.length == _photos.length) {
        // Deselect all
        _selectedPhotoIds.clear();
      } else {
        // Select all
        _selectedPhotoIds = _photos.map((p) => p.id).toSet();
      }
    });
  }

  void _togglePhotoSelection(int photoId) {
    setState(() {
      if (_selectedPhotoIds.contains(photoId)) {
        _selectedPhotoIds.remove(photoId);
      } else {
        _selectedPhotoIds.add(photoId);
      }
    });
  }

  Future<void> _bulkDelete() async {
    final count = _selectedPhotoIds.length;
    
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Items'),
        content: Text('Are you sure you want to delete $count item${count > 1 ? 's' : ''}? This cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    // Show loading dialog
    if (!mounted) return;
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );

    int successCount = 0;
    int failCount = 0;

    // Delete each photo individually
    for (final photoId in _selectedPhotoIds) {
      final photo = _photos.firstWhere((p) => p.id == photoId);
      final result = await _apiService.deletePhoto(photoId, photo.isVideo);
      
      if (result['success']) {
        successCount++;
      } else {
        failCount++;
      }
    }

    if (!mounted) return;
    Navigator.pop(context); // Close loading dialog

    // Show result
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          failCount == 0
            ? 'Deleted $successCount item${successCount > 1 ? 's' : ''}'
            : 'Deleted $successCount, failed $failCount',
        ),
        backgroundColor: failCount == 0 ? null : Colors.orange,
      ),
    );

    // Exit selection mode and reload
    _cancelSelection();
    _loadPhotos(isRefresh: true);
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              'Error loading photos',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(_error!),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadPhotos,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_photos.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.photo_outlined, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            Text(
              'No media yet',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            const Text('Add photos or videos to this album to get started'),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _navigateToUpload,
              icon: const Icon(Icons.add_a_photo),
              label: const Text('Upload Photos'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => _loadPhotos(isRefresh: true),
      child: GridView.builder(
        controller: _scrollController,
        padding: const EdgeInsets.all(8),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 3,
          crossAxisSpacing: 4,
          mainAxisSpacing: 4,
        ),
        itemCount: _photos.length + (_isLoadingMore ? 1 : 0),
        itemBuilder: (context, index) {
          // Show loading indicator at the bottom
          if (index == _photos.length) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: CircularProgressIndicator(),
              ),
            );
          }
          return _buildPhotoTile(_photos[index], index);
        },
      ),
    );
  }

  Widget _buildPhotoTile(Photo photo, int index) {
    final isSelected = _selectedPhotoIds.contains(photo.id);
    
    return GestureDetector(
      onTap: () async {
        if (_isSelectionMode) {
          _togglePhotoSelection(photo.id);
          return;
        }
        
        final result = await Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => PhotoDetailScreen(
              photo: photo,
              allPhotos: _photos,
              initialIndex: index,
              album: widget.album,
            ),
          ),
        );
        
        // If result is true, photo was deleted - reload photos
        if (result == true) {
          _loadPhotos(isRefresh: true);
        }
      },
      onLongPress: () {
        if (!_isSelectionMode) {
          // Show a quick feedback that long-press enters selection mode
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Selection mode activated'),
              duration: Duration(milliseconds: 500),
            ),
          );
          _enterSelectionMode();
          _togglePhotoSelection(photo.id);
        }
      },
      child: Hero(
        tag: 'photo-${photo.id}',
        child: Container(
          decoration: BoxDecoration(
            color: Colors.grey[300],
            borderRadius: BorderRadius.circular(4),
            border: _isSelectionMode && isSelected
              ? Border.all(color: Theme.of(context).primaryColor, width: 3)
              : null,
          ),
          child: Stack(
            fit: StackFit.expand,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: CachedNetworkImage(
                  imageUrl: photo.thumbnailUrl ?? photo.imageUrl,
                  fit: BoxFit.cover,
                  placeholder: (context, url) => const Center(
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  errorWidget: (context, url, error) => const Center(
                    child: Icon(Icons.broken_image, color: Colors.grey),
                  ),
                ),
              ),
              // Selection checkbox
              if (_isSelectionMode)
                Positioned(
                  top: 4,
                  right: 4,
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.black26, width: 1),
                    ),
                    child: Icon(
                      isSelected ? Icons.check_circle : Icons.circle_outlined,
                      color: isSelected ? Theme.of(context).primaryColor : Colors.grey,
                      size: 24,
                    ),
                  ),
                ),
              // Video play icon overlay
              if (photo.isVideo && !_isSelectionMode)
                Center(
                  child: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.6),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.play_arrow,
                      color: Colors.white,
                      size: 24,
                    ),
                  ),
                ),
              if (photo.title.isNotEmpty)
                Positioned(
                  bottom: 0,
                  left: 0,
                  right: 0,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.bottomCenter,
                        end: Alignment.topCenter,
                        colors: [
                          Colors.black.withOpacity(0.7),
                          Colors.transparent,
                        ],
                      ),
                    ),
                    child: Text(
                      photo.title,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
