import argparse
import os
import subprocess
import tempfile
import math

VIDEO_EXTENSIONS = (".mp4", ".mov", ".mkv", ".avi")


def run(cmd):
    subprocess.run(cmd, check=True)


def get_duration(file):
    """Get media duration using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def get_clip_order(folder):
    order_file = os.path.join(folder, "order.txt")

    if os.path.exists(order_file):
        with open(order_file) as f:
            files = [line.strip() for line in f if line.strip()]
        files = [os.path.join(folder, f) for f in files]
    else:
        files = [
            os.path.join(folder, f)
            for f in sorted(os.listdir(folder))
            if f.lower().endswith(VIDEO_EXTENSIONS)
        ]

    return files


def build_concat_file(clips, path):
    with open(path, "w") as f:
        for clip in clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")


def concat_videos(clips, output, tempdir, fps):
    concat_file = os.path.join(tempdir, "concat.txt")
    build_concat_file(clips, concat_file)

    run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_file,
            "-r",
            str(fps),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-c:a",
            "aac",
            output,
        ]
    )


def prepare_audio(audio_files, video_duration, tempdir):
    """Loop audio tracks if needed and concatenate them."""
    durations = [get_duration(a) for a in audio_files]
    total_audio = sum(durations)

    loops_needed = math.ceil(video_duration / total_audio)

    concat_file = os.path.join(tempdir, "audio_concat.txt")

    with open(concat_file, "w") as f:
        for _ in range(loops_needed):
            for audio in audio_files:
                f.write(f"file '{os.path.abspath(audio)}'\n")

    combined_audio = os.path.join(tempdir, "combined_audio.wav")

    run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_file,
            "-c",
            "copy",
            combined_audio,
        ]
    )

    return combined_audio


def mix_audio(video, audio, output, video_volume, music_volume):
    run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-i",
            video,
            "-i",
            audio,
            "-filter_complex",
            f"[0:a]volume={video_volume}[a0];[1:a]volume={music_volume}[a1];"
            f"[a0][a1]amix=inputs=2:duration=first[a]",
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-shortest",
            output,
        ]
    )


def main():
    parser = argparse.ArgumentParser(description="Merge video clips with optional music")

    parser.add_argument("clip_folder")
    parser.add_argument("--audio", nargs="*", default=[])
    parser.add_argument("--output", default="output.mp4")
    parser.add_argument("--video-volume", type=float, default=1.0)
    parser.add_argument("--music-volume", type=float, default=0.3)

    # NEW FPS FLAG
    parser.add_argument("--fps", type=int, default=30, help="Output video FPS (default: 30)")

    args = parser.parse_args()

    clips = get_clip_order(args.clip_folder)

    if not clips:
        raise Exception("No clips found")

    with tempfile.TemporaryDirectory() as tempdir:
        temp_video = os.path.join(tempdir, "video.mp4")

        print("Concatenating clips...")
        concat_videos(clips, temp_video, tempdir, args.fps)

        if not args.audio:
            print("No music provided. Saving video only.")
            os.rename(temp_video, args.output)
            print("Done:", args.output)
            return

        print("Preparing audio...")
        video_duration = get_duration(temp_video)
        combined_audio = prepare_audio(args.audio, video_duration, tempdir)

        print("Mixing audio...")
        mix_audio(
            temp_video,
            combined_audio,
            args.output,
            args.video_volume,
            args.music_volume,
        )

    print("Done:", args.output)


if __name__ == "__main__":
    main()
