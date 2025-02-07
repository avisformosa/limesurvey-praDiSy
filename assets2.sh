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

FILES_LOGO=(
    "assets/images/limecursor-handle.png"
    "assets/images/Logo_LimeSurvey.png"
    "installer/images/comfortupdate-logo.png"
    "themes/admin/Sea_Green/images/logo_icon.png"
    "assets/images/logo-icon-black.png"
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
# Ersatzdateien für SVG-Logos
REPLACEMENT_FILE_SVG_LOGO="$PRADISY_DIR/logo_with_title.svg"
REPLACEMENT_FILE_SVG_WITH_TITLE_LOGO="$PRADISY_DIR/logo_with_title.svg"
REPLACEMENT_FILE_TWIG="PraDiSy/assets/twig/logo.twig"

###############################################
# Funktionen
###############################################

# Prüft, ob ImageMagick (convert und identify) verfügbar ist.
check_imagemagick() {
    if command -v convert >/dev/null 2>&1 && command -v identify >/dev/null 2>&1; then
        IMAGEMAGICK_AVAILABLE=1
    else
        IMAGEMAGICK_AVAILABLE=0
    fi
}

# Sichert vorhandene Dateien
backup() {
    mkdir -p "$BACKUP_DIR"

    # Backup der Dateien aus allen Listen
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

# Stellt die gesicherten Dateien wieder her
restore() {
    for backup_file in "$BACKUP_DIR"/*; do
        original_file=$(echo "$backup_file" | sed "s|$BACKUP_DIR/||" | tr '.' '/')
        cp "$backup_file" "$original_file"
        echo "Wiederhergestellt: $backup_file nach $original_file"
    done
}

# Ersetzt eine einzelne Datei:
# - Existiert die Ersatzdatei nicht, wird eine Fehlermeldung ausgegeben.
# - Existiert das Ziel (zu ersetzende Datei) nicht, wird dies gemeldet.
# - Handelt es sich beim Ziel um eine PNG-Datei, so wird zunächst deren
#   Auflösung ermittelt und der Ersatz mittels convert resized, um das Seitenverhältnis zu wahren.
# - Bei anderen Formaten erfolgt ein einfacher Kopiervorgang.
replace_file() {
    local target_file="$1"
    local replacement_file="$2"

    if [ ! -f "$replacement_file" ]; then
        echo "Ersatzdatei nicht gefunden: $replacement_file"
        return
    fi

    if [ ! -f "$target_file" ]; then
        echo "Zieldatei nicht gefunden: $target_file"
        return
    fi

    if [[ "$target_file" == *.png ]]; then
        # Für PNG-Dateien muss ImageMagick verfügbar sein.
        if [ "$IMAGEMAGICK_AVAILABLE" -ne 1 ]; then
            echo "ImageMagick (convert/identify) nicht verfügbar. Kann $target_file nicht ersetzen."
            return
        fi

        # Ermitteln der aktuellen Auflösung der Zieldatei
        dimensions=$(identify -format "%w %h" "$target_file" 2>/dev/null)
        if [ -z "$dimensions" ]; then
            echo "Konnte Dimensionen von $target_file nicht ermitteln."
            return
        fi
        width=$(echo $dimensions | cut -d' ' -f1)
        height=$(echo $dimensions | cut -d' ' -f2)

        # Mit -resize wird das Bild so skaliert, dass es maximal in den
        # Rahmen ${width}x${height} passt – ohne das Seitenverhältnis zu verändern.
        convert "$replacement_file" -resize "${width}x${height}" "$target_file"
        echo "Ersetzt (mit Resize): $target_file durch $replacement_file (max ${width}x${height})"
    else
        cp "$replacement_file" "$target_file"
        echo "Ersetzt: $target_file durch $replacement_file"
    fi
}

# Ersetzt die Dateien mit den entsprechenden Ersatzdateien.
replace() {
    # Zunächst prüfen wir, ob ImageMagick verfügbar ist (wird nur bei PNG benötigt).
    check_imagemagick

    # Ersetzen der Twig-Datei
    for file in "${FILES_TWIG_REPLACEMENT[@]}"; do
        replace_file "$file" "$REPLACEMENT_FILE_TWIG"
    done

    for file in "${FILES_WITH_TITLE_LOGO[@]}"; do
        replace_file "$file" "$REPLACEMENT_FILE_WITH_TITLE_LOGO"
    done

    for file in "${FILES_LOGO[@]}"; do
        replace_file "$file" "$REPLACEMENT_FILE_LOGO"
    done

    for file in "${FILES_FAVICON[@]}"; do
        replace_file "$file" "$REPLACEMENT_FILE_FAVICON"
    done

    for file in "${FILES_WHITE_ICON[@]}"; do
        replace_file "$file" "$REPLACEMENT_FILE_WHITE_ICON"
    done

    for file in "${FILES_WHITE_WITH_TITLE_LOGO[@]}"; do
        replace_file "$file" "$REPLACEMENT_FILE_WHITE_WITH_TITLE_LOGO"
    done

    for file in "${FILES_GRAY_WITH_TITLE_LOGO[@]}"; do
        replace_file "$file" "$REPLACEMENT_FILE_GRAY_WITH_TITLE_LOGO"
    done

    for file in "${FILES_SVG_LOGO[@]}"; do
        replace_file "$file" "$REPLACEMENT_FILE_SVG_LOGO"
    done

    for file in "${FILES_SVG_WITH_TITLE_LOGO[@]}"; do
        replace_file "$file" "$REPLACEMENT_FILE_SVG_WITH_TITLE_LOGO"
    done
}

###############################################
# Hauptskript
###############################################
case "$1" in
    backup)
        backup
        ;;
    restore)
        restore
        ;;
    replace)
        replace
        ;;
    *)
        echo "Verwendung: $0 {backup|restore|replace}"
        ;;
esac
