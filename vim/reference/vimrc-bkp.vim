" AUTHOR : avimehenwal
" FILE   : $HOME/.vimrc  $MYVIMRC
" ORIGIN : Sat 28 Apr 05:01:05 IST 2018

" Don't seek mastery, seek proficiency

" modlines
"" /* vim: set tabstop=8 softtabstop=8 shiftwidth=8 noexpandtab : */
" do not make VIM compatible with VI. Might have undesired side-effects
" like- no undo file, no search highlights, no filetype and expandtab etc.
set nocompatible           " -N switch
let mapleader="\<Space>"
let maplocalleader="\\"

" Package-Manager +Lazy loading https://github.com/junegunn/vim-plug ---------------------{{{
if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

call plug#begin('~/.vim/plugged')
    Plug 'avimehenwal/asciidoc-sane.vim'
    Plug 'avimehenwal/vim-korrektur'
    Plug 'nelstrom/vim-visual-star-search'
    Plug 'majutsushi/tagbar'
    Plug 'tpope/vim-unimpaired'
    Plug 'tpope/vim-repeat'
    Plug 'junegunn/vader.vim'
    Plug 'mfukar/robotframework-vim'
    Plug 'lervag/vimtex'
    Plug 'xuhdev/vim-latex-live-preview', { 'for': 'tex' }
    Plug '~/.fzf'
    	let g:livepreview_previewer = 'evince'
    " Asynchronous syntax checkers
    Plug 'w0rp/ale'
    " python compiler script for makeprg
    Plug 'mattboehm/vim-unstack'
    Plug 'scrooloose/nerdtree'
        let NERDTreeShowBookmarks=1
    Plug 'itchyny/lightline.vim'
    Plug 'Stautob/vim-fish'
    " Themes and colours ---------------------------------{{{
    Plug 'chriskempson/base16-vim'
    Plug 'NLKNguyen/papercolor-theme'
    "}}}
    " Dormant ----------------------------------{{{
    "Plug 'gorodinskiy/vim-coloresque'
    "Plug 'junegunn/vim-easy-align'
    "Plug 'mhinz/vim-signify'
    "Plug 'ntpeters/vim-better-whitespace'
    "Plug 'bling/vim-bufferline'
    "Plug 'mileszs/ack.vim'
    "Plug 'hail2u/vim-css3-syntax'
    "Plug 'tpope/vim-haml'
    "Plug 'mattn/emmet-vim'
    "Plug 'jelera/vim-javascript-syntax'              " Javascript Bundle
    " Fugitive Git -------------------------------{{{
    Plug 'tpope/vim-fugitive'
    if exists("*fugitive#statusline")
      set statusline+=%{fugitive#statusline()}
    endif
    "}}}
    " UndoTree -------------------------------{{{
    "Plug 'mbbill/undotree'
    Plug 'vim-scripts/Gundo'
    if has("persistent_undo")
        set undodir=~/.undodir/
        set undofile
    endif
    "}}}
    " CtrlP can do with find-------------------------------{{{
    "Plug 'ctrlpvim/ctrlp.vim'
    "set wildmode=list:longest,list:full
    "set wildignore+=*.o,*.obj,.git,*.rbc,*.pyc,__pycache__
    "let g:ctrlp_custom_ignore = '\v[\/](node_modules|target|dist)|(\.(swp|tox|ico|git|hg|svn))$'
    "let g:ctrlp_user_command = "find %s -type f | grep -Ev '"+ g:ctrlp_custom_ignore +"'"
    "let g:ctrlp_use_caching = 1
    "}}}
    " Drag and copy visual blocks -------------------------------{{{
    "Plug 'shinokada/dragvisuals.vim'
    "vmap  <expr>  <LEFT>   DVB_Drag('left')
    "vmap  <expr>  <RIGHT>  DVB_Drag('right')
    "vmap  <expr>  <DOWN>   DVB_Drag('down')
    "vmap  <expr>  <UP>     DVB_Drag('up')
    "vmap  <expr>  D        DVB_Duplicate()
    "let g:DVB_TrimWS = 1             " Remove any introduced trailing whitespace after moving...
    "}}}
    "}}}
call plug#end()
"}}}
" General Configs -------------------------------{{{
filetype on            " enable vim filetype detection
filetype plugin on     " enable plugins on filetype
filetype indent on     " load filetype-specific indent files
set number             " display line numbers
set relativenumber     " relative numbers based on cursor position
set title              " set title of vim window to filename
set encoding=utf-8     " text encoding
set fileencoding=utf-8
set fileencodings=utf-8
set ruler              " shows cursor position offsets
" Real programmers don't use TABs but spaces
set autoindent         " copy indent to next line when <CR>
set smartindent        " strict indent rules for C-like files
set smartcase          " used with search patterns from / ? n N :g :s only
set smarttab           " detect changes on files outside vim
set shiftwidth=4       " text identation shift using << >>
set tabstop=4          " no of cols a tab is count
set softtabstop=4      " insert mode
set expandtab          " insert mode tab to space conversion
set laststatus=2       " always a status line
set history=1000       " remember more commands
set undolevels=1000
set showcmd            " shows command in bottom bar
""set cursorline         " highlight current line
""set cursor             " highlight current column
" Auto commenting list making *, #. Doesnt work with numners and -
" https://stackoverflow.com/questions/9065967/markdown-lists-in-vim-automatically-new-bullet-on-cr
set formatoptions+=jtcroqln   "h comments, format-comments, formatoptions, fo-table
set wildmenu           " visual autocomplete for command menu
set lazyredraw         " redraw only when needed. Faster macros
""set showmatch          " highlight matching [{()}]
set mouse=a
""set gcr=a:blinkon0     " Disable the blinking cursor.
set bs=2               " makes backspace behave like normal again
set splitbelow         " Natural splits
set splitright
set backspace=indent,eol,start    " effects <BS> functionality
set shortmess+=I       " disable intro splash
if !&scrolloff
  set scrolloff=1      " scrollon
endif
if !&sidescrolloff
  set sidescrolloff=5
endif
set display+=lastline  " :help 'display'
" displaying whitespaces and tabs at the end
set list               " makes whitespace chars visible
" customise how whitespaces appears
if &listchars ==# 'eol:$'
  set listchars=tab:>\ ,trail:-,extends:>,precedes:<,nbsp:+
endif
" displaying whitespaces and tabs at the end
set list               " makes whitespace chars visible
" customise how whitespaces appears
if &listchars ==# 'eol:$'
  set listchars=tab:>\ ,trail:-,extends:>,precedes:<,nbsp:+
endif

" DO NOT UNCOMMENT THIS LINE-causes unpleasent highlights
" set spell spelllang=en_us
set spellfile=$HOME/.vim/en.utf-8.add
set thesaurus+=~/Documents/thesaurus    "Add thesaurus file for ^X^T
set dictionary+=~/Documents/dictionary  "Add dictionary file for ^X^K

set wildignore=*.swp,*.bak,*.pyc,*.class,tags
set visualbell
set noerrorbells
set nobackup           " avoid creating backup file before writing to buffer
set noswapfile         " :h writebackup
" allows unwritten changes on file to open new files with :edit
set hidden             " doesn't warn while editing and closing hidden buffers
set autowrite          " Automatically save before commands like :next and :make

" vim Session-management
"":mksession ~/mysession.vim
"":source ~/mysession.vim
""$ vim -S ~/mysession.vim

"           +--Disable hlsearch while loading viminfo
"           | +--Remember marks for last 500 files
"           | |    +--Remember up to 10000 lines in each register
"           | |    |      +--Remember up to 1MB in each register
"           | |    |      |     +--Remember last 1000 search patterns
"           | |    |      |     |     +---Remember last 1000 commands
"           | |    |      |     |     |
"           v v    v      v     v     v
""set viminfo=h,'500,<10000,s1000,/1000,:1000
""set viminfo='1000,f1,<500  "lines, marks
"}}}
" Autocommands --------------------------------------{{{
if has("autocmd")
   "source vimrs after write automatically
    ""autocmd BufWritePost .vimrc source $MYVIMRC
    filetype plugin indent on

    " Filetype specific
    autocmd Filetype tex setl updatetime=1
    autocmd Filetype html,xml set listchars-=tab:>.
    autocmd Filetype python setlocal expandtab tabstop=4 shiftwidth=4 textwidth=80 fileformat=unix
    autocmd FileType json nmap <LocalLeader>pp :%!python -m json.tool<CR>

    " show whitespaces
    autocmd ColorScheme * highlight ExtraWhitespace ctermbg=red guibg=red
    autocmd InsertLeave * match ExtraWhitespace /\s\+$/
    autocmd BufEnter * :syntax sync fromstart

    " remove trailing space before writing
    autocmd BufWritePre * %s/\s\+$//e

    " Retain code-folds
    autocmd BufWinLeave *.vim*,*.py,*.adoc mkview
    autocmd BufWinEnter *.vim*,*.py,*.adoc silent loadview

    autocmd FileType vim,zsh,conf setlocal foldmethod=marker

    " cursor line and relative numbering when set focus
    augroup toggle_cursorline
        autocmd!
        autocmd InsertEnter * :setlocal cursorline
        autocmd InsertLeave * :setlocal nocursorline
    augroup END
endif

" highlight only the characters (not the entire column) exceeding 100 char rule
""highlight ColorColumn ctermfg=red
""call matchadd('ColorColumn', '\%81v', 100)

" Remember cursor position
""augroup vimrc-remember-cursor-position
""  autocmd!
""  autocmd BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g`\"" | endif
""augroup END
"}}}
" Key Maps ----------------------------------{{{
" Efficient shortcuts
nnoremap : ;
nnoremap ; :
nnoremap Q :q!<CR>
nnoremap <Tab> :tabNext<CR>
" Maintain Visual Mode after shifting > and <
vmap < <gv
vmap > >gv
" Ablity to move on big wrapped lines
nnoremap j gj
nnoremap k gk
" Remove annoying highlight left after localsearch
nnoremap <silent> '/ :nohlsearch<CR>
" Save file in 2 strokes, i_CTRL-O :w
" mappings freeze the terminal, recover CTRL+Q
" use xtty -ixon in startup script
nnoremap <silent> <C-S> :write<CR>
inoremap <silent> <C-S> <C-O>:write<CR>

" File Explorer
nnoremap <Leader>e :Vexplore<CR>
nnoremap <F9> :NERDTreeToggle<CR>
nnoremap <F4> :!firefox % &<CR>
" Use Q for formatting the current paragraph (or selection)
vnoremap <F3> gq
nnoremap <F3> gqap

" Searching and Grepping ---------------------{{{
" Grepping and searching. Use :vimgrep for quickfix
set path+=**           " inbuild fuzzy search at path root
set incsearch          " incremental search as we type
set hlsearch
set ignorecase         " ignore case in search
" hinders ** search and file searches autocompletion :find
""set autochdir          " change to dir of file selected/opened/deleted

" -R read all files under dir and follow symlinks
nnoremap <F5> :grep -R '<cWORD>' .<CR>
nnoremap <F6> :execute "vimgrep /" . expand("<cWORD>") . "/gj **" <Bar> cw<CR>
nnoremap <F7> :cprevious<CR>
nnoremap <F8> :cnext<CR>
""nnoremap <F6> :grep '<cWORD>' %<CR>
""nnoremap <F7> :execute "vimgrep /" . expand("<cWORD>") . "/gj *.py"<CR>
"}}}

" Editing and sourcing from config files.
nnoremap <Leader>es :echom Scratch()<CR>
nnoremap <Leader>ev :execute "tabedit". $HOME . "/.vimrc"<CR>
nnoremap <Leader>sv :execute "source". $MYVIMRC<CR>
nnoremap <Leader>zr :tabedit $HOME/.zshrc<CR>
nnoremap <Leader>ze :tabedit $HOME/.zshenv<CR>

" Linux/ External Tools
nnoremap <Leader>co :%!column -t<CR>
nnoremap <Leader>so :%!sort -k1<CR>
nnoremap <Leader>w :w !sudo tee %
" editing with sudo after opening file /etc/hosts etc
cnoremap w!! w !sudo tee % >/dev/null

" Plugins
nnoremap <Leader>u :GundoToggle<CR>
nnoremap <Leader>t :TagbarToggle<CR>

" Copy / Paste Behavious -------------------------------------{{{
"vim-default to use cut-buffer * instead of primary application clipboard *
set clipboard=unnamedplus  " don't have to prepend "+ before yank and paste
" Copy pasting to local
noremap <Leader>p "+p
noremap <Leader>P "+P
noremap <Leader>y "+y
noremap <Leader>Y "+Y
set pastetoggle=<F2>   " prevent cascading indents of paragraphs
"}}}

" Git Fujitive
noremap <Leader>gw :Gwrite<CR>
noremap <Leader>gb :Gblame<CR>
noremap <Leader>gd :Gvdiff<CR>
noremap <Leader>gst :Gstatus<CR>

" don't get distracked
"" inoremap <Left>  <NOP>
"" inoremap <Right> <NOP>
"" inoremap <Up>    <NOP>
"" inoremap <Down>  <NOP>

"}}}
"Snippet-Manager------------------------------------{{{
let SNIPPET_BASE = $HOME . '/.vim/templates/'
nnoremap <expr> <localleader>bs   ':-1read' . SNIPPET_BASE . 'bootstrap_html.snippet<CR>7jwf>a'
nnoremap <expr> <localleader>py   ':-1read' . SNIPPET_BASE . 'python_script.snippet<CR>4jA <ESC>:r! date<CR>kJ6j0'
nnoremap <expr> <localleader>sh   ':-1read' . SNIPPET_BASE . 'shell_script.snippet<CR>3jA <ESC>:r! date<CR>kJ6jA<SPACE>'
nnoremap <expr> <localleader>pl   ':-1read' . SNIPPET_BASE . 'perl_script.snippet<CR>3jA <ESC>:r! date<CR>kJ10jA'
nnoremap <expr> <localleader>html ':-1read' . SNIPPET_BASE . 'html_basic.snippet<CR>7jwf>a'
nnoremap <expr> <localleader>rfw  ':-1read' . SNIPPET_BASE . 'robotframework.snippet<CR>1ji'

" to-dos
" Add asciidoctor formats mappings
"}}}
" ABBREVIATIONS-----------------------------------------{{{
inoreabbrev lorem Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eligendi non quis exercitationem culpa nesciunt nihil aut nostrum explicabo reprehe nderit optio amet ab temporibus asperiores quasi cupiditate. Voluptatum ducimus voluptates voluptas?
inoreabbrev -- ---
inoreabbrev avi Avi Mehenwal
inoreabbrev email avi.mehenwal@gmai.com
inoreabbrev bang #!/usr/bin/env python
inoreabbrev shebang #!/usr/bin/env bash
"}}}
" Colorscheme ------------------------------{{{
if has('gui_running')
    ""set background=light
    set guifont=Monospace\ 12
    "colorscheme base16-default-light
    colorscheme base16-default-dark
endif
syntax enable         " syntax on
"}}}
" Custome Functions -----------------------------------{{{
" Diff b/w current buffer and corresponding file on disk
function! s:DiffWithSaved()
    let filetype=&ft
    diffthis
    vnew | r # | normal! 1Gdd
    diffthis
    exe "setlocal bt=nofile bh=wipe nobl noswf ro ft=" . filetype
endfunction
command! DiffSaved call s:DiffWithSaved()

" Enabling syntax highlighting for diff and patches
augroup PatchDiffHighlight
    autocmd!
    autocmd FileType  diff  syntax enable
augroup END

" scratch buffer
function! Scratch()
    vnew
    setlocal buftype=nofile
    setlocal bufhidden=hide
    setlocal noswapfile
    "" :vnew | setlocal nobuflisted buftype=nofile bufhidden=wipe noswapfile
    return "Scratch Pad loaded!"
endfunction
"}}}

" TO-DOs
" search highlight the current word with cursor position
" https://github.com/Shougo/deoplete.nvim
" :mkspell ~/.vim/spell/en-basic basic_english_words.txt      personal dict
" inbuilt Filebrowsing using netrw netrw-browse-maps
""let g:netrw_banner=0              " disable banner
""let g:netrw_browse_split=4        " open in prior window
""let g:netrw_altv=1                " open spilit on right
""let g:netrw_liststyle=3           " tree view
""let g:netrw_list_hide=netrw_gitignore#Hide()

if has('nvim')
  let $NVIM_TUI_ENABLE_TRUE_COLOR=1
endif
"" https://github.com/Shougo/dein.vim
