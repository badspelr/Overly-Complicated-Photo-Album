class Album {
  final int id;
  final String title;
  final String? description;
  final Owner owner;
  final int? category;
  final bool isPublic;
  final DateTime createdAt;
  final bool isOwner;
  final String? coverPhoto;

  Album({
    required this.id,
    required this.title,
    this.description,
    required this.owner,
    this.category,
    required this.isPublic,
    required this.createdAt,
    required this.isOwner,
    this.coverPhoto,
  });

  factory Album.fromJson(Map<String, dynamic> json) {
    return Album(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      owner: Owner.fromJson(json['owner']),
      category: json['category'],
      isPublic: json['is_public'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
      isOwner: json['is_owner'] ?? false,
      coverPhoto: json['cover_photo'],
    );
  }
}

class Owner {
  final int id;
  final String username;
  final String email;

  Owner({
    required this.id,
    required this.username,
    required this.email,
  });

  factory Owner.fromJson(Map<String, dynamic> json) {
    return Owner(
      id: json['id'],
      username: json['username'],
      email: json['email'] ?? '',
    );
  }
}
