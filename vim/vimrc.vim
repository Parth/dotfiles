set nocompatible              " be iMproved, required
filetype off                  " required
let mapleader=","
set rtp+=~/dotfiles/vim/bundle/Vundle.vim
call vundle#begin()

Plugin 'VundleVim/Vundle.vim'
Plugin 'scrooloose/nerdtree'
Plugin 'valloric/youcompleteme'
Plugin 'scrooloose/syntastic'
Plugin 'leafgarland/typescript-vim'

call vundle#end()

" NERDTree Config 
" 
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 0 && !exists("s:std_in") | NERDTree | endif

autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 1 && isdirectory(argv()[0]) && !exists("s:std_in") | exe 'NERDTree' argv()[0] | wincmd p | ene | exe 'cd '.argv()[0] | endif

autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif

map <C-n> :NERDTreeToggle<CR>

" Syntastic Config
set statusline+=%#warningmsg#
set statusline+=%{SyntasticStatuslineFlag()}
set statusline+=%*
let g:syntastic_always_populate_loc_list = 1
let g:syntastic_auto_loc_list = 1
let g:syntastic_check_on_open = 1
let g:syntastic_check_on_wq = 0
let g:syntastic_javascript_checkers = ['eslint']
let g:syntastic_javascript_eslint_exe = 'npm run lint --'
let g:syntastic_typescript_checkers = ['eslint']

" Upload Functionality
set exrc
set secure

" rsync
function RemoteSync ()
    if !exists("g:enable_rsync") || g:enable_rsync == 0
        return
    endif

    let rsync_command = "rsync -a --exclude='*.swp' --exclude='.git/' --exclude='.exrc' --exclude-from=" . g:rsync_exclude . " . " . g:rsync_user . "@" . g:rsync_server . ":" .g:rsync_remote . " &> /dev/null"

    execute "!" . rsync_command
endfunction

au BufWritePost,FileWritePost * silent call RemoteSync()

function Upload ()
    if !exists("g:enable_rsync") || g:enable_rsync == 0
        return
    endif

    let rsync_command = "rsync -a --progress --exclude='*.swp' --exclude='.git/' --exclude='.exrc' --exclude-from=" . g:rsync_exclude . " . " . g:rsync_user . "@" . g:rsync_server . ":" .g:rsync_remote . " "

    execute "!" . rsync_command
endfunction

map <C-s> :call Upload()<CR>

" Gernal Settings
syntax enable
set relativenumber 
set number
set tabstop=4
set shiftwidth=4
set expandtab
set hlsearch

" Line numbers to gray color
highlight LineNr term=bold cterm=NONE ctermfg=DarkGrey ctermbg=NONE gui=NONE guifg=DarkGrey guibg=NONE

" Return to the same line you left off at
	augroup line_return
		au!
		au BufReadPost *
			\ if line("'\"") > 0 && line("'\"") <= line("$") |
			\	execute 'normal! g`"zvzz' |
			\ endif
	augroup END

" Auto load
	" Triger `autoread` when files changes on disk
	" https://unix.stackexchange.com/questions/149209/refresh-changed-content-of-file-opened-in-vim/383044#383044
	" https://vi.stackexchange.com/questions/13692/prevent-focusgained-autocmd-running-in-command-line-editing-mode
	autocmd FocusGained,BufEnter,CursorHold,CursorHoldI * if mode() != 'c' | checktime | endif
	set autoread 
	" Notification after file change
	" https://vi.stackexchange.com/questions/13091/autocmd-event-for-autoread
	autocmd FileChangedShellPost *
	  \ echohl WarningMsg | echo "File changed on disk. Buffer reloaded." | echohl None

filetype plugin indent on
