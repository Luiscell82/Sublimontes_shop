# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Sublimontes Shop** is a Flutter mobile marketplace app where:
- Guest users can browse products without registering
- Registered users with an active membership can publish products
- Users can chat and share product links

## Development Commands

Flutter is required locally to build and run the project. It is not available in the remote cloud environment.

```bash
# Install dependencies
flutter pub get

# Run the app (debug)
flutter run

# Build APK
flutter build apk

# Build iOS
flutter build ios

# Run tests
flutter test

# Run a single test file
flutter test test/widget_test.dart

# Lint / analyze
flutter analyze

# Format code
dart format lib/
```

## Architecture

State is managed via `Provider` (`ChangeNotifier`). A single `AppState` instance is provided at the root (`main.dart`) and consumed throughout the widget tree with `context.watch<AppState>()` / `context.read<AppState>()`.

Session persistence uses `SharedPreferences`. No external backend — all data is stored locally.

### Key layers

| Path | Responsibility |
|------|---------------|
| `lib/main.dart` | App entry point, Provider setup, named route table |
| `lib/utils/app_state.dart` | Central state: current user, products, messages, auth methods |
| `lib/models/` | Plain Dart models: `User`, `Product`, `Message` |
| `lib/screens/` | One file per screen, navigated via `Navigator.pushNamed` |
| `lib/utils/conexion.dart` | `isConnected()` — wraps `connectivity_plus` |

### Membership gate

`AppState.currentUser.tieneMembresia` is checked before allowing product publishing. If false, the app redirects to `MembershipScreen` where the user can activate (mock payment).

### Navigation routes (defined in main.dart)

```
/              → HomeScreen
/login         → LoginScreen
/register      → RegisterScreen
/publish       → ProductPublishScreen
/chat          → ChatScreen  (receives Product as argument)
/membership    → MembershipScreen
/product       → ProductDetailScreen (receives Product as argument)
```

## Cloud Session Setup

A `SessionStart` hook at `.claude/hooks/session-start.sh` auto-installs `agent-browser` (npm) and wires up Chromium from the pre-installed Playwright binary (`/opt/pw-browsers/chromium-1194/`). This runs automatically on each remote session — no manual setup needed.
