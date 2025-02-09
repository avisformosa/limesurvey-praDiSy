# Beispiel-Daten mit mehr Variation
set.seed(123)
daten <- data.frame(
  Datum = seq(as.Date("2024-01-01"), as.Date("2024-01-20"), by = "days"),
  BDI_Wert = cumsum(sample(c(-2, -1, 0, 1, 2, 3), 20, replace = TRUE)) + 15
)
daten$BDI_Wert <- pmax(pmin(daten$BDI_Wert, 40), 0)  # Werte auf 0–40 begrenzen

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

# Bibliotheken
library(ggplot2)
library(patchwork)  # Für Kombination von Plots

# Hauptplot (Zeitreihe mit Kategorien)
zeitreihe_plot <- ggplot() +
  geom_rect(data = bereiche, aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax, fill = kategorie), alpha = 0.3) +
  geom_line(data = daten, aes(x = Datum, y = BDI_Wert), color = "black", size = 0.8) +
  geom_point(data = daten, aes(x = Datum, y = BDI_Wert), shape = 21, fill = "white", color = "black", size = 2) +
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

# Verteilungsplot (Histogramm mit Mittelwert und Streuung)
verteilung_plot <- ggplot(daten, aes(x = BDI_Wert)) +
  geom_histogram(binwidth = 2, fill = "lightblue", color = "black", alpha = 0.7) +
  geom_vline(aes(xintercept = mean(BDI_Wert)), color = "red", linetype = "dashed", size = 1) +
  annotate("text", x = mean(daten$BDI_Wert) + 2, y = 3, label = paste("Mittelwert =", round(mean(daten$BDI_Wert), 1)), color = "red") +
  labs(
    title = "Verteilung der BDI-Werte",
    x = "BDI-Wert",
    y = "Häufigkeit"
  ) +
  theme_minimal()

# Beide Plots kombinieren
zeitreihe_plot + verteilung_plot + plot_layout(widths = c(2, 1))
