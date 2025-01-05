from PyQt5 import QtWidgets, uic, QtCore
import os
from collections import Counter
from mutagen import File
from PyQt5.QtGui import QStandardItemModel, QStandardItem


def get_audio_files(directory):
    """Recursively find all audio files in a directory."""
    audio_extensions = {'.mp3', '.flac', '.wav', '.aac', '.m4a', '.ogg', '.wma'}
    audio_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in audio_extensions:
                audio_path = os.path.join(root, file)
                audio_files.append(audio_path)
    return audio_files


def get_genre(file_path):
    """Extract the genre metadata from an audio file."""
    try:
        audio = File(file_path)
        if audio:
            for tag in ['genre', 'GENRE', 'TCON']:  # Common tags for genre
                if tag in audio.tags:
                    genre = audio.tags[tag]
                    if isinstance(genre, list):
                        genre = genre[0]
                    return [g.strip().lower() for g in str(genre).split(';')]
    except Exception:
        pass  # Silently ignore files with errors
    return []


def map_to_simplified_genres(complex_genres):
    """Map complex genres to simplified categories."""
    simplified_keywords = {
                #
                # A
                "Ambient": ["ambient"],
                # B
                "*Blues": [
                    "blues", "delta blues", "chicago blues", "texas blues",
                    "memphis blues", "electric blues", "acoustic blues",
                    "classic blues", "modern blues",
                    "contemporary blues", "blues rock", "soul blues",
                    "funk blues", "rhythm and blues", "piedmont blues",
                    "jump blues", "urban blues", "gospel blues", "boogie-woogie",
                    "new orleans blues", "west coast blues", "louisiana blues",
                    "british blues", "psychedelic blues", "progressive blues",
                    "hard blues", "traditional blues", "slide guitar blues",
                    "harmonica blues", "slow blues", "jazzy blues",
                    "swing blues", "folk blues",
                    "blues shuffles", "blues ballads", "vocal blues",
                    "blues funk fusion", "experimental blues", "ambient blues",
                    "lo-fi blues", "dark blues", "melancholy blues",
                    "uplifting blues", "electric delta blues", "rockabilly blues",
                    "roots blues", "americana blues", "chicago electric blues",
                    "delta slide blues", "chill blues", "indie blues",
                    "garage blues", "retro blues", "modern delta blues",
                    "fusion blues", "contemporary electric blues",
                    "deep blues", "gritty blues", "emotive blues", "storytelling blues",
                    "minimal blues", "raw blues", "boogie blues", "shuffle blues",
                    "bluegrass blues", "swamp blues", "stomp blues",
                    "jazzy swing blues", "barrelhouse blues", "ragtime blues",
                    "vaudeville blues", "piano blues", "harmonica-heavy blues",
                    "southern blues", "texas electric blues", "british electric blues",
                    "progressive electric blues", "soulful blues", "blues gospel fusion",
                    "slide guitar electric blues", "rock blues fusion",
                    "psychedelic electric blues", "acoustic folk blues",
                    "experimental delta blues", "chicago urban blues",
                    "funky blues rock", "dark soulful blues", "celestial blues",
                    "spiritual blues", "electric swamp blues", "minimalist blues",
                    "ethereal blues", "fusion delta blues",
                ],

                # C
                "*Classical": [
                    "classical", "baroque", "romantic", "classical crossover",
                    "neoclassical", "impressionism", "expressionism", "minimalism",
                    "post-romantic", "modern classical", "contemporary classical",
                    "chamber music", "symphonic", "orchestral", "opera",
                    "choral", "liturgical", "sacred music", "cantata",
                    "fugue", "suite", "concerto", "sonata", "string quartet",
                    "symphony", "tone poem", "program music", "ballet music",
                    "piano concerto", "violin concerto", "cello concerto",
                    "classical piano", "classical guitar", "classical harp",
                    "solo piano", "art song", "lieder", "renaissance",
                    "medieval", "gregorian chant", "early music",
                    "avant-garde classical", "experimental classical",
                    "ambient classical", "ethereal classical", "classical jazz fusion",
                    "neo-baroque", "neo-romantic", "post-minimalism",
                    "film score", "cinematic classical", "classical electronic",
                    "aleatoric music", "microtonal classical", "serialism",
                    "atonal music", "twelve-tone", "spectral music",
                    "nationalist classical", "folk-inspired classical",
                    "ethnic classical", "world classical", "historical classical",
                    "period instruments", "historical performance", "early romantic",
                    "late romantic", "high classical", "sacred choral",
                    "secular choral", "opera buffa", "opera seria",
                    "grand opera", "comic opera", "lyric opera", "baroque opera",
                    "chamber orchestra", "string orchestra", "wind ensemble",
                    "brass ensemble", "woodwind quintet", "vocal ensemble",
                    "solo violin", "solo cello", "solo flute",
                    "classical avant-garde", "new classical", "fusion classical",
                    "modernist classical", "romantic symphony", "post-romantic symphony",
                    "early classical", "heroic classical", "philosophical classical",
                    "epic classical", "symphonic poem", "classical cantata",  "neoclassicism",
                    "orchestra", "orkiestra symfoniczna", "early avant garde",
                ],

                "*Country": [ "country", "outlaw country","indie country",
                    "country-infused", "country blues", "country pop",


                ],

                # D
                # E
                "*EDM / Electronic": [
                    "edm", "electronic", "dubstep", "brostep", "future bass",
                    "trap", "house", "progressive house", "deep house",
                    "tropical house", "electro house", "tech house",
                    "bass house", "garage house", "minimal house",
                    "techno", "minimal techno", "acid techno", "melodic techno",
                    "hard techno", "trance", "progressive trance", "uplifting trance",
                    "psytrance", "hard trance", "goa trance", "vocal trance",
                    "chillstep", "hardstep", "drum and bass", "liquid drum and bass",
                    "neurofunk", "jump up", "future garage", "electro swing",
                    "glitch hop", "breakbeat", "big beat", "breakcore",
                    "idm (intelligent dance music)", "ambient", "chillwave",
                    "synthwave", "vaporwave", "future funk", "hardstyle",
                    "rawstyle", "euphoric hardstyle", "industrial hardstyle",
                    "speedcore", "happy hardcore", "hardcore techno",
                    "gabber", "nightcore", "industrial", "darkwave",
                    "synthpop", "electropop", "chiptune", "8-bit",
                    "lo-fi", "bass music", "experimental bass", "riddim",
                    "hybrid trap", "melodic dubstep", "orchestral dubstep",
                    "cinematic bass", "drumstep", "midtempo bass",
                    "downtempo", "future trap", "neurostep", "wubstep",
                    "moombahton", "twerk music", "bounce", "french house",
                    "disco house", "funky house", "ghetto house",
                    "uk garage", "speed garage", "future garage",
                    "bassline", "uk bass", "tropical bass", "latin edm",
                    "afro house", "afrobeat edm", "electroclash",
                    "digital hardcore", "cyberpunk", "progressive breaks",
                    "breaks", "tech breaks", "trancecore", "dub techno",
                    "deep bass", "ethereal bass", "chill bass", "electro chill",
                    "experimental edm", "festival edm", "mainstage edm",
                    "complextro", "ambient", "eurodance", "big room",
                    "escape room", "vapor twitch", "uk dance",
                    "sped up", "dancefloor dnb", "deep dnb",
                    "dutch dnb", "poptimism", "glitchcore", "trip hop",
                    "bossbeat", "australian dance", "aussietronica",
                    "alternative dance", "expirimental club", "vogue",
                ],

                # F
                # G
                # H
                # I
                "*Indie": [
                    "indie", "indie rock", "indie pop", "indie folk",
                    "indie electronic", "indie dance", "indie soul",
                    "indie R&B", "indie rap", "indie punk", "indie metal",
                    "indie acoustic", "indie experimental", "indie ambient",
                    "indie psychedelic", "indie classical", "indie jazz",
                    "indie blues", "indie reggae",
                    "indie lo-fi", "indie dream pop", "indie synthpop",
                    "indie shoegaze", "indie emo", "indie garage rock",
                    "indie goth", "indie grunge", "indie Americana",
                    "indie alternative", "indie chamber pop", "indie baroque pop",
                    "indie cinematic", "indie orchestral", "indie surf rock",
                    "indie power pop", "indie dance-punk", "indie hardcore",
                    "indie math rock", "indie noise rock", "indie prog rock",
                    "indie post-punk", "indie post-rock", "indie funk",
                    "indie groove", "indie world", "indie Afrobeat",
                    "indie Latin", "indie tropical", "indie Middle Eastern",
                    "indie Indian", "indie Asian", "indie Celtic",
                    "indie Scandinavian", "indie Nordic", "indie Americana rock",
                    "indie melancholic", "indie uplifting", "indie storytelling",
                    "indie twee pop", "indie bedroom pop", "indie minimal",
                    "indie darkwave", "indie new wave", "indie Britpop",
                    "indie slowcore", "indie fastcore", "indie chillwave",
                    "indie vaporwave", "indie retro", "indie modern",
                    "indie futuristic", "indie nostalgic", "indie theatrical",
                    "indie cinematic folk", "indie chamber rock", "indie orchestral pop",
                    "indie epic", "indie lo-fi beats", "indie garage",
                    "indie surf pop", "indie funk rock", "indie art pop",
                    "indie acoustic rock", "indie folk rock", "indie electronic rock",
                    "indie bass", "indie dreampop", "indie post-dream",
                    "indie jangly pop", "indie ethereal", "indie world fusion",
                    "indie cosmic", "indie celestial", "indie quirky",
                    "indie heartfelt", "indie deep vibes", "indie groove pop",
                    "indie", "freak folk", "neo-psychedelic",
                    "neo mellow", "alt z"
                ],

                # J
                # K
                # L
                "*Latino": ["latin", "latino", "latin music", "música latina",
                      "latin pop", "latin rock", "latin alternative", "latin indie",
                      "pop latino", "latin ballads", "latin synthpop", "latin funk",
                      "latin soul", "latin chill", "latin electronic",
                      "reggaetón", "latin trap", "urbano latino", "latin hip-hop",
                      "reggae en español", "latin rap", "latin dancehall",
                      "latin r&b", "perreo", "dembow",
                      "música regional mexicana", "mariachi", "ranchera", "grupera",
                      "norteño", "banda", "corridos", "corridos tumbados",
                      "huapango", "jarabe", "bolero", "trova", "música andina",
                      "chileno", "cueca", "nueva canción", "vallenato", "joropo",
                      "salsa", "salsa romántica", "bachata", "merengue", "son cubano",
                      "timba", "cuban rumba", "guaracha", "cha-cha-chá", "mambo",
                      "bomba", "plena", "reggaetón cubano", "salsa dura",
                      "cumbia", "cumbia villera", "cumbia colombiana", "cumbia sonidera",
                      "cumbia peruana", "cumbia chilena", "cumbia mexicana",
                      "cumbia tejana", "vallenato-cumbia", "cumbia tropical",
                      "música folclórica", "folklore andino", "latin folk",
                      "música llanera", "música afrolatina", "música indígena",
                      "música afroperuana", "música criolla", "zamba",
                      "milonga", "tango", "cueca chilena", "bambuco",
                      "latin dance", "latin party", "latin beats", "tropical beats",
                      "guaguancó", "latin house", "latin deep house", "latin reggaetón mix",
                      "moombahton", "tropical bass", "latin edm",
                      "nuevo reggaetón", "latin chillwave", "latin lo-fi", "latin bedroom pop",
                      "indie latino", "latino experimental", "latin jazz", "salsa jazz",
                      "bossa nova", "latin fusion",
                      "mexican folk", "argentine rock", "chilean indie", "caribbean latino",
                      "puerto rican reggaetón", "cuban jazz", "brazilian latin", "latino urbano",
                      "latin tropical", "peruvian folk", "venezuelan folk", "latin ballad pop",
                      "andino latino", "latin experimental",
                ],
                # M
                "*Metal": [
                    "metal", "heavy metal", "thrash metal", "death metal",
                    "black metal", "power metal", "doom metal", "progressive metal",
                    "nu-metal", "groove metal", "symphonic metal", "folk metal",
                    "viking metal", "melodic death metal", "industrial metal",
                    "metalcore", "deathcore", "post-metal", "avant-garde metal",
                    "technical death metal", "grindcore", "sludge metal",
                    "stoner metal", "speed metal", "glam metal", "hair metal",
                    "gothic metal", "alternative metal", "experimental metal",
                    "ambient metal", "orchestral metal", "cinematic metal",
                    "djent", "math metal", "rap metal", "electro metal",
                    "psychedelic metal", "hardcore metal", "atmospheric black metal",
                    "drone metal", "dark metal", "epic metal", "neoclassical metal",
                    "instrumental metal", "technical metal", "chamber metal",
                    "extreme metal", "modern metal", "future metal", "retro metal",
                    "classic metal", "jazzy metal", "funk metal", "punk metal",
                    "crossover thrash", "post-hardcore metal", "blackened death metal",
                    "blackened thrash metal", "symphonic black metal", "symphonic death metal",
                    "folk-infused metal", "celtic metal", "medieval metal",
                    "pirate metal", "tribal metal", "middle eastern metal", "latin metal",
                    "japanese metal", "kawaii metal", "chinese metal", "russian metal",
                    "scandinavian metal", "finnish metal", "swedish metal",
                    "norwegian black metal", "german metal", "italian symphonic metal",
                    "spanish metal", "canadian metal", "american metal", "british metal",
                    "australian metal", "ambient black metal", "progressive death metal",
                    "melodic black metal", "raw black metal", "post-black metal",
                    "hard rock/metal", "deathgrind", "doomcore", "metalstep",
                    "cyber metal", "ethereal metal", "twee metal", "uplifting metal",
                    "melancholy metal", "storytelling metal", "concept metal", "fusion metal",
                    "slayer",
                ],

                # N
                # O
                # P
                "Piano" : ["background piano"],
                "*Pop": [
                    "pop", "electro", "dance pop", "synthpop", "indie pop",
                    "dream pop", "art pop", "bubblegum pop", "electropop",
                    "alt-pop", "bedroom pop", "folk pop", "barbadian",
                    "columbian", "swedish", "pop rock", "pop punk",
                    "j-pop", "k-pop", "c-pop", "latin pop",
                    "pixie", "tropical pop", "pop rap", "hyperpop",
                    "acoustic pop", "euro pop", "teen pop",
                    "chamber pop", "soul pop", "soft pop", "power pop",
                    "r&b pop", "adult contemporary", "anthem pop",
                    "glam pop", "orchestral pop", "dancehall pop",
                    "vocal pop", "britpop", "city pop", "future pop",
                    "opera pop", "ambient pop", "cinematic pop", "emo pop",
                    "funk pop", "classical pop", "space pop", "psychedelic pop",
                    "progressive pop", "goth pop", "romantic pop", "garage pop",
                    "new wave", "reggae pop", "island pop", "minimal pop",
                    "blues pop", "urban pop", "twee pop", "global pop",
                    "retro pop", "modern pop", "shoegaze pop", "lo-fi pop",
                    "experimental pop", "melancholy pop", "uplifting pop",
                    "jazzy pop", "contemporary pop", "world pop", "afro pop",
                    "middle eastern pop", "bollywood pop", "traditional pop",
                    "vintage pop", "classic pop", "neo-pop", "industrial pop",
                    "commercial pop", "alternative pop", "stadium pop",
                    "bedroom electronic pop", "happy pop", "melodic pop",
                    "anthemic pop", "swing pop", "duet pop", "feel-good pop",
                    "underground pop", "quirky pop", "smooth pop", "tropical house pop",
                    "urban contemporary", "girl group", "boy band", "bubblegum bass",
                ],

                # Q
                # R
                "*R&B/Soul": [
                    "r&b", "soul", "neo-soul", "classic soul", "contemporary r&b",
                    "funk", "motown", "quiet storm", "blue-eyed soul",
                    "rhythm and blues", "doo-wop", "gospel", "urban r&b",
                    "new jack swing", "p-funk", "modern soul", "acid jazz",
                    "philly soul", "southern soul", "memphis soul", "chicago soul",
                    "northern soul", "deep soul", "retro soul", "indie soul",
                    "alternative r&b", "trap soul", "progressive r&b", "electro soul",
                    "experimental r&b", "psychedelic soul", "soul jazz", "funk soul",
                    "vintage r&b", "disco soul", "lo-fi r&b", "future soul",
                    "afro soul", "caribbean soul", "latin soul", "jazz soul",
                    "melancholy r&b", "uplifting soul", "crossover r&b",
                    "soul blues", "traditional r&b", "smooth r&b", "romantic soul",
                    "fusion soul", "gospel r&b", "ambient soul", "electronic r&b",
                    "alternative soul", "dark r&b", "synth soul", "chill r&b",
                    "soulful house", "funkadelic r&b", "world soul", "afrobeat r&b",
                    "reggae soul", "island r&b", "minimal r&b", "urban soul",
                    "twee soul", "global soul", "modern soul ballads",
                    "indie r&b", "experimental soul", "emotive r&b",
                    "jazzy r&b", "vocal r&b", "cinematic soul", "classic r&b ballads",
                    "bedroom soul", "duet r&b", "happy soul", "melodic r&b",
                    "anthemic r&b", "feel-good soul", "quirky soul", "smooth soul",
                    "funky r&b", "bluegrass soul", "electro-funk r&b",
                    "groove soul", "fusion r&b", "avant-garde soul",
                    "ethereal r&b", "orchestral soul", "timeless r&b",
                    "folk soul", "future funk r&b", "dark soul",
                    "urban contemporary", "afrobeats", "reggae fusion",
                ],

            "*Rap & Hip-Hop": [
                "hip-hop", "rap", "trap", "conscious hip-hop", "gangsta rap",
                "old school hip-hop", "west coast rap", "east coast rap",
                "southern hip-hop", "midwest hip-hop", "drill", "mumble rap",
                "alternative hip-hop", "boom bap", "hardcore hip-hop",
                "experimental hip-hop", "lo-fi hip-hop", "cloud rap", "emo rap",
                "jazz rap", "underground hip-hop", "progressive rap",
                "industrial hip-hop", "funk rap", "freestyle rap", "horrorcore",
                "nerdcore", "grime", "uk drill", "afrobeat rap", "afro hip-hop",
                "latin rap", "chicano rap", "reggaeton", "dancehall rap",
                "trap soul", "melodic rap", "urban hip-hop", "commercial rap",
                "phonk", "hyphy", "snap music", "crunk", "dirty south",
                "bounce music", "g-funk", "bass music", "minimal rap",
                "chill hop", "new school hip-hop", "party rap", "pop rap",
                "hardcore rap", "lyrical rap", "motivational rap", "storytelling rap",
                "battle rap", "comedy rap", "uplifting hip-hop", "emotive rap",
                "tiktok rap", "viral rap", "drip rap", "luxury rap", "street rap",
                "political hip-hop", "conscious rap", "trap metal", "psychedelic rap",
                "spoken word hip-hop", "ambient hip-hop", "orchestral hip-hop",
                "cinematic rap", "vocal rap", "dark hip-hop", "epic rap",
                "bedroom rap", "indie hip-hop", "post-rap", "global hip-hop",
                "world rap", "island rap", "jazzy hip-hop", "gospel rap",
                "classic hip-hop", "throwback rap", "funky rap", "groove rap",
                "future rap", "chopper rap", "anime rap", "avant-garde hip-hop",
                "trap hop", "reggae rap", "soulful hip-hop", "underground rap",
                "hip", "chicago bop", "atlanta bass",
            ],
            "*Rock": [
                "rock", "classic rock", "alternative rock", "indie rock",
                "hard rock", "punk rock", "pop rock", "progressive rock",
                "psychedelic rock", "garage rock", "grunge", "post-rock",
                "arena rock", "folk rock", "southern rock", "blues rock",
                "glam rock", "space rock", "art rock", "experimental rock",
                "math rock", "noise rock", "post-punk", "surf rock",
                "stoner rock", "industrial rock", "new wave", "britpop",
                "shoegaze", "gothic rock", "emo", "melodic rock",
                "funk rock", "jazz rock", "punk", "garage punk",
                "alt-rock", "psychedelic punk", "power pop", "soft rock",
                "roots rock", "heartland rock", "acoustic rock", "lo-fi rock",
                "heavy rock", "metalcore", "pop-punk", "post-hardcore",
                "death rock", "nu-metal", "rap rock", "sludge rock",
                "progressive metal", "alternative metal", "doom rock",
                "dream rock", "punk blues", "desert rock", "experimental metal",
                "avant-garde rock", "minimal rock", "noise punk", "dark rock",
                "cinematic rock", "orchestral rock", "ambient rock",
                "vocal rock", "anthemic rock", "uplifting rock", "retro rock",
                "modern rock", "future rock", "fusion rock", "jazzy rock",
                "gospel rock", "epic rock", "funky rock", "groove rock",
                "psychedelic metal", "folk punk", "reggae rock",
                "ska punk", "island rock", "twee rock", "melancholy rock",
                "garage psych", "chamber rock", "classical rock",
                "thrash rock", "hardcore rock", "punk-infused rock",
                "americana rock", "baroque rock", "dance rock", "symphonic rock",
                "screemo", "mellow gold", "new rave", "permanent wave",
                "post-grunge", "screamo",
            ],
                # S
                # T
                # U
                # V
                # W
                # X
                # Y
                # Z
            }

    simplified_genres = []
    for genre in complex_genres:
        genre_lower = genre.lower().strip()  # Normalize case
        matched = None
        for simplified_genre, keywords in simplified_keywords.items():
            if any(keyword in genre_lower for keyword in keywords):  # Check for substring matches
                matched = simplified_genre
                break
        simplified_genres.append(matched if matched else genre.title())  # Default to title-cased genre
    return simplified_genres


