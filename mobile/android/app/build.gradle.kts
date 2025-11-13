plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")

    // 👇 NUEVO: plugin de Google Services (Firebase)
    id("com.google.gms.google-services")
}

android {
    namespace = "com.example.mobile"
    compileSdk = flutter.compileSdkVersion

    // 🔧 NDK requerido por firebase/stripe/etc.
    ndkVersion = "27.0.12077973"

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11

        // ✅ Habilitar core library desugaring (lo pide flutter_local_notifications)
        isCoreLibraryDesugaringEnabled = true
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_11.toString()
    }

    defaultConfig {
        applicationId = "com.example.mobile"

        // 👇 Puedes fijar directamente minSdk 23 para evitar líos
        minSdk = 23

        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

flutter {
    source = "../.."
}

dependencies {
    // 👇 ya lo tenías, lo dejamos
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.0.4")
}
