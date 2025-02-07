#!/bin/bash

# Pfade definieren
SOURCE_DIR="PraDiSy/assets/adminscripts"
TARGET_DIR="admin"

# Liste der Dateien, die kopiert werden sollen
FILES_TO_COPY=(
    "phpinfo.php"
    "db_test.php"
)

# Funktion zum Kopieren der Dateien
copy_files() {
    for file in "${FILES_TO_COPY[@]}"; do
        if [ -f "$SOURCE_DIR/$file" ]; then
            cp "$SOURCE_DIR/$file" "$TARGET_DIR/$file"
            echo "Kopiert: $file von $SOURCE_DIR nach $TARGET_DIR"
        else
            echo "Datei nicht gefunden: $SOURCE_DIR/$file"
        fi
    done
}

# Hauptskript
copy_files
