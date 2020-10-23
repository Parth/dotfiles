" Syntax
syntax enable

" Preferences
let g:mapleader='\'
set history=5000
set showcmd
set nojoinspaces
set complete-=t
set hidden
set clipboard=unnamedplus                             "automatically use system clipboard
set foldmethod=manual
filetype plugin indent on
set backspace=start,eol,indent				"to make backspace work

" set listchars=tab:▸\ ,eol:¬
set foldlevelstart=99
set noswapfile
set number relativenumber                             "relative numbering from cursor

" search and sort
set incsearch					      "realtime incremental search as we type
set hlsearch 						"highlight search
set ignorecase
set smartcase 						"ignores ignorecase
set cindent						"indent C code
set autoindent
set tagstack          "start storing tags on tagstack

" https://stackoverflow.com/questions/1878974/redefine-tab-as-4-spaces#:~:text=Always%20keep%20'tabstop'%20at%208,4%20(or%203)%20characters.
set tabstop=8 softtabstop=0 expandtab shiftwidth=4 smarttab


" Build Tools and compilers for quickfix
set makeprg=make
" latex gcc npm \run \lint python haml
" could be updated by plugin for a specific project

" Plugins
set completefunc=emoji#complete


" Plugin settings
let g:airline#extensions#tabline#enabled = 1
" let g:airline_theme='simple'
let g:airline#extensions#tabline#left_sep = ' '
let g:airline#extensions#tabline#left_alt_sep = '|'
let g:airline#extensions#tabline#formatter = 'default'
let g:rg_highlight = 1
" airline integrations
let g:airline#extensions#coc#enabled = 1
let g:airline#extensions#fzf#enabled = 1
let g:airline#extensions#quickfix#quickfix_text = 'Quickfix'

" theme
set t_Co=256
syntax on
let g:gruvbox_contrast_dark = 'hard'
let g:gruvbox_contrast_light = 'hard'
colorscheme gruvbox
set background=dark

" ultisnip snippet manager
let g:UltiSnipsExpandTrigger="<tab>"
let g:UltiSnipsJumpForwardTrigger="<c-b>"
let g:UltiSnipsJumpBackwardTrigger="<c-z>"
" If you want :UltiSnipsEdit to split your window.
let g:UltiSnipsEditSplit="vertical"


" Runtimepath
set rtp+=$HOME/.fzf/bin/fzf
set rtp+=$HOME/.vim/plugged/gruvbox
