# Beispiel-Daten mit mehr Variation
set.seed(123)
daten <- data.frame(
  Datum = seq(as.Date("2024-01-01"), as.Date("2024-01-20"), by = "days"),
  BDI_Wert = cumsum(sample(c(-2, -1, 0, 1, 2, 3), 20, replace = TRUE)) + 15
)
daten$BDI_Wert <- pmax(pmin(daten$BDI_Wert, 40), 0)  # Werte auf 0–40 begrenzen

# Bereiche definieren (angepasst, um Lücken zu vermeiden)
bereiche <- data.frame(
  xmin = as.Date("2024-01-01"),
  xmax = as.Date("2024-01-20"),
  ymin = c(0, 8, 13, 19, 28),
  ymax = c(8, 13, 19, 28, 63),
  kategorie = c(
    "Keine Depression",
    "Minimale Depression",
    "Leichte Depression",
    "Mittelschwere Depression",
    "Schwere Depression"
  )
)

# Kritische Punktgrenzen
kritische_punkte <- data.frame(
  y = c(8, 13, 19, 28),
  label = c("8 (Keine Depression)", 
            "13 (Minimale Depression)", 
            "19 (Leichte Depression)", 
            "28 (Mittelschwere Depression)")
)

# Bibliotheken
library(ggplot2)

# Hauptplot (Zeitreihe mit Kategorien und kritischen Punkten)
zeitreihe_plot <- ggplot() +
  # Farbige Bereiche
  geom_rect(data = bereiche, aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax, fill = kategorie), alpha = 0.3) +
  # Datenlinie und Punkte
  geom_line(data = daten, aes(x = Datum, y = BDI_Wert), color = "black", size = 0.8) +
  geom_point(data = daten, aes(x = Datum, y = BDI_Wert), shape = 21, fill = "white", color = "black", size = 2) +
  # Beschriftung für Maximal-, Minimal- und Endpunkt
  geom_text(data = daten[which.max(daten$BDI_Wert), ], aes(x = Datum, y = BDI_Wert, label = BDI_Wert), vjust = -1) +
  geom_text(data = daten[which.min(daten$BDI_Wert), ], aes(x = Datum, y = BDI_Wert, label = BDI_Wert), vjust = 1.5) +
  geom_text(data = daten[nrow(daten), ], aes(x = Datum, y = BDI_Wert, label = BDI_Wert), vjust = -1) +
  # Kritische Punktgrenzen als horizontale Linien
  geom_hline(data = kritische_punkte, aes(yintercept = y), linetype = "dashed", color = "gray") +
  # Kritische Punktgrenzen beschriften
  geom_text(
    data = kritische_punkte, 
    aes(x = as.Date("2024-01-01"), y = y, label = label), 
    hjust = -0.1, vjust = -0.5, 
    color = "darkgray", size = 3.5  # Kleinere und dunklere Schrift
  ) +
  # Achsentitel und Titel
  labs(
    title = "Zeitreihe der BDI-Werte mit Depressionsbereichen und kritischen Punkten",
    x = "Datum",
    y = "BDI-Wert",
    fill = "Kategorie"
  ) +
  theme_minimal() +
  scale_x_date(date_breaks = "2 days", date_labels = "%d.%m.%Y") +
  scale_y_continuous(expand = expansion(mult = c(0.05, 0.05))) +  # Erweiterte Skalen
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),
    legend.position = "top"  # Legende oben
  ) +
  scale_fill_manual(
    values = c(
      "Keine Depression" = "green",
      "Minimale Depression" = "yellow",
      "Leichte Depression" = "orange",
      "Mittelschwere Depression" = "red",
      "Schwere Depression" = "darkred"
    )
  )

# Plot anzeigen
zeitreihe_plot
