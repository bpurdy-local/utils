# =============================================================================
# .zshrc - Zsh configuration
# =============================================================================
# Copy to ~/.zshrc or source from it

# -----------------------------------------------------------------------------
# SENSITIVE CONFIG - Import from secure location
# -----------------------------------------------------------------------------
SENSITIVE_CONFIG="$HOME/.config/secrets/env.sh"
[[ -f "$SENSITIVE_CONFIG" ]] && source "$SENSITIVE_CONFIG"

# Also support .env.local in home directory
if [[ -f "$HOME/.env.local" ]]; then
    set -a
    source "$HOME/.env.local"
    set +a
fi

# -----------------------------------------------------------------------------
# OH-MY-ZSH (optional - comment out if not using)
# -----------------------------------------------------------------------------
# export ZSH="$HOME/.oh-my-zsh"
# ZSH_THEME="robbyrussell"  # or: agnoster, powerlevel10k/powerlevel10k
# plugins=(
#     git
#     docker
#     python
#     pip
#     virtualenv
#     zsh-autosuggestions
#     zsh-syntax-highlighting
#     fzf
# )
# source $ZSH/oh-my-zsh.sh

# -----------------------------------------------------------------------------
# SHELL OPTIONS
# -----------------------------------------------------------------------------
setopt AUTO_CD              # cd by typing directory name
setopt AUTO_PUSHD           # Push directories onto stack
setopt PUSHD_IGNORE_DUPS    # Don't push duplicates
setopt PUSHD_SILENT         # Don't print stack after pushd/popd
setopt CORRECT              # Spelling correction for commands
setopt EXTENDED_GLOB        # Extended globbing
setopt NO_CASE_GLOB         # Case insensitive globbing
setopt NUMERIC_GLOB_SORT    # Sort numerically
setopt NO_BEEP              # No beeping

# -----------------------------------------------------------------------------
# HISTORY
# -----------------------------------------------------------------------------
HISTFILE=~/.zsh_history
HISTSIZE=50000
SAVEHIST=50000

setopt EXTENDED_HISTORY          # Write timestamp to history
setopt HIST_EXPIRE_DUPS_FIRST    # Expire duplicates first
setopt HIST_IGNORE_DUPS          # Don't record duplicates
setopt HIST_IGNORE_SPACE         # Don't record commands starting with space
setopt HIST_FIND_NO_DUPS         # Don't display duplicates in search
setopt HIST_REDUCE_BLANKS        # Remove superfluous blanks
setopt SHARE_HISTORY             # Share history between sessions
setopt INC_APPEND_HISTORY        # Add commands immediately

# -----------------------------------------------------------------------------
# COMPLETION
# -----------------------------------------------------------------------------
autoload -Uz compinit && compinit
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'  # Case insensitive
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"  # Colored completions
zstyle ':completion:*' menu select  # Menu selection
zstyle ':completion:*' special-dirs true  # Complete . and ..
zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*=0=01;31'

# -----------------------------------------------------------------------------
# ENVIRONMENT
# -----------------------------------------------------------------------------
export EDITOR="vim"
export VISUAL="vim"
export PAGER="less"
export LESS="-R -F -X"
export PATH="$HOME/.local/bin:$HOME/bin:$PATH"

# -----------------------------------------------------------------------------
# AUTO LS AFTER CD
# -----------------------------------------------------------------------------
cd() {
    builtin cd "$@" && ls -la
}

pushd() {
    builtin pushd "$@" && ls -la
}

popd() {
    builtin popd "$@" && ls -la
}

# -----------------------------------------------------------------------------
# NAVIGATION
# -----------------------------------------------------------------------------
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."
alias ~="cd ~"
alias -- -="cd -"

# Directory shortcuts (customize)
alias proj="cd ~/projects"
alias docs="cd ~/Documents"
alias dl="cd ~/Downloads"

# -----------------------------------------------------------------------------
# LS ALIASES
# -----------------------------------------------------------------------------
alias ls="ls --color=auto"
alias ll="ls -la"
alias la="ls -A"
alias l="ls -CF"
alias lt="ls -lt"
alias ltr="ls -ltr"
alias lsize="ls -lSh"
alias ldot="ls -ld .*"

# -----------------------------------------------------------------------------
# FILE OPERATIONS
# -----------------------------------------------------------------------------
alias cp="cp -iv"
alias mv="mv -iv"
alias rm="rm -iv"
alias mkdir="mkdir -pv"

mkcd() { mkdir -p "$1" && cd "$1" }

extract() {
    if [[ -f "$1" ]]; then
        case "$1" in
            *.tar.bz2) tar xjf "$1" ;;
            *.tar.gz)  tar xzf "$1" ;;
            *.tar.xz)  tar xJf "$1" ;;
            *.bz2)     bunzip2 "$1" ;;
            *.rar)     unrar x "$1" ;;
            *.gz)      gunzip "$1" ;;
            *.tar)     tar xf "$1" ;;
            *.tbz2)    tar xjf "$1" ;;
            *.tgz)     tar xzf "$1" ;;
            *.zip)     unzip "$1" ;;
            *.Z)       uncompress "$1" ;;
            *.7z)      7z x "$1" ;;
            *)         echo "'$1' cannot be extracted" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

