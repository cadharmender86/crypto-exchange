# BitNova Mobile

Flutter client for the BitNova crypto exchange.

## Current foundation

- Flutter/Dart project configuration
- REST API client
- OAuth2-compatible login against the existing backend
- Secure access-token storage
- Session gate and logout
- Initial authenticated home screen
- Assets/markets API integration

## Backend

The mobile app uses the same backend as the web application. The default Android emulator URL is:

`http://10.0.2.2:8000/api/v1`

For a physical device or deployed API, override it with:

`flutter run --dart-define=API_BASE_URL=https://your-api.example.com/api/v1`

## Local setup

From the repository root:

```powershell
cd mobile
flutter create . --platforms android,ios
flutter pub get
flutter run
```

If `flutter create .` reports that existing files would be overwritten, keep the existing `pubspec.yaml` and `lib/` files and generate only the native platform directories before running `flutter pub get`.
