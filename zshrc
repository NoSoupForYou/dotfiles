# Lines configured by zsh-newuser-install
HISTFILE=~/.histfile
HISTSIZE=100000
SAVEHIST=100000
setopt appendhistory autocd extendedglob nomatch notify
unsetopt beep
bindkey -e
# End of lines configured by zsh-newuser-install
# The following lines were added by compinstall
zstyle :compinstall filename '/home/Carlos/.zshrc'

autoload -Uz compinit
compinit
# End of lines added by compinstall
#
autoload -U promptinit
promptinit
prompt adam2

export PATH="${PATH}":/bin
cd
