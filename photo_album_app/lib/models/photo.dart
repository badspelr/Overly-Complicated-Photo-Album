class Photo {
  final int id;
  final String title;
  final String? description;
  final int? albumId;
  final int? category;
  final String imageUrl;
  final String? thumbnailUrl;
  final DateTime uploadedAt;
  final bool isOwner;
  final bool isVideo;

  Photo({
    required this.id,
    required this.title,
    this.description,
    this.albumId,
    this.category,
    required this.imageUrl,
    this.thumbnailUrl,
    required this.uploadedAt,
    required this.isOwner,
    this.isVideo = false,
  });

  factory Photo.fromJson(Map<String, dynamic> json) {
    // Check if this is a video or photo
    final bool hasVideo = json.containsKey('video');
    
    return Photo(
      id: json['id'],
      title: json['title'] ?? '',
      description: json['description'],
      albumId: json['album'],
      category: json['category'],
      imageUrl: hasVideo ? json['video'] : json['image'],
      thumbnailUrl: json['thumbnail'],
      uploadedAt: DateTime.parse(json['uploaded_at']),
      isOwner: json['is_owner'] ?? false,
      isVideo: hasVideo,
    );
  }
}
