#!/bin/bash

# Verzeichnisse
BACKUP_DIR="logo_backup"
CORPORATE_IDENTITY_DIR="corporate_identity"
PRADISY_DIR="PraDiSy/assets/images"

# Zu ersetzende Dateien mit spezifischen Ersatzdateien "installer/images/admin-logo.svg"
FILES_WITH_TITLE_LOGO=(
    "assets/images/__Limesurvey_logo.png"
    "assets/images/Limesurvey_logo-big.png"
    "themes/admin/Sea_Green/images/Limesurvey_logo.png"
    "themes/admin/Sea_Green/images/logo.png"
    "themes/survey/bootswatch/files/logo.png"
    "themes/survey/bootswatch/files/survey_list_header.png"
    "themes/survey/fruity_twentythree/files/logo.png"
    "themes/survey/fruity/files/logo.png"
    "themes/survey/fruity/files/survey_list_header.png"
    "themes/survey/vanilla/files/logo.png"
    "themes/survey/vanilla/files/survey_list_header.png"
)

# "installer/images/cloud-logo.svg"

FILES_LOGO=(
    "assets/images/limecursor-handle.png"
    "assets/images/Logo_LimeSurvey.png"
    "installer/images/comfortupdate-logo.png"
    "themes/admin/Sea_Green/images/logo_icon.png"
)

FILES_FAVICON=(
    "themes/survey/fruity_twentythree/files/favicon.ico"
    "themes/survey/fruity/files/favicon.ico"
    "themes/survey/vanilla/files/favicon.ico"
    "application/favicon.ico"
    "themes/admin/favicon.ico"
)

FILES_WHITE_ICON=(
    "assets/images/logo-icon-white.png"
)

FILES_WHITE_WITH_TITLE_LOGO=(
    "assets/images/logo-white.png"
    "themes/admin/Sea_Green/images/logo-white.png"
)

FILES_GRAY_WITH_TITLE_LOGO=(
    "themes/survey/bootswatch/files/logo_pdf.png"
    "themes/survey/fruity_twentythree/files/logo_pdf.png"
    "themes/survey/fruity/files/logo_pdf.png"
    "themes/survey/vanilla/files/logo_pdf.png"
)

FILES_SVG_LOGO=(
    "themes/admin/Sea_Green/images/logo.svg"
)

FILES_SVG_WITH_TITLE_LOGO=(
    "installer/images/admin-logo.svg"
    "themes/admin/Sea_Green/images/logo.svg"
)

# Pfade zu den Ersatzdateien
FILES_TWIG_REPLACEMENT=(
    "Limesurvey/themes/survey/fruity_twentythree/views/ls_logo_svg.twig"
)

# Pfade zu den Ersatzdateien
REPLACEMENT_FILE_WITH_TITLE_LOGO="$PRADISY_DIR/logo_with_title.png"
REPLACEMENT_FILE_LOGO="$PRADISY_DIR/logo.png"
REPLACEMENT_FILE_FAVICON="$PRADISY_DIR/favicon.ico"
REPLACEMENT_FILE_WHITE_ICON="$PRADISY_DIR/logo_white.png"
REPLACEMENT_FILE_WHITE_WITH_TITLE_LOGO="$PRADISY_DIR/logo_white_with_title.png"
REPLACEMENT_FILE_GRAY_WITH_TITLE_LOGO="$PRADISY_DIR/logo_gray_with_title.png"
REPLACEMENT_FILE_SVG_LOGO="$PRADISY_DIR/logo.svg"  # Ersatzdatei für SVG-Logos
REPLACEMENT_FILE_SVG_WITH_TITLE_LOGO="$PRADISY_DIR/logo_with_title.svg"  # Ersatzdatei für admin-logo.svg
REPLACEMENT_FILE_TWIG="PraDiSy/assets/twig/logo.twig"

# Backup-Funktion
backup() {
    mkdir -p "$BACKUP_DIR"

    # Backup der Dateien in den Listen
    for file in "${FILES_WITH_TITLE_LOGO[@]}" "${FILES_LOGO[@]}" "${FILES_FAVICON[@]}" "${FILES_WHITE_ICON[@]}" "${FILES_WHITE_WITH_TITLE_LOGO[@]}" "${FILES_GRAY_WITH_TITLE_LOGO[@]}"; do
        if [ -f "$file" ]; then
            backup_file=$(echo "$file" | tr '/' '.')
            cp "$file" "$BACKUP_DIR/$backup_file"
            echo "Gesichert: $file als $BACKUP_DIR/$backup_file"
        else
            echo "Datei nicht gefunden: $file"
        fi
    done
}

