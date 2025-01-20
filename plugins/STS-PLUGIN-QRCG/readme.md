# Qr Code Generator

## Encoding Data

QR codes can hold a wide range of data. Below are some examples. of course there are more, but these are a few to get you started!

| Type             | Description                                                    | Example                                              |
| ---------------- | -------------------------------------------------------------- | ---------------------------------------------------- |
| Text             | Encoding text does not require anything special                | ```This is some example text.```               |
| URLs             | Links to a web address                                         | ```https://google.com\```                      |
| Email            | Auto open email client with recipient and subject filled out.  | ```mailto:someone@example.com?subject=Hello``` |
| Phone Number     | Will be dialed when scanned.                                   | ```tel:+1234567890```                          |
| SMS              | will write a text message to a number                          | ```sms:+1234567890?body=Hello```               |
| Wifi Information | will connect to wifi and automate login with name and password | ```WIFI:S:MyNetwork;T:WPA;P:password123;;```   |

## QR Code Versions overview 1-40

| Version | Modules per Side | Numeric Data Capacity (Level L) | Level M | Level Q | Level H |
|---------|------------------|----------------------------------|---------|---------|---------|
| 1       | 21 × 21          | 41 characters                   | 34      | 27      | 17      |
| 2       | 25 × 25          | 77 characters                   | 63      | 48      | 34      |
| 3       | 29 × 29          | 127 characters                  | 101     | 77      | 58      |
| 4       | 33 × 33          | 187 characters                  | 149     | 111     | 82      |
| 5       | 37 × 37          | 255 characters                  | 202     | 144     | 106     |
| 6       | 41 × 41          | 322 characters                  | 255     | 178     | 139     |
| 7       | 45 × 45          | 370 characters                  | 293     | 207     | 154     |
| 8       | 49 × 49          | 461 characters                  | 365     | 259     | 202     |
| 9       | 53 × 53          | 552 characters                  | 432     | 312     | 235     |
| 10      | 57 × 57          | 652 characters                  | 513     | 364     | 288     |
| 11      | 61 × 61          | 772 characters                  | 604     | 427     | 331     |
| 12      | 65 × 65          | 883 characters                  | 691     | 489     | 374     |
| 13      | 69 × 69          | 1022 characters                 | 796     | 580     | 427     |
| 14      | 73 × 73          | 1101 characters                 | 871     | 621     | 468     |
| 15      | 77 × 77          | 1250 characters                 | 991     | 703     | 530     |
| 16      | 81 × 81          | 1408 characters                 | 1082    | 775     | 602     |
| 17      | 85 × 85          | 1548 characters                 | 1212    | 876     | 674     |
| 18      | 89 × 89          | 1725 characters                 | 1346    | 948     | 746     |
| 19      | 93 × 93          | 1903 characters                 | 1500    | 1049    | 813     |
| 20      | 97 × 97          | 2061 characters                 | 1600    | 1153    | 919     |
| 21      | 101 × 101        | 2232 characters                 | 1708    | 1249    | 969     |
| 22      | 105 × 105        | 2409 characters                 | 1872    | 1352    | 1056    |
| 23      | 109 × 109        | 2620 characters                 | 2059    | 1460    | 1108    |
| 24      | 113 × 113        | 2812 characters                 | 2188    | 1588    | 1228    |
| 25      | 117 × 117        | 3057 characters                 | 2395    | 1718    | 1286    |
| 26      | 121 × 121        | 3283 characters                 | 2544    | 1804    | 1425    |
| 27      | 125 × 125        | 3517 characters                 | 2701    | 1933    | 1501    |
| 28      | 129 × 129        | 3669 characters                 | 2857    | 2085    | 1581    |
| 29      | 133 × 133        | 3909 characters                 | 3035    | 2181    | 1693    |
| 30      | 137 × 137        | 4158 characters                 | 3289    | 2358    | 1793    |
| 31      | 141 × 141        | 4417 characters                 | 3486    | 2473    | 1873    |
| 32      | 145 × 145        | 4686 characters                 | 3693    | 2670    | 1989    |
| 33      | 149 × 149        | 4965 characters                 | 3909    | 2805    | 2099    |
| 34      | 153 × 153        | 5253 characters                 | 4134    | 2949    | 2213    |
| 35      | 157 × 157        | 5529 characters                 | 4343    | 3081    | 2331    |
| 36      | 161 × 161        | 5836 characters                 | 4588    | 3244    | 2452    |
| 37      | 165 × 165        | 6153 characters                 | 4775    | 3417    | 2577    |
| 38      | 169 × 169        | 6479 characters                 | 5039    | 3599    | 2705    |
| 39      | 173 × 173        | 6743 characters                 | 5313    | 3791    | 2840    |
| 40      | 177 × 177        | 7089 characters                 | 5596    | 3993    | 2953    |

## Error Correction Capabilities

QR Code has error correction capability to restore data if the code is dirty or damaged. Four error correction levels are available for users to choose according to the operating environment. Raising this level improves error correction capability but also increases the amount of data QR Code size.

| Correction Level | Data Restoration |
|------------------|------------------|
| Level L          | Approx 7%        |
| Level M          | Approx 15%       |
| Level Q          | Approx 25%       |
| Level H          | Approx 30%       |

Learn More: <https://www.qrcode.com/en/about/error_correction.html>
