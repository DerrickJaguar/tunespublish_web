let currentIndex = 0;

let songs = [
    {% for song in all_songs %}
        {
            title: "{{ song.name }}",
            artist: "{{ song.album }}",
            file: "{{ song.song_file.url }}",
            img: "{{ song.song_img.url }}"
        },
    {% endfor %}
];

let audioPlayer = document.getElementById("audio-player");
let audioSource = document.getElementById("audio-source");
let songTitle = document.getElementById("current-song-title");
let songArtist = document.getElementById("current-song-artist");
let songImage = document.getElementById("current-song-img");

document.getElementById("next-song").addEventListener("click", () => {
    if (currentIndex < songs.length - 1) {
        currentIndex++;
        updateSong();
    }
});

document.getElementById("prev-song").addEventListener("click", () => {
    if (currentIndex > 0) {
        currentIndex--;
        updateSong();
    }
});

function updateSong() {
    let newSong = songs[currentIndex];
    audioSource.src = newSong.file;
    audioPlayer.load();
    audioPlayer.play();

    songTitle.textContent = newSong.title;
    songArtist.textContent = newSong.artist;
    songImage.src = newSong.img;
}
