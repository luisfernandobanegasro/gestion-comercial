// Importaciones necesarias para que Kotlin funcione con clases de Java
import java.util.Properties
import java.io.FileInputStream

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("dev.flutter.flutter-gradle-plugin")
}

fun localProperties(project: org.gradle.api.Project): Properties {
    val properties = Properties()
    val localPropertiesFile = project.rootProject.file("local.properties")
    if (localPropertiesFile.exists()) {
        properties.load(FileInputStream(localPropertiesFile))
    }
    return properties
}

val flutterVersionCode: String by lazy { localProperties(project).getProperty("flutter.versionCode") ?: "1" }
val flutterVersionName: String by lazy { localProperties(project).getProperty("flutter.versionName") ?: "1.0" }

android {
    namespace = "com.example.mobile"
    // Leemos la propiedad del archivo gradle.properties
    compileSdk = (project.property("flutter.compileSdkVersion") as String).toInt()

    ndkVersion = "27.0.12077973"

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
        isCoreLibraryDesugaringEnabled = true
    }

    kotlinOptions {
        jvmTarget = "1.8"
    }

    defaultConfig {
        applicationId = "com.example.mobile"
        minSdk = 23
        targetSdk = (project.property("flutter.targetSdkVersion") as String).toInt()
        versionCode = flutterVersionCode.toInt()
        versionName = flutterVersionName
    }

    buildTypes {
        release {
            // No modifiques esta sección, es crucial para Stripe
            signingConfig = signingConfigs.getByName("debug")
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro" // <-- Usa tu archivo de reglas
            )
        }
    }
}

flutter {
    source = "../.."
}

dependencies {
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.0.4")
}
