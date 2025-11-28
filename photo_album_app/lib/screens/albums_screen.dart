import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../services/api_service.dart';
import '../models/album.dart';
import 'photos_screen.dart';
import 'album_form_screen.dart';

class AlbumsScreen extends StatefulWidget {
  const AlbumsScreen({super.key});

  @override
  State<AlbumsScreen> createState() => _AlbumsScreenState();
}

class _AlbumsScreenState extends State<AlbumsScreen> {
  final _apiService = ApiService();
  final _scrollController = ScrollController();
  List<Album> _albums = [];
  bool _isLoading = true;
  bool _isLoadingMore = false;
  String? _error;
  String? _nextPageUrl;

  @override
  void initState() {
    super.initState();
    _loadAlbums();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 200) {
      if (!_isLoadingMore && _nextPageUrl != null) {
        _loadMoreAlbums();
      }
    }
  }

  Future<void> _loadAlbums({bool isRefresh = false}) async {
    setState(() {
      _isLoading = true;
      _error = null;
      if (isRefresh) {
        _albums = [];
        _nextPageUrl = null;
      }
    });

    try {
      final result = await _apiService.getAlbums();

      if (!mounted) return;

      setState(() {
        _isLoading = false;
        if (result['success']) {
          // Handle both paginated and non-paginated responses
          final dynamic data = result['data'];
          List<dynamic> albumsJson;
          
          if (data is Map && data.containsKey('results')) {
            // Paginated response
            albumsJson = data['results'] as List<dynamic>;
            _nextPageUrl = data['next'];
          } else if (data is List) {
            // Direct list response
            albumsJson = data;
            _nextPageUrl = null;
          } else {
            _error = 'Unexpected response format: ${data.runtimeType}';
            return;
          }
          
          _albums = albumsJson.map((json) => Album.fromJson(json as Map<String, dynamic>)).toList();
        } else {
          _error = result['error'];
        }
      });
    } catch (e, stackTrace) {
      print('Error loading albums: $e');
      print('Stack trace: $stackTrace');
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _error = 'Error: $e';
      });
    }
  }

  Future<void> _loadMoreAlbums() async {
    if (_isLoadingMore || _nextPageUrl == null) return;
    
    setState(() {
      _isLoadingMore = true;
    });

    try {
      final result = await _apiService.getAlbumsPage(_nextPageUrl!);
      if (!mounted) return;
      
      setState(() {
        _isLoadingMore = false;
        if (result['success']) {
          final data = result['data'];
          List<dynamic> albumsJson = [];
          
          if (data is Map<String, dynamic>) {
            albumsJson = data['results'] as List;
            _nextPageUrl = data['next'];
          } else if (data is List) {
            albumsJson = data;
            _nextPageUrl = null;
          }
          
          final newAlbums = albumsJson.map((json) => Album.fromJson(json as Map<String, dynamic>)).toList();
          _albums.addAll(newAlbums);
        }
      });
    } catch (e) {
      print('Error loading more albums: $e');
      if (!mounted) return;
      setState(() {
        _isLoadingMore = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Albums'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAlbums,
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await _apiService.clearToken();
              if (context.mounted) {
                Navigator.of(context).pushReplacementNamed('/login');
              }
            },
          ),
        ],
      ),
      body: _buildBody(),
      floatingActionButton: FloatingActionButton(
        onPressed: _navigateToCreateAlbum,
        tooltip: 'Create Album',
        child: const Icon(Icons.add),
      ),
    );
  }

  Future<void> _navigateToCreateAlbum() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const AlbumFormScreen(),
      ),
    );

    // Reload albums if album was created
    if (result == true) {
      _loadAlbums();
    }
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
              'Error loading albums',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(_error!),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadAlbums,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_albums.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.photo_album_outlined, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            Text(
              'No albums yet',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            const Text('Create your first album to get started'),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => _loadAlbums(isRefresh: true),
      child: GridView.builder(
        controller: _scrollController,
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
          childAspectRatio: 0.85,
        ),
        itemCount: _albums.length + (_isLoadingMore ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == _albums.length) {
            // Loading indicator at the bottom
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: CircularProgressIndicator(),
              ),
            );
          }
          return _buildAlbumCard(_albums[index]);
        },
      ),
    );
  }

  Widget _buildAlbumCard(Album album) {
    return Card(
      clipBehavior: Clip.antiAlias,
      elevation: 2,
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => PhotosScreen(album: album),
            ),
          );
        },
        onLongPress: () => _showAlbumOptions(album),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Album cover/thumbnail
            Expanded(
              child: Container(
                width: double.infinity,
                color: Colors.grey[300],
                child: album.coverPhoto != null
                    ? CachedNetworkImage(
                        imageUrl: album.coverPhoto!,
                        fit: BoxFit.cover,
                        placeholder: (context, url) => const Center(
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                        errorWidget: (context, url, error) => Icon(
                          Icons.photo_album,
                          size: 64,
                          color: Colors.grey[600],
                        ),
                      )
                    : Icon(
                        Icons.photo_album,
                        size: 64,
                        color: Colors.grey[600],
                      ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    album.title,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (album.description != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      album.description!,
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(
                        album.isPublic ? Icons.public : Icons.lock,
                        size: 14,
                        color: Colors.grey[600],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        album.isPublic ? 'Public' : 'Private',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showAlbumOptions(Album album) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.edit),
                title: const Text('Edit Album'),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToEditAlbum(album);
                },
              ),
              ListTile(
                leading: const Icon(Icons.delete, color: Colors.red),
                title: const Text('Delete Album', style: TextStyle(color: Colors.red)),
                onTap: () {
                  Navigator.pop(context);
                  _confirmDeleteAlbum(album);
                },
              ),
              ListTile(
                leading: const Icon(Icons.cancel),
                title: const Text('Cancel'),
                onTap: () => Navigator.pop(context),
              ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _navigateToEditAlbum(Album album) async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AlbumFormScreen(album: album),
      ),
    );

    // Reload albums if album was updated
    if (result == true) {
      _loadAlbums();
    }
  }

  Future<void> _confirmDeleteAlbum(Album album) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Delete Album'),
          content: Text(
            'Are you sure you want to delete "${album.title}"?\n\n'
            'This will also delete all photos and videos in this album. '
            'This action cannot be undone.',
          ),
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
        );
      },
    );

    if (confirmed == true) {
      _deleteAlbum(album);
    }
  }

  Future<void> _deleteAlbum(Album album) async {
    // Show loading indicator
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Row(
          children: [
            SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            SizedBox(width: 16),
            Text('Deleting album...'),
          ],
        ),
        duration: Duration(seconds: 30),
      ),
    );

    final result = await _apiService.deleteAlbum(album.id);

    if (!mounted) return;

    // Clear the loading snackbar
    ScaffoldMessenger.of(context).clearSnackBars();

    if (result['success']) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Album deleted successfully'),
          backgroundColor: Colors.green,
        ),
      );
      _loadAlbums();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['error'] ?? 'Failed to delete album'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}
