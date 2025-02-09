import sys
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QSystemTrayIcon, QMessageBox
from PyQt5.QtGui import QIcon


def show_message():
    QMessageBox.information(None, "Info", "Das ist ein Test!")


app = QApplication(sys.argv)

# Verstecke das Hauptfenster
app.setQuitOnLastWindowClosed(False)

# Erstelle ein System Tray Icon
tray_icon = QSystemTrayIcon()
tray_icon.setIcon(QIcon("/Users/andre/Coding/Limesurvey/LimeSurvey/server/icon.png"))  # Pfad zu einem Icon
tray_icon.setToolTip("Meine Menu Bar App")

# Menü erstellen
menu = QMenu()

# Aktion hinzufügen
action_show = QAction("Zeige Nachricht")
action_show.triggered.connect(show_message)
menu.addAction(action_show)

# Trennlinie
menu.addSeparator()

# Beenden-Aktion
action_quit = QAction("Beenden")
action_quit.triggered.connect(app.quit)
menu.addAction(action_quit)

# Menü zum Tray Icon hinzufügen
tray_icon.setContextMenu(menu)

# Zeige das Tray Icon
tray_icon.show()

sys.exit(app.exec_())
