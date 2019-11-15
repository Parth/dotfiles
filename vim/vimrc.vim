" Variables
	let isWindows = system('uname -mrs | grep Microsoft | wc -l')
" General Vim settings
	syntax on
	syntax enable
	filetype plugin on
	set omnifunc=syntaxcomplete#Complete
	set backspace=indent,eol,start
	let mapleader=","
	set autoindent
	set tabstop=4
	set shiftwidth=4
	set dir=/tmp/
"	set relativenumber 
	set number

	" Disable terminal output, makes ack better, might block other plugins
	set shellpipe=>

	set background=dark
	if isWindows == 0 |
		colorscheme solarized
		let g:solarized_termcolors=256 |
	endif

	autocmd Filetype html setlocal sw=2 expandtab
	autocmd Filetype javascript setlocal sw=4 expandtab
	autocmd Filetype typescript setlocal sw=4 expandtab
	"autocmd Filetype typescript set omnifunc=javascriptcomplete#CompleteJS
	autocmd Filetype typescript set omnifunc=tscompletejob#complete

"	set cursorline
	hi Cursor ctermfg=White ctermbg=Yellow cterm=bold guifg=white guibg=yellow gui=bold

	set hlsearch
"	nnoremap <C-l> :nohl<CR><C-l>:echo "Search Cleared"<CR>
"	nnoremap <C-c> :set norelativenumber<CR>:set nonumber<CR>:echo "Line numbers turned off."<CR>
"	nnoremap <C-n> :set relativenumber<CR>:set number<CR>:echo "Line numbers turned on."<CR>

"	nnoremap n nzzzv
"	nnoremap N Nzzzv

"	nnoremap H 0
"	nnoremap L $
"	nnoremap J G
"	nnoremap K gg

"	map <tab> %

"	set backspace=indent,eol,start

"	nnoremap <Space> za
"	nnoremap <leader>z zMzvzz

"	nnoremap vv 0v$

"	set listchars=tab:\|\ 
"	nnoremap <leader><tab> :set list!<cr>
"	set pastetoggle=<F2>
"	set mouse=a
"	set incsearch

" Language Specific
	" Tabs
		so ~/dotfiles/vim/tabs.vim

	" General
		inoremap <leader>for <esc>Ifor (int i = 0; i < <esc>A; i++) {<enter>}<esc>O<tab>
		inoremap <leader>if <esc>Iif (<esc>A) {<enter>}<esc>O<tab>
		

	" Java
		inoremap <leader>sys <esc>ISystem.out.println(<esc>A);
		vnoremap <leader>sys yOSystem.out.println(<esc>pA);

	" Java
		inoremap <leader>con <esc>Iconsole.log(<esc>A);
		vnoremap <leader>con yOconsole.log(<esc>pA);

	" C++
		inoremap <leader>cout <esc>Istd::cout << <esc>A << std::endl;
		vnoremap <leader>cout yOstd::cout << <esc>pA << std:endl;

	" C
		inoremap <leader>out <esc>Iprintf(<esc>A);<esc>2hi
		vnoremap <leader>out yOprintf(, <esc>pA);<esc>h%a

	" Typescript
		autocmd BufNewFile,BufRead *.ts set syntax=javascript
		autocmd BufNewFile,BufRead *.tsx set syntax=javascript

	" Markup
		inoremap <leader>< <esc>I<<esc>A><esc>yypa/<esc>O<tab>


" File and Window Management 
"	inoremap <leader>w <Esc>:w<CR>
"	nnoremap <leader>w :w<CR>
"
"	inoremap <leader>q <ESC>:q<CR>
"	nnoremap <leader>q :q<CR>
"
"	inoremap <leader>x <ESC>:x<CR>
"	nnoremap <leader>x :x<CR>

"	nnoremap <leader>e :Ex<CR>
"	nnoremap <leader>t :tabnew<CR>:Ex<CR>
"	nnoremap <leader>v :vsplit<CR>:w<CR>:Ex<CR>
"	nnoremap <leader>s :split<CR>:w<CR>:Ex<CR>

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

" Future stuff
	"Swap line
	"Insert blank below and above

" Pathogen Plugins
"so ~/dotfiles/vim/pathogen.vim
"set runtimepath+=~/dotfiles/vim
" execute pathogen#runtime_append_all_bundles()
"execute pathogen#infect()

" Plugins ----------------------------------------------
" NERDTree -----

nnoremap <silent> <Leader>M :NERDTreeToggle<CR>
nnoremap <silent> <Leader>m :NERDTreeFind<CR>
let NERDTreeMinimalUI=1
let NERDTreeDirArrows=1
let NERDTreeShowHidden=1
" Close if ND is the last tab
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif

" TSCompleteJob ------
let g:tscompletejob_enable_tagstack = 1

" ACK ---------
nnoremap <leader>s :Ack!  src/<left><left><left><left><left>
xnoremap <leader>S y:Ack!  src/<left><left><left><left><left><C-R>"

" Omnisharp .NET ------
let g:OmniSharp_server_stdio=1
" let g:OmniSharp_server_path='~/dotfiles/utils/omnisharp-linux-x64/run'
