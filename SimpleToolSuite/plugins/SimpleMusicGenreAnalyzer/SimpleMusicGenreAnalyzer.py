import os
from collections import Counter
from mutagen import File
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


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
                "country blues", "classic blues", "modern blues",
                "contemporary blues", "blues rock", "soul blues",
                "funk blues", "rhythm and blues", "piedmont blues",
                "jump blues", "urban blues", "gospel blues", "boogie-woogie",
                "new orleans blues", "west coast blues", "louisiana blues",
                "british blues", "psychedelic blues", "progressive blues",
                "hard blues", "traditional blues", "slide guitar blues",
                "harmonica blues", "slow blues", "jazzy blues",
                "swing blues", "country-infused blues", "folk blues",
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

            # D
            # E
            "*EDM": [
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
                "dutch dnb",
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
                "indie blues", "indie country", "indie reggae",
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
                "acoustic pop", "euro pop", "teen pop", "country pop",
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
            "screemo", "mellow gold", "new rave"
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
        genre_lower = genre.lower().strip()
        matched = None
        for simplified_genre, keywords in simplified_keywords.items():
            if any(keyword in genre_lower for keyword in keywords):
                matched = simplified_genre
                break
        # Default to the original genre title-cased if no matching keyword is found
        simplified_genres.append(matched if matched else genre.title())
    return simplified_genres


def calculate_genre_distribution(audio_files, simplified=False):
    """Calculate the percentage distribution of genres."""
    genres = []
    for file in audio_files:
        genre_list = get_genre(file)
        genres.extend(genre_list)

    if simplified:
        genres = map_to_simplified_genres(genres)

    genre_count = Counter(genres)
    total_tracks = len(genres)

    if total_tracks == 0:
        return genre_count, {}, 0

    multiple_category_songs = sum(1 for file in audio_files if len(get_genre(file)) > 1)
    genre_percentage = {genre: (count / total_tracks) * 100 for genre, count in genre_count.items()}
    return genre_count, genre_percentage, multiple_category_songs


def run_analysis(directory, simplified, output_widget):
    """Run analysis and display results."""
    if not os.path.isdir(directory):
        messagebox.showerror("Error", "Invalid directory. Please try again.")
        return

    output_widget.delete('1.0', tk.END)
    output_widget.insert(tk.END, "Scanning for audio files...\n")
    audio_files = get_audio_files(directory)

    if not audio_files:
        output_widget.insert(tk.END, "No audio files found in the directory.\n")
        return

    output_widget.insert(tk.END, "Calculating genre distribution...\n")
    genre_count, genre_distribution, multiple_category_songs = calculate_genre_distribution(audio_files, simplified=simplified)

    if genre_distribution:
        output_widget.insert(tk.END, f"\nTotal Songs: {len(audio_files)}\n")
        output_widget.insert(tk.END, f"Songs in Multiple Categories: {multiple_category_songs}\n")
        output_widget.insert(tk.END, "\n* = Tags Are Categorized\n")

        tagged_genres = {k: v for k, v in genre_distribution.items() if '*' in k}
        untagged_genres = {k: v for k, v in genre_distribution.items() if '*' not in k}

        max_digits = len(str(len(genre_distribution)))

        output_widget.insert(tk.END, "\n--- Tagged Genres ---\n")
        for i, (genre, percentage) in enumerate(sorted(tagged_genres.items(), key=lambda x: x[1], reverse=True), 1):
            output_widget.insert(tk.END, f"{i:0{max_digits}d}. {percentage:06.2f}% - {genre} ({genre_count[genre]} songs)\n")

        output_widget.insert(tk.END, "\n----------------------\n")

        output_widget.insert(tk.END, "\n--- Untagged Genres ---\n")
        for i, (genre, percentage) in enumerate(sorted(untagged_genres.items(), key=lambda x: x[1], reverse=True), 1):
            output_widget.insert(tk.END, f"{i:0{max_digits}d}. {percentage:06.2f}% - {genre} ({genre_count[genre]} songs)\n")
    else:
        output_widget.insert(tk.END, "No genre information found in the audio files.\n")


def main(parent):
    """Main entry point for the plugin."""
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    directory_var = tk.StringVar()
    simplified_var = tk.BooleanVar(value=False)

    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(2, weight=1)

    ttk.Label(frame, text="Music Directory:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    ttk.Entry(frame, textvariable=directory_var, width=50).grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
    ttk.Button(frame, text="Browse", command=lambda: directory_var.set(filedialog.askdirectory())).grid(row=0, column=2, padx=5, pady=5)

    ttk.Checkbutton(frame, text="Show Simplified Genres", variable=simplified_var).grid(row=1, column=0, columnspan=3, padx=5, pady=5)

    output_text = tk.Text(frame, wrap=tk.WORD, height=20)
    output_text.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

    analyze_button = ttk.Button(frame, text="Analyze")

    def start_analysis():
        """Change button text to 'Analyzing...' and run analysis."""
        analyze_button.config(text="Analyzing...", state=tk.DISABLED)
        parent.update_idletasks()

        def perform_analysis():
            analyze()
            analyze_button.config(text="Analyze", state=tk.NORMAL)

        parent.after(100, perform_analysis)

    def analyze():
        """Run the analysis and display results."""
        directory = directory_var.get()
        simplified = simplified_var.get()
        if not directory:
            messagebox.showerror("Error", "Please select a music directory.")
            analyze_button.config(text="Analyze", state=tk.NORMAL)
            return

        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "Analysis started...\n")
        try:
            run_analysis(directory, simplified, output_text)
        except Exception as e:
            output_text.insert(tk.END, f"Error: {e}\n")
        output_text.insert(tk.END, "Analysis completed.\n")

    analyze_button.config(command=start_analysis)
    analyze_button.grid(row=3, column=0, columnspan=3, pady=10)
