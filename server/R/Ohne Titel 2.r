# Beispiel-Daten mit mehr Variation
set.seed(123)  # Für Reproduzierbarkeit
daten <- data.frame(
  Datum = seq(as.Date("2024-01-01"), as.Date("2024-01-20"), by = "days"),
  BDI_Wert = cumsum(sample(c(-2, -1, 0, 1, 2, 3), 20, replace = TRUE)) + 15  # Startwert und Variation
)

# Sicherstellen, dass die Werte im Bereich 0–40 liegen
daten$BDI_Wert <- pmax(pmin(daten$BDI_Wert, 40), 0)

# Bereiche definieren
bereiche <- data.frame(
  xmin = as.Date("2024-01-01"),
  xmax = as.Date("2024-01-20"),
  ymin = c(0, 9, 14, 20, 29),
  ymax = c(8, 13, 19, 28, 63),
  kategorie = c(
    "Keine Depression",
    "Minimale Depression",
    "Leichte Depression",
    "Mittelschwere Depression",
    "Schwere Depression"
  )
)

# Plot erstellen
library(ggplot2)

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
  scale_x_date(date_breaks = "2 days", date_labels = "%d.%m.%Y") +
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
