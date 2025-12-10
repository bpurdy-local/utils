# =============================================================================
# .bashrc - Interactive shell configuration
# =============================================================================
# Copy to ~/.bashrc or source from it: source /path/to/this/file

# -----------------------------------------------------------------------------
# SENSITIVE CONFIG - Import from secure location
# -----------------------------------------------------------------------------
# Keep API keys, tokens, and secrets in a separate file not in version control
SENSITIVE_CONFIG="$HOME/.config/secrets/env.sh"
if [[ -f "$SENSITIVE_CONFIG" ]]; then
    source "$SENSITIVE_CONFIG"
fi

# Also support .env.local in home directory
if [[ -f "$HOME/.env.local" ]]; then
    set -a  # Auto-export all variables
    source "$HOME/.env.local"
    set +a
fi

# -----------------------------------------------------------------------------
# SHELL OPTIONS
# -----------------------------------------------------------------------------
shopt -s histappend       # Append to history, don't overwrite
shopt -s checkwinsize     # Update LINES and COLUMNS after each command
shopt -s cdspell          # Autocorrect typos in cd
shopt -s dirspell         # Autocorrect directory names
shopt -s globstar         # Enable ** for recursive globbing
shopt -s nocaseglob       # Case-insensitive globbing

# -----------------------------------------------------------------------------
# HISTORY
# -----------------------------------------------------------------------------
export HISTSIZE=50000
export HISTFILESIZE=100000
export HISTCONTROL=ignoreboth:erasedups  # Ignore duplicates and space-prefixed
export HISTIGNORE="ls:cd:pwd:exit:clear:history"
export HISTTIMEFORMAT="%Y-%m-%d %H:%M:%S  "

# -----------------------------------------------------------------------------
# ENVIRONMENT
# -----------------------------------------------------------------------------
export EDITOR="vim"
export VISUAL="vim"
export PAGER="less"
export LESS="-R -F -X"  # Color, quit if one screen, don't clear screen

# Path additions (add your own)
export PATH="$HOME/.local/bin:$HOME/bin:$PATH"

# -----------------------------------------------------------------------------
# AUTO LS AFTER CD - Your favorite feature!
# -----------------------------------------------------------------------------
cd() {
    builtin cd "$@" && ls -la
}

# Also support pushd/popd with auto-ls
pushd() {
    builtin pushd "$@" && ls -la
}

popd() {
    builtin popd "$@" && ls -la
}

# -----------------------------------------------------------------------------
# NAVIGATION ALIASES
# -----------------------------------------------------------------------------
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."
alias .....="cd ../../../.."
alias ~="cd ~"
alias -- -="cd -"  # Go back to previous directory

# Quick access to common directories (customize these)
alias proj="cd ~/projects"
alias docs="cd ~/Documents"
alias dl="cd ~/Downloads"
alias desk="cd ~/Desktop"

# -----------------------------------------------------------------------------
# LS ALIASES
# -----------------------------------------------------------------------------
alias ls="ls --color=auto"
alias ll="ls -la"
alias la="ls -A"
alias l="ls -CF"
alias lt="ls -lt"           # Sort by time
alias ltr="ls -ltr"         # Sort by time, reverse
alias lsize="ls -lSh"       # Sort by size
alias ldot="ls -ld .*"      # Show only dotfiles
alias ldir="ls -la | grep '^d'"  # Directories only

# -----------------------------------------------------------------------------
# FILE OPERATIONS
# -----------------------------------------------------------------------------
alias cp="cp -iv"           # Interactive, verbose
alias mv="mv -iv"           # Interactive, verbose
alias rm="rm -iv"           # Interactive, verbose (consider trash-cli instead)
alias mkdir="mkdir -pv"     # Create parents, verbose

# Safe operations
alias trash="mv -t ~/.Trash"  # macOS, adjust for Linux
alias del="trash"

# Quick file creation
mkcd() {
    mkdir -p "$1" && cd "$1"
}

# Extract any archive
extract() {
    if [[ -f "$1" ]]; then
        case "$1" in
            *.tar.bz2)   tar xjf "$1"    ;;
            *.tar.gz)    tar xzf "$1"    ;;
            *.tar.xz)    tar xJf "$1"    ;;
            *.bz2)       bunzip2 "$1"    ;;
            *.rar)       unrar x "$1"    ;;
            *.gz)        gunzip "$1"     ;;
            *.tar)       tar xf "$1"     ;;
            *.tbz2)      tar xjf "$1"    ;;
            *.tgz)       tar xzf "$1"    ;;
            *.zip)       unzip "$1"      ;;
            *.Z)         uncompress "$1" ;;
            *.7z)        7z x "$1"       ;;
            *)           echo "'$1' cannot be extracted" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

# -----------------------------------------------------------------------------
# SEARCH
# -----------------------------------------------------------------------------
alias grep="grep --color=auto"
alias egrep="egrep --color=auto"
alias fgrep="fgrep --color=auto"

# Find files
ff() { find . -type f -iname "*$1*"; }
fd() { find . -type d -iname "*$1*"; }

# Find in files (grep recursively)
fif() { grep -rn "$1" --include="$2" .; }

# Find large files
large() { find . -type f -size +${1:-100M} -exec ls -lh {} \; | sort -k5 -h; }

# -----------------------------------------------------------------------------
# GIT SHORTCUTS
# -----------------------------------------------------------------------------
alias g="git"
alias gs="git status"
alias ga="git add"
alias gaa="git add -A"
alias gc="git commit"
alias gcm="git commit -m"
alias gca="git commit --amend"
alias gco="git checkout"
alias gcob="git checkout -b"
alias gb="git branch"
alias gba="git branch -a"
alias gbd="git branch -d"
alias gd="git diff"
alias gds="git diff --staged"
alias gl="git log --oneline -20"
alias glog="git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
alias gp="git push"
alias gpu="git push -u origin HEAD"
alias gpull="git pull"
alias gf="git fetch"
alias gfa="git fetch --all"
alias gst="git stash"
alias gstp="git stash pop"
alias gm="git merge"
alias grb="git rebase"
alias grbc="git rebase --continue"
alias grba="git rebase --abort"

