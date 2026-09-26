# Just configuration file for running commands.
#
# For more information, visit https://just.systems.

set script-interpreter := ["nu"]
set shell := ["nu", "--commands"]

export DENO_INSTALL_ROOT := justfile_directory() / ".vendor/lib/deno"
export MARIMO_SKIP_UPDATE_CHECK := "1"
export PATH := if os() == "windows" {
  justfile_directory() / ".vendor/bin;" + justfile_directory() /
  ".vendor/lib/deno/bin;" + env("PATH")
} else {
  justfile_directory() / ".vendor/bin:" + justfile_directory() /
  ".vendor/lib/deno/bin:" + env("PATH")
}
export UV_PYTHON_INSTALL_DIR :=  justfile_directory() / ".vendor/lib/uv/python"
export UV_TOOL_BIN_DIR := justfile_directory() / ".vendor/bin"
export UV_TOOL_DIR := justfile_directory() / ".vendor/lib/uv/tool"

# Build project for release.
[script]
build: _build-app _build-slide
  deno run --allow-all npm:vitepress build

[script]
_build-app: _build-lib
  mkdir doc/site/app
  let apps = ls doc/app/*.md | get name | path relative-to doc/app
  (
    {"apps": $apps} | to json | uv run jinja2 --strict --outfile
    doc/site/app/index.md doc/app/index.md.j2
  )
  for app in $apps {
    let subpath = $app | path parse | get stem
    let mode = if $subpath == "scratchpad" { "edit" } else { "run" }
    let html = $"doc/public/app/($subpath).html"
    (
      uv run marimo --yes export html-wasm --mode $mode --output $html
      $"doc/app/($app)"
    )
    minhtml  --minify-css --minify-js --output $html $html
    (
      open $html
      | str replace --all "./favicon.ico" "/melopa/favicon.ico"
      | str replace --all "./apple-touch-icon.png" "/melopa/apple-touch-icon.png"
      | str replace --all "./manifest.json" "/melopa/site.webmanifest"
      | save --force $html
    )
  }
  (
    rm --force --recursive doc/public/app/*.png doc/public/app/.nojekyll
    doc/public/app/CLAUDE.md doc/public/app/favicon.ico
    doc/public/app/manifest.json doc/public/app/site.webmanifest
  )

[script]
_build-lib:
  mkdir doc/public/lib
  uv build --out-dir build/dist
  cp build/dist/melopa-*-py3-none-any.whl doc/public/lib/

[script]
_build-slide:
  mkdir doc/site/slide
  let slides = ls doc/slide/*.md | get name | path relative-to doc/slide
  (
    {"slides": $slides} | to json | uv run jinja2 --strict --outfile
    doc/site/slide/index.md doc/slide/index.md.j2
  )
  for slide in $slides {
    let route = $slide | str replace --regex "(.+).md" "$1"
    (
      deno run --allow-all npm:@slidev/cli build --base
      $"/melopa/slide/($route)/" --out $"../public/slide/($route)"
      $"doc/slide/($slide)"
    )
    (
      deno run --allow-all npm:@slidev/cli export --output
      $"doc/public/slide/($route).pdf" $"doc/slide/($slide)"
    )
  }

# Run continuous integration pipeline.
ci: setup lint test build

# Run Deno in project environment.
[no-exit-message]
@deno *args:
  deno {{args}}

# Format project files.
format +paths=".":
  deno run --allow-all npm:prettier --write {{paths}}
  uv run ruff format {{paths}}

# Analyze files for issues.
lint +paths=".":
  deno run --allow-all npm:prettier --check {{paths}}
  uv run ruff format --check {{paths}}
  uv run ruff check {{paths}}
  uv run ty check {{paths}}

# List available commands.
[default]
@list:
  just --list

# Run project notebooks.
[no-exit-message]
note +paths="doc/app":
  uv run marimo --yes edit --no-sandbox --watch {{paths}}

# Run Nushell in project environment.
[no-exit-message]
@nu *args="nu --login":
  nu --commands "{{args}}"

# Run project website.
[no-exit-message]
run *args:
  deno run --allow-all npm:vitepress dev {{args}}

# Serve built website.
serve *args: build
  # Miniserve is used since vitepress serve command incorrectly returns audio
  # files. Issue does not occur for vitepress dev command.
  miniserve --route-prefix /melopa build/site {{args}}

# Install development tools and dependencies.
[script]
setup: _setup
  let ext = if $nu.os-info.name == "windows" { ".exe" } else { "" }
  if (which deno | is-empty) {
    print "Installing Deno."
    http get https://scruffaluff.github.io/picoware/install/deno.nu
    | nu --commands $in --preserve-env --dest .vendor/bin
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
  if (which uv | is-empty) {
    print "Installing Uv."
    http get https://scruffaluff.github.io/picoware/install/uv.nu
    | nu --commands $in --preserve-env --dest .vendor/bin
  }
  print $"Using (uv --version)."
  print "Installing packages with Deno and Uv."
  if ($env.INIT? | into bool --relaxed) {
    deno install
    uv sync
    just format
  } else {
    deno install --frozen
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

# Run project slideshows.
[script]
slide slide:
  let route = "{{slide}}" | str replace --regex ".*doc/(.+).md" "$1"
  deno run --allow-all npm:@slidev/cli --base $"/melopa/($route)/" "{{slide}}"

# Run tests (use DEBUG=1 for debugger).
test: test-js test-py

# Run JavaScript tests.
test-js +args='run':
  deno run --allow-all npm:vitest --dir src {{args}}

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