def calculate_genre_distribution(audio_files, use_simple_genres):
    """Calculate the percentage distribution of genres."""
    genres = []
    for file in audio_files:
        genre_list = get_genre(file)
        if use_simple_genres:
            genre_list = map_to_simplified_genres(genre_list)
        genres.extend(genre_list)

    genre_count = Counter(genres)
    total_tracks = len(genres)

    if total_tracks == 0:
        return genre_count, {}, 0

    genre_percentage = {genre: (count / total_tracks) * 100 for genre, count in genre_count.items()}
    return genre_count, genre_percentage


def calculate_overlap(audio_files):
    """Find the number of songs that belong to multiple genres."""
    overlap_count = 0
    for file in audio_files:
        genres = get_genre(file)
        if len(genres) > 1:  # Check if a song has multiple genres
            overlap_count += 1
    return overlap_count


def main(parent):
    """Main entry point for the plugin."""
    # Locate the UI file within the plugin directory
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    ui_file_path = os.path.join(plugin_dir, "smga_ui.ui")

    print(f"[DEBUG] Looking for UI file at: {ui_file_path}")

    if not os.path.exists(ui_file_path):
        raise FileNotFoundError(f"UI file not found at: {ui_file_path}")

    # Load the plugin's UI
    plugin_widget = uic.loadUi(ui_file_path)

    # Ensure the parent has a layout
    if parent.layout() is None:
        parent.setLayout(QtWidgets.QVBoxLayout())

    # Add the plugin widget to the parent
    parent.layout().addWidget(plugin_widget)

    # Access UI elements
    select_directory_button = plugin_widget.findChild(QtWidgets.QPushButton, "pushButton_select")
    directory_input = plugin_widget.findChild(QtWidgets.QLineEdit, "lineEdit_directory")
    analyze_button = plugin_widget.findChild(QtWidgets.QPushButton, "pushButton_analyze")
    results_table = plugin_widget.findChild(QtWidgets.QTableView, "tableView_results")
    overlap_label = plugin_widget.findChild(QtWidgets.QLabel, "genre_overlap_value")
    simple_radio = plugin_widget.findChild(QtWidgets.QRadioButton, "radioButton")
    complex_radio = plugin_widget.findChild(QtWidgets.QRadioButton, "radioButton_complex")

    # Set the Complex button as the default
    complex_radio.setChecked(True)
    print("[DEBUG] Complex radio button set as default.")

    def select_directory():
        """Open a dialog to select a directory and update the input field."""
        directory = QtWidgets.QFileDialog.getExistingDirectory(plugin_widget, "Select Music Directory")
        if directory:
            print(f"[DEBUG] Selected directory: {directory}")
            directory_input.setText(directory)

    from PyQt5 import QtCore  # Import QtCore for QTimer

    def analyze():
        """Analyze the audio files in the selected directory and display results."""
        # Change button state to indicate progress
        analyze_button.setText("Analyzing...")
        analyze_button.setEnabled(False)
        overlap_label.setText("0")  # Reset overlap count display at the start

        # Use QTimer to allow the UI to update before starting analysis
        QtCore.QTimer.singleShot(100, perform_analysis)

    def perform_analysis():
        """Perform the actual analysis logic."""
        try:
            selected_directory = directory_input.text().strip()
            if not selected_directory:
                QtWidgets.QMessageBox.warning(plugin_widget, "Error", "Please select a directory first.")
                return

            use_simple_genres = simple_radio.isChecked()
            audio_files = get_audio_files(selected_directory)

            if not audio_files:
                QtWidgets.QMessageBox.information(plugin_widget, "Analysis", "No audio files found in the selected directory.")
                return

            genre_count, genre_percentage = calculate_genre_distribution(audio_files, use_simple_genres)
            overlap_count = calculate_overlap(audio_files)

            overlap_label.setText(str(overlap_count))
            display_results(genre_count, genre_percentage)

        except Exception as e:
            QtWidgets.QMessageBox.critical(plugin_widget, "Error", f"An error occurred: {e}")
            print(f"[ERROR] {e}")
        finally:
            # Reset the button state
            analyze_button.setText("Analyze")
            analyze_button.setEnabled(True)


    def display_results(genre_count, genre_percentage):
        """Populate the table with genre distribution data."""
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Genre", "Count", "Percentage (%)"])

        for genre, count in sorted(genre_count.items(), key=lambda item: genre_percentage.get(item[0], 0), reverse=True):
            percentage = genre_percentage.get(genre, 0)
            model.appendRow([
                QStandardItem(genre.title()),  # Convert to title case for display
                QStandardItem(str(count)),
                QStandardItem(f"{percentage:.2f}")
            ])

        results_table.setModel(model)
        results_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    # Connect buttons to their respective functions
    select_directory_button.clicked.connect(select_directory)
    analyze_button.clicked.connect(analyze)