# Git helpers
gclean() {
    # Delete merged branches
    git branch --merged | grep -v '\*\|main\|master' | xargs -n 1 git branch -d
}

gwip() {
    # Quick work-in-progress commit
    git add -A && git commit -m "WIP: $(date +%Y-%m-%d-%H%M)"
}

# -----------------------------------------------------------------------------
# PYTHON
# -----------------------------------------------------------------------------
alias py="python3"
alias python="python3"
alias pip="pip3"
alias venv="python3 -m venv .venv && source .venv/bin/activate"
alias activate="source .venv/bin/activate"
alias deact="deactivate"

# Create and activate venv in one step
mkvenv() {
    python3 -m venv "${1:-.venv}" && source "${1:-.venv}/bin/activate"
}

# Run pytest with common options
alias pt="pytest"
alias ptv="pytest -v"
alias ptx="pytest -x"  # Stop on first failure
alias pts="pytest -s"  # Show print statements
alias ptcov="pytest --cov --cov-report=html"

# Linting
alias lint="ruff check ."
alias lintfix="ruff check --fix ."
alias fmt="ruff format ."

# -----------------------------------------------------------------------------
# DOCKER
# -----------------------------------------------------------------------------
alias d="docker"
alias dc="docker compose"
alias dps="docker ps"
alias dpsa="docker ps -a"
alias di="docker images"
alias drm="docker rm"
alias drmi="docker rmi"
alias dex="docker exec -it"
alias dlogs="docker logs -f"

# Docker cleanup
dclean() {
    docker system prune -af
    docker volume prune -f
}

# -----------------------------------------------------------------------------
# NETWORKING
# -----------------------------------------------------------------------------
alias ip="curl -s ifconfig.me"
alias localip="ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print \$1}'"
alias ports="netstat -tulanp 2>/dev/null || lsof -i -P -n | grep LISTEN"
alias ping="ping -c 5"

# Quick HTTP server
serve() {
    python3 -m http.server "${1:-8000}"
}

# -----------------------------------------------------------------------------
# SYSTEM
# -----------------------------------------------------------------------------
alias reload="source ~/.bashrc"
alias path='echo -e ${PATH//:/\\n}'
alias now="date '+%Y-%m-%d %H:%M:%S'"
alias week="date +%V"
alias timer='echo "Timer started. Stop with Ctrl-D." && date && time cat && date'

# Disk usage
alias df="df -h"
alias du="du -h"
alias dud="du -d 1 -h"
alias duf="du -sh *"

# Process management
alias psg="ps aux | grep -v grep | grep -i"
alias top="htop 2>/dev/null || top"
alias mem="free -h 2>/dev/null || vm_stat"

# Quick system info
sysinfo() {
    echo "Hostname: $(hostname)"
    echo "Uptime: $(uptime)"
    echo "Kernel: $(uname -r)"
    echo "CPU: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2)"
    echo "Memory: $(free -h 2>/dev/null | awk '/^Mem:/ {print $2}' || sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 " GB"}')"
}

# -----------------------------------------------------------------------------
# UTILITIES
# -----------------------------------------------------------------------------
# Quick note taking
note() {
    local notes_dir="$HOME/notes"
    mkdir -p "$notes_dir"
    if [[ -z "$1" ]]; then
        # List notes
        ls -lt "$notes_dir"
    else
        # Add note
        echo "$(date '+%Y-%m-%d %H:%M'): $*" >> "$notes_dir/quicknotes.txt"
        echo "Note added."
    fi
}

# Calculator
calc() {
    python3 -c "print($*)"
}

# Weather
weather() {
    curl -s "wttr.in/${1:-}"
}

# Generate random password
genpass() {
    openssl rand -base64 "${1:-32}" | tr -d '\n'
    echo
}

# JSON pretty print
json() {
    if [[ -t 0 ]]; then
        python3 -m json.tool "$@"
    else
        python3 -m json.tool
    fi
}

# Stopwatch
stopwatch() {
    date1=$(date +%s)
    echo "Stopwatch started. Press Ctrl-C to stop."
    while true; do
        echo -ne "$(date -u --date @$(($(date +%s) - date1)) +%H:%M:%S)\r"
        sleep 0.1
    done
}

# Backup a file
backup() {
    cp "$1" "$1.bak.$(date +%Y%m%d%H%M%S)"
}

# -----------------------------------------------------------------------------
# PROMPT
# -----------------------------------------------------------------------------
# Git branch in prompt
parse_git_branch() {
    git branch 2>/dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}

# Colors
RED='\[\033[0;31m\]'
GREEN='\[\033[0;32m\]'
YELLOW='\[\033[0;33m\]'
BLUE='\[\033[0;34m\]'
PURPLE='\[\033[0;35m\]'
CYAN='\[\033[0;36m\]'
WHITE='\[\033[0;37m\]'
RESET='\[\033[0m\]'

# Prompt: user@host:path (branch)$
export PS1="${GREEN}\u${WHITE}@${CYAN}\h${WHITE}:${BLUE}\w${YELLOW}\$(parse_git_branch)${RESET}\$ "

# -----------------------------------------------------------------------------
# LOCAL OVERRIDES
# -----------------------------------------------------------------------------
# Source machine-specific config if it exists
if [[ -f "$HOME/.bashrc.local" ]]; then
    source "$HOME/.bashrc.local"
fi

echo "🚀 Shell ready."