# -----------------------------------------------------------------------------
# SEARCH
# -----------------------------------------------------------------------------
alias grep="grep --color=auto"

ff() { find . -type f -iname "*$1*" }
fd() { find . -type d -iname "*$1*" }
fif() { grep -rn "$1" --include="$2" . }

# -----------------------------------------------------------------------------
# GIT
# -----------------------------------------------------------------------------
alias g="git"
alias gs="git status -sb"
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
alias gf="git fetch --all"
alias gst="git stash"
alias gstp="git stash pop"
alias gm="git merge"
alias grb="git rebase"
alias grbc="git rebase --continue"

gclean() { git branch --merged | grep -v '\*\|main\|master' | xargs -n 1 git branch -d }
gwip() { git add -A && git commit -m "WIP: $(date +%Y-%m-%d-%H%M)" }

# -----------------------------------------------------------------------------
# PYTHON
# -----------------------------------------------------------------------------
alias py="python3"
alias python="python3"
alias pip="pip3"
alias venv="python3 -m venv .venv && source .venv/bin/activate"
alias activate="source .venv/bin/activate"
alias deact="deactivate"

mkvenv() { python3 -m venv "${1:-.venv}" && source "${1:-.venv}/bin/activate" }

alias pt="pytest"
alias ptv="pytest -v"
alias ptx="pytest -x"
alias pts="pytest -s"
alias ptcov="pytest --cov --cov-report=html"

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
alias dex="docker exec -it"
alias dlogs="docker logs -f"

dclean() { docker system prune -af && docker volume prune -f }

# -----------------------------------------------------------------------------
# NETWORKING
# -----------------------------------------------------------------------------
alias ip="curl -s ifconfig.me"
alias localip="ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print \$1}'"
alias ports="lsof -i -P -n | grep LISTEN"

serve() { python3 -m http.server "${1:-8000}" }

# -----------------------------------------------------------------------------
# SYSTEM
# -----------------------------------------------------------------------------
alias reload="source ~/.zshrc"
alias path='echo -e ${PATH//:/\\n}'
alias now="date '+%Y-%m-%d %H:%M:%S'"

alias df="df -h"
alias du="du -h"
alias dud="du -d 1 -h"
alias duf="du -sh *"

alias psg="ps aux | grep -v grep | grep -i"

# -----------------------------------------------------------------------------
# UTILITIES
# -----------------------------------------------------------------------------
calc() { python3 -c "print($*)" }
weather() { curl -s "wttr.in/${1:-}" }
genpass() { openssl rand -base64 "${1:-32}" | tr -d '\n'; echo }
json() { python3 -m json.tool "$@" }
backup() { cp "$1" "$1.bak.$(date +%Y%m%d%H%M%S)" }

# Quick notes
note() {
    local notes_dir="$HOME/notes"
    mkdir -p "$notes_dir"
    if [[ -z "$1" ]]; then
        ls -lt "$notes_dir"
    else
        echo "$(date '+%Y-%m-%d %H:%M'): $*" >> "$notes_dir/quicknotes.txt"
        echo "Note added."
    fi
}

# -----------------------------------------------------------------------------
# FZF (if installed)
# -----------------------------------------------------------------------------
if command -v fzf &> /dev/null; then
    # Use fd if available, otherwise find
    if command -v fd &> /dev/null; then
        export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
        export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
        export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'
    fi

    export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border'

    # Fuzzy cd
    fcd() { cd "$(find . -type d | fzf)" }

    # Fuzzy edit
    fe() { ${EDITOR:-vim} "$(fzf)" }

    # Fuzzy git checkout branch
    fco() { git checkout "$(git branch -a | fzf | tr -d '[:space:]')" }
fi

# -----------------------------------------------------------------------------
# PROMPT
# -----------------------------------------------------------------------------
# Simple prompt with git branch (works without oh-my-zsh)
autoload -Uz vcs_info
precmd() { vcs_info }
zstyle ':vcs_info:git:*' formats ' (%b)'

setopt PROMPT_SUBST
PROMPT='%F{green}%n%f@%F{cyan}%m%f:%F{blue}%~%f%F{yellow}${vcs_info_msg_0_}%f$ '

# -----------------------------------------------------------------------------
# KEY BINDINGS
# -----------------------------------------------------------------------------
bindkey -e  # Emacs key bindings (use -v for vim)
bindkey '^[[A' history-search-backward  # Up arrow
bindkey '^[[B' history-search-forward   # Down arrow
bindkey '^[[H' beginning-of-line        # Home
bindkey '^[[F' end-of-line              # End
bindkey '^[[3~' delete-char             # Delete

# -----------------------------------------------------------------------------
# LOCAL OVERRIDES
# -----------------------------------------------------------------------------
[[ -f "$HOME/.zshrc.local" ]] && source "$HOME/.zshrc.local"

echo "🚀 Shell ready."
