#!/usr/bin/env nu

const repo = path self | path dirname --num-levels 2

for file in (ls $"($repo)/data/audio" | get name) {
    let parts = $file | path parse
    if $parts.extension != "flac" {
        let output = $"($parts.parent)/($parts.stem).flac"
        (
            ffmpeg -hide_banner -loglevel error -i $file -ac 1 -filter:a
            aformat=s16:44100 $output
        )
        rm $file
    }
}
