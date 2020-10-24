" author : avimehenwal
"
"
" start vim with zero configuration
" -N              									Not fully Vi compatible: 'nocompatible'
" -u <vimrc>      									Use <vimrc> instead of any .vimrc
" vi -Nu NORC <filepath>
"
" Order of rc-file detection
" 1. $VIMINIT												Environment Variable
" 2. $HOME/.vimrc
" 3. $HOME/.vim/vimrc
" 4. $EXINIT												Environment Variable
" 5. $HOME/.exrc
" 6. $VIMRUNTIME/defaults.vim

syntax on
filetype plugin indent on 					" filetype detection:ON  plugin:ON  indent:ON
set backspace=start,eol,indent			" make backspace work in Insert Mode
set noswapfile											" only useful in multi-user systems
" set hidden												" hide a unsaved buffer instead of showing warning

" File Explorer
" Configure default netrw plugin like nerdtree https://shapeshed.com/vim-netrw/
let g:netrw_banner = 0
let g:netrw_liststyle = 3
let g:netrw_browse_split = 4
let g:netrw_altv = 1
let g:netrw_winsize = 25
" augroup ProjectDrawer

" set some environment variable
let $RTP=split(&runtimepath, ',')[0]
let $RC="$HOME/.vim/vimrc"

" linter Tools :retab
