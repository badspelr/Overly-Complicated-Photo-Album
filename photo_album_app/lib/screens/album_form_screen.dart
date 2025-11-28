import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/album.dart';

class AlbumFormScreen extends StatefulWidget {
  final Album? album; // null for create, Album instance for edit

  const AlbumFormScreen({super.key, this.album});

  @override
  State<AlbumFormScreen> createState() => _AlbumFormScreenState();
}

class _AlbumFormScreenState extends State<AlbumFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _apiService = ApiService();
  
  bool _isPublic = false;
  bool _isLoading = false;
  int? _selectedCategoryId;

  @override
  void initState() {
    super.initState();
    // Pre-fill form if editing
    if (widget.album != null) {
      _titleController.text = widget.album!.title;
      _descriptionController.text = widget.album!.description ?? '';
      _isPublic = widget.album!.isPublic;
      _selectedCategoryId = widget.album!.category;
    }
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _saveAlbum() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final Map<String, dynamic> result;
    
    if (widget.album == null) {
      // Create new album
      result = await _apiService.createAlbum(
        title: _titleController.text.trim(),
        description: _descriptionController.text.trim(),
        isPublic: _isPublic,
        categoryId: _selectedCategoryId,
      );
    } else {
      // Update existing album
      result = await _apiService.updateAlbum(
        albumId: widget.album!.id,
        title: _titleController.text.trim(),
        description: _descriptionController.text.trim(),
        isPublic: _isPublic,
        categoryId: _selectedCategoryId,
      );
    }

    setState(() => _isLoading = false);

    if (!mounted) return;

    if (result['success']) {
      // Return true to indicate success
      Navigator.of(context).pop(true);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(widget.album == null 
            ? 'Album created successfully' 
            : 'Album updated successfully'),
          backgroundColor: Colors.green,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['error'] ?? 'Failed to save album'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEditing = widget.album != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEditing ? 'Edit Album' : 'Create Album'),
        actions: [
          if (_isLoading)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            )
          else
            IconButton(
              icon: const Icon(Icons.check),
              onPressed: _saveAlbum,
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Title field
            TextFormField(
              controller: _titleController,
              decoration: const InputDecoration(
                labelText: 'Album Title',
                hintText: 'Enter album name',
                prefixIcon: Icon(Icons.title),
                border: OutlineInputBorder(),
              ),
              textCapitalization: TextCapitalization.words,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter a title';
                }
                if (value.trim().length > 100) {
                  return 'Title must be less than 100 characters';
                }
                return null;
              },
              enabled: !_isLoading,
            ),
            const SizedBox(height: 16),

            // Description field
            TextFormField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Description (Optional)',
                hintText: 'Enter album description',
                prefixIcon: Icon(Icons.description),
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
              textCapitalization: TextCapitalization.sentences,
              enabled: !_isLoading,
            ),
            const SizedBox(height: 16),

            // Public/Private toggle
            Card(
              child: SwitchListTile(
                title: const Text('Public Album'),
                subtitle: Text(
                  _isPublic 
                    ? 'Visible to all users' 
                    : 'Only visible to you and shared users',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
                value: _isPublic,
                onChanged: _isLoading ? null : (value) {
                  setState(() => _isPublic = value);
                },
                secondary: Icon(
                  _isPublic ? Icons.public : Icons.lock,
                  color: _isPublic ? Colors.green : Colors.orange,
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Category selector (simplified for now)
            // TODO: Load categories from API and show dropdown
            Card(
              child: ListTile(
                leading: const Icon(Icons.category),
                title: const Text('Category'),
                subtitle: Text(
                  _selectedCategoryId != null 
                    ? 'Category ID: $_selectedCategoryId' 
                    : 'No category selected',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: _isLoading ? null : () {
                  // TODO: Show category picker
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Category selection coming soon'),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 32),

            // Save button (alternative to app bar button)
            if (!_isLoading)
              ElevatedButton.icon(
                onPressed: _saveAlbum,
                icon: const Icon(Icons.save),
                label: Text(isEditing ? 'Update Album' : 'Create Album'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.all(16),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