# Restore-Funktion
restore() {
    for backup_file in "$BACKUP_DIR"/*; do
        original_file=$(echo "$backup_file" | sed "s|$BACKUP_DIR/||" | tr '.' '/')
        cp "$backup_file" "$original_file"
        echo "Wiederhergestellt: $backup_file nach $original_file"
    done
}

# Replace-Funktion
replace() {

  # Ersetzen der Twig-Datei
    for file in "${FILES_TWIG_REPLACEMENT[@]}"; do
        if [ -f "$REPLACEMENT_FILE_TWIG" ]; then
            cp "$REPLACEMENT_FILE_TWIG" "$file"
            echo "Ersetzt: $file durch $REPLACEMENT_FILE_TWIG"
        else
            echo "Ersatzdatei nicht gefunden: $REPLACEMENT_FILE_TWIG"
        fi
    done

    for file in "${FILES_WITH_TITLE_LOGO[@]}"; do
        if [ -f "$REPLACEMENT_FILE_WITH_TITLE_LOGO" ]; then
            cp "$REPLACEMENT_FILE_WITH_TITLE_LOGO" "$file"
            echo "Ersetzt: $file durch $REPLACEMENT_FILE_WITH_TITLE_LOGO"
        else
            echo "Ersatzdatei nicht gefunden: $REPLACEMENT_FILE_WITH_TITLE_LOGO"
        fi
    done

    for file in "${FILES_LOGO[@]}"; do
        if [ -f "$REPLACEMENT_FILE_LOGO" ]; then
            cp "$REPLACEMENT_FILE_LOGO" "$file"
            echo "Ersetzt: $file durch $REPLACEMENT_FILE_LOGO"
        else
            echo "Ersatzdatei nicht gefunden: $REPLACEMENT_FILE_LOGO"
        fi
    done

    for file in "${FILES_FAVICON[@]}"; do
        if [ -f "$REPLACEMENT_FILE_FAVICON" ]; then
            cp "$REPLACEMENT_FILE_FAVICON" "$file"
            echo "Ersetzt: $file durch $REPLACEMENT_FILE_FAVICON"
        else
            echo "Ersatzdatei nicht gefunden: $REPLACEMENT_FILE_FAVICON"
        fi
    done

    for file in "${FILES_WHITE_ICON[@]}"; do
        if [ -f "$REPLACEMENT_FILE_WHITE_ICON" ]; then
            cp "$REPLACEMENT_FILE_WHITE_ICON" "$file"
            echo "Ersetzt: $file durch $REPLACEMENT_FILE_WHITE_ICON"
        else
            echo "Ersatzdatei nicht gefunden: $REPLACEMENT_FILE_WHITE_ICON"
        fi
    done

    for file in "${FILES_WHITE_WITH_TITLE_LOGO[@]}"; do
        if [ -f "$REPLACEMENT_FILE_WHITE_WITH_TITLE_LOGO" ]; then
            cp "$REPLACEMENT_FILE_WHITE_WITH_TITLE_LOGO" "$file"
            echo "Ersetzt: $file durch $REPLACEMENT_FILE_WHITE_WITH_TITLE_LOGO"
        else
            echo "Ersatzdatei nicht gefunden: $REPLACEMENT_FILE_WHITE_WITH_TITLE_LOGO"
        fi
    done

    for file in "${FILES_GRAY_WITH_TITLE_LOGO[@]}"; do
        if [ -f "$REPLACEMENT_FILE_GRAY_WITH_TITLE_LOGO" ]; then
            cp "$REPLACEMENT_FILE_GRAY_WITH_TITLE_LOGO" "$file"
            echo "Ersetzt: $file durch $REPLACEMENT_FILE_GRAY_WITH_TITLE_LOGO"
        else
            echo "Ersatzdatei nicht gefunden: $REPLACEMENT_FILE_GRAY_WITH_TITLE_LOGO"
        fi
    done
    
    for file in "${FILES_SVG_LOGO[@]}"; do
        if [ -f "$REPLACEMENT_FILE_SVG_LOGO" ]; then
            cp "$REPLACEMENT_FILE_SVG_LOGO" "$file"
            echo "Ersetzt: $file durch $REPLACEMENT_FILE_SVG_LOGO"
        else
            echo "Ersatzdatei nicht gefunden: $REPLACEMENT_FILE_SVG_LOGO"
        fi
    done

    for file in "${FILES_SVG_WITH_TITLE_LOGO[@]}"; do
        if [ -f "$REPLACEMENT_FILE_SVG_WITH_TITLE_LOGO" ]; then
            cp "$REPLACEMENT_FILE_SVG_WITH_TITLE_LOGO" "$file"
            echo "Ersetzt: $file durch $REPLACEMENT_FILE_SVG_WITH_TITLE_LOGO"
        else
            echo "Ersatzdatei nicht gefunden: $REPLACEMENT_FILE_SVG_WITH_TITLE_LOGO"
        fi
    done
}

# Hauptskript
if [ "$1" == "backup" ]; then
    backup
elif [ "$1" == "restore" ]; then
    restore
elif [ "$1" == "replace" ]; then
    replace
else
    echo "Verwendung: $0 {backup|restore|replace}"
fi
