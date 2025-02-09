# Beispiel-Daten erstellen
daten <- data.frame(
  Datum = seq(as.Date("2024-01-01"), as.Date("2024-01-10"), by = "days"),
  BDI_Wert = c(15, 14, 16, 13, 17, 18, 15, 12, 14, 13)  # Beispielwerte
)

# Bibliothek für bessere Datumsdarstellung (optional)
if (!requireNamespace("ggplot2", quietly = TRUE)) {
  install.packages("ggplot2")
}
library(ggplot2)

# Zeitreihen-Plot erstellen
ggplot(daten, aes(x = Datum, y = BDI_Wert)) +
  geom_line(color = "blue", size = 1) +  # Linie zeichnen
  geom_point(color = "red", size = 2) + # Punkte markieren
  labs(
    title = "Zeitreihe der BDI-Werte",
    x = "Datum",
    y = "BDI-Wert"
  ) +
  theme_minimal() +  # Klarer Stil
  scale_x_date(date_breaks = "1 day", date_labels = "%d.%m.%Y") +  # Datumsformat
  theme(axis.text.x = element_text(angle = 45, hjust = 1))  # Text drehen


# Beispiel-Daten erstellen
daten <- data.frame(
  Datum = seq(as.Date("2024-01-01"), as.Date("2024-01-10"), by = "days"),
  BDI_Wert = c(15, 14, 16, 13, 17, 18, 15, 12, 14, 13)  # Beispielwerte
)

# Bibliothek ggplot2 laden
library(ggplot2)

# Bereiche definieren
bereiche <- data.frame(
  xmin = as.Date("2024-01-01"),  # Startdatum
  xmax = as.Date("2024-01-10"),  # Enddatum
  ymin = c(0, 9, 14, 20, 29),    # Untergrenze der Bereiche
  ymax = c(8, 13, 19, 28, 63),   # Obergrenze der Bereiche
  kategorie = c(
    "Keine Depression",
    "Minimale Depression",
    "Leichte Depression",
    "Mittelschwere Depression",
    "Schwere Depression"
  )
)

# Zeitreihen-Plot erstellen mit Heatmap-Bereichen
ggplot() +
  # Heatmap-Bereiche hinzufügen
  geom_rect(data = bereiche, aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax, fill = kategorie), alpha = 0.3) +
  # BDI-Werte als Linie und Punkte
  geom_line(data = daten, aes(x = Datum, y = BDI_Wert), color = "blue", size = 1) +
  geom_point(data = daten, aes(x = Datum, y = BDI_Wert), color = "red", size = 2) +
  # Labels und Titel
  labs(
    title = "Zeitreihe der BDI-Werte mit Depressionsbereichen",
    x = "Datum",
    y = "BDI-Wert",
    fill = "Kategorie"
  ) +
  theme_minimal() +
  scale_x_date(date_breaks = "1 day", date_labels = "%d.%m.%Y") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_fill_manual(
    values = c(
      "Keine Depression" = "green",
      "Minimale Depression" = "yellow",
      "Leichte Depression" = "orange",
      "Mittelschwere Depression" = "red",
      "Schwere Depression" = "darkred"
    )
  )
