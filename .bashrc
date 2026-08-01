#
# ~/.bashrc
#
source ./.git-prompt.sh

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

export WALLPAPER_PATH="/home/esteb/images/wallpapers/space.jpg"

alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias clearr='clear; neofetch --source /home/esteb/.config/qtile/assets/neofetch/test.txt'
alias widewall='feh --bg-fill "/home/esteb/images/wallpapers/space.jpg"'
alias updatesystem='cd /home/esteb/Scripts; ./sysmaintenance.sh'
alias memoria='cd /home/esteb/Documentos/Memoria/tt-repo'
alias wallpaper='setwallpaper gradient5.jpg'

# Function to change the wallpaper using feh
setwallpaper() {
    local dir="$HOME/images/wallpapers"

    if [[ -z "$1" ]]; then
        echo "Uso: setwallpaper <archivo>"
        return 1
    fi

    feh --bg-fill "$dir/$1"
}

_setwall_completion() {
    local dir="$HOME/images/wallpapers"
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local file

    COMPREPLY=()

    while IFS= read -r -d '' file; do
        file="${file##*/}"   # deja solo el nombre del archivo
        [[ $file == "$cur"* ]] && COMPREPLY+=("$file")
    done < <(
        find "$dir" -maxdepth 1 -type f \
            \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" \) \
            -print0
    )
}

complete -F _setwall_completion setwallpaper

# Colors
yellow='\[\e[33m\]'

PS1='\[\e[33m\][\[\e[34m\]\u\[\e[34m\]@\[\e[34m\]\h \[\e[37m\]\W\[\e[33m\]]\[\e[32m\]$(__git_ps1 "(%s)")\[\e[37m\]\$ \[\e[37m\]'

#PS1='\[\e[33m\][\[\e[37m\]\W\[\e[33m\]]\[\e[37m\]\$ \[\e[37m\]'

neofetch --source /home/esteb/.config/qtile/assets/neofetch/test.txt

[ -f "/home/esteb/.ghcup/env" ] && . "/home/esteb/.ghcup/env" # ghcup-env

# opencode
export PATH=/home/esteb/.opencode/bin:$PATH
 
cd /home/esteb/Documentos/Memoria/tt-repo
