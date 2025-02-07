<?php
$servername = "db"; // Standard-Host für ddev
$username = "db";   // Standard-Benutzername für ddev
$password = "db";   // Standard-Passwort für ddev
$dbname = "db";     // Standard-Datenbankname für ddev

// Verbindung erstellen
$conn = new mysqli($servername, $username, $password, $dbname);

// Verbindung überprüfen
if ($conn->connect_error) {
    die("Verbindung fehlgeschlagen: " . $conn->connect_error);
}
echo "Erfolgreich verbunden mit der Datenbank!<br>";

// MySQL-Version abfragen
$sql = "SELECT VERSION() as version";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        echo "MySQL-Version: " . $row["version"];
    }
} else {
    echo "Keine Ergebnisse";
}

$conn->close();
?>
