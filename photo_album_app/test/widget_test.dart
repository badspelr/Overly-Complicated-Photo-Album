import 'package:flutter_test/flutter_test.dart';

import 'package:photo_album_app/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MyApp(isLoggedIn: false));

    // Verify that login screen is shown by finding the title and login button
    expect(find.text('Photo Album'), findsOneWidget);
    expect(find.text('Login'), findsOneWidget);
  });
}
