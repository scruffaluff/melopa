# Just configuration file for running commands.
#
# For more information, visit https://just.systems.

set script-interpreter := ["nu"]
set shell := ["nu", "--commands"]
export DENO_INSTALL_ROOT := justfile_directory() / ".vendor/lib/deno"
export PATH := if os() == "windows" {
  justfile_directory() / ".vendor/bin;" + justfile_directory() /
  ".vendor/lib/deno/bin;" + env("PATH")
} else {
  justfile_directory() / ".vendor/bin:" + justfile_directory() /
  ".vendor/lib/deno/bin:" + env("PATH")
}

# Build project for release.
[script]
build:
  let notebooks = ls doc/*.md | get name | path relative-to doc
  let temp = mktemp --dry --tmpdir --suffix .json
  {"notebooks": $notebooks} | save $temp
  mkdir build/site/data
  uv build --out-dir build/dist
  (
    uv run jinja2 --strict --outfile build/site/index.html doc/index.html.j2
    $temp
  )
  (
    minhtml --minify-css --minify-js --output build/site/index.html
    build/site/index.html
  )
  (
    cp --recursive data/audio build/dist/melopa-*-py3-none-any.whl
    build/site/data/
  )
  for notebook in $notebooks {
    let subpath = $notebook | path parse | get stem
    let mode = if $subpath == "scratchpad" { "edit" } else { "run" }
    let html = $"build/site/($subpath).html"
    (
      uv run marimo --yes export html-wasm --mode $mode --output $html
      $"doc/($notebook)"
    )
    minhtml  --minify-css --minify-js --output $html $html
  }
  rm --force --recursive build/site/files build/site/CLAUDE.md

# Run continuous integration pipeline.
ci: setup lint test build

# Format project files.
format +paths=".":
  prettier --write {{paths}}
  uv run ruff format {{paths}}

# Analyze files for issues.
lint +paths=".":
  prettier --check {{paths}}
  uv run ruff format --check {{paths}}
  uv run ruff check {{paths}}
  uv run ty check {{paths}}

# List available commands.
[default]
@list:
  just --list

# Run Nushell in project environment.
[no-exit-message]
@nu *args="nu --login":
  nu --commands "{{args}}"

# Run project notebooks.
[no-exit-message]
run +paths="doc":
  uv run marimo --yes edit --no-sandbox --watch {{paths}}

# Serve built website.
serve *flags: build
  miniserve --route-prefix /melopa build/site {{flags}}

# Install development tools and dependencies.
[script]
setup: _setup
  let ext = if $nu.os-info.name == "windows" { ".exe" } else { "" }
  if (which deno | is-empty) {
    print "Installing Deno."
    http get https://scruffaluff.github.io/picoware/install/deno.nu
    | nu -c $"($in | decode); main --preserve-env --dest .vendor/bin"
  }
  print $"Using (deno -V)."
  if (which minhtml | is-empty) {
    let version = http get https://api.github.com/repos/wilsonzlin/minify-html/releases/latest
    | get tag_name | str substring 1..
    let target = match $nu.os-info.name {
      "macos" => $"($nu.os-info.arch)-apple-darwin"
      "linux" => $"($nu.os-info.arch)-unknown-linux-gnu"
      "windows" => $"($nu.os-info.arch)-pc-windows-msvc.exe"
    }
    print "Installing Minhtml."
    mkdir .vendor/bin
    http get $"https://github.com/wilsonzlin/minify-html/releases/download/v($version)/minhtml-($version)-($target)"
    | save --force $".vendor/bin/minhtml($ext)"
    if $nu.os-info.name != "windows" {
      chmod 755 .vendor/bin/minhtml
    }
  }
  print $"Using (minhtml --version)."
  if (which miniserve | is-empty) {
    let version = http get https://formulae.brew.sh/api/formula/miniserve.json
    | get versions.stable
    let target = match $nu.os-info.name {
      "macos" => $"($nu.os-info.arch)-apple-darwin"
      "linux" => $"($nu.os-info.arch)-unknown-linux-musl"
      "windows" => $"($nu.os-info.arch)-pc-windows-msvc.exe"
    }
    print "Installing Miniserve."
    mkdir .vendor/bin
    http get $"https://github.com/svenstaro/miniserve/releases/download/v($version)/miniserve-($version)-($target)"
    | save --force $".vendor/bin/miniserve($ext)"
    if $nu.os-info.name != "windows" {
      chmod 755 .vendor/bin/miniserve
    }
  }
  print $"Using (miniserve --version)."
  if (which prettier | is-empty) {
    print "Installing Prettier."
    deno install --allow-all --global npm:prettier
  }
  print $"Using Prettier (prettier --version)."
  if (which uv | is-empty) {
    print "Installing Uv."
    http get https://scruffaluff.github.io/picoware/install/uv.nu
    | nu -c $"($in | decode); main --preserve-env --dest .vendor/bin"
  }
  print $"Using (uv --version)."
  print "Installing Python packages with Uv."
  if ($env.INIT? | into bool --relaxed) {
    uv sync
    just format
  } else {
    uv sync --locked
  }

[unix]
_setup:
  #!/usr/bin/env sh
  set -eu
  if [ ! -x "$(command -v nu)" ]; then
    echo 'Installing Nushell.'
    curl --fail --location --show-error \
      https://scruffaluff.github.io/picoware/install/nushell.sh | sh -s -- \
      --preserve-env --dest .vendor/bin
  fi
  echo "Using Nushell $(nu --version)."

[windows]
_setup:
  #!powershell.exe
  $ErrorActionPreference = 'Stop'
  $ProgressPreference = 'SilentlyContinue'
  $PSNativeCommandUseErrorActionPreference = $True
  if (-not (Get-Command -ErrorAction SilentlyContinue nu)) {
    Write-Output 'Installing Nushell.'
    $NushellScript = Invoke-WebRequest -UseBasicParsing -Uri `
      https://scruffaluff.github.io/picoware/install/nushell.ps1
    Invoke-Expression "& { $NushellScript } --preserve-env --dest .vendor/bin"
  }
  Write-Output "Using Nushell $(nu --version)."

# Run tests (use DEBUG=1 for debugger).
test: test-js test-py

# Run JavaScripts.
test-js +args='run':
  deno run --allow-all npm:vitest {{args}}

# Run Python tests (use DEBUG=1 for debugger).
[script]
test-py *args:
  if ($env.DEBUG? | into bool --relaxed) {
    uv run pytest --pdb {{args}}
  } else {
    uv run pytest {{args}}
  }

# Run Uv in project environment.
[no-exit-message]
@uv *args:
  uv {{args}}
