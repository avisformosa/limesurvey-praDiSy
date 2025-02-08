<?php
// Sample subject received from the email
$subject = 'DIAG123PARTICIPANT456DATE2024-09-15TIME14:00';

// Define a regular expression to extract the variables
$pattern = '/DIAG(?P<surveyId>\d+)PARTICIPANT(?P<participantId>\d+)DATE(?P<date>[\d\-]+)TIME(?P<time>[\d:]+)/';

// Check if the subject matches the expected pattern
if (preg_match($pattern, $subject, $matches)) {
    // Extracted values
    $surveyId = $matches['surveyId'];
    $participantId = $matches['participantId'];
    $date = $matches['date'];
    $time = $matches['time'];

    // Output the extracted values (or use them for further processing)
    echo "Survey ID: " . $surveyId . PHP_EOL;
    echo "Participant ID: " . $participantId . PHP_EOL;
    echo "Date: " . $date . PHP_EOL;
    echo "Time: " . $time . PHP_EOL;
} else {
    echo "Fehler: Das Betreffformat stimmt nicht mit dem erwarteten Muster überein." . PHP_EOL;
}
