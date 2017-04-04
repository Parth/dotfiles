" General Vim settings
	syntax on
	let mapleader=","
	set relativenumber number
	set autoindent

	set cursorline
	hi Cursor ctermfg=White ctermbg=Yellow cterm=bold guifg=white guibg=yellow gui=bold

	set foldmethod=indent
	hi Folded ctermbg=023

	set hlsearch
	nnoremap <C-l> :nohl<CR><C-l>:echo "Search Cleared"<cr>

	nnoremap n nzzzv
	nnoremap N Nzzzv

	nnoremap H 0
	nnoremap L $
	nnoremap J G
	nnoremap K gg

	map <tab> %

	set backspace=indent,eol,start

	nnoremap <Space> za
	nnoremap <leader>z zMzvzz

	nnoremap vv 0v$

	set listchars=tab:\|\ 
	nnoremap <leader><tab> :set list!<cr>
	set pastetoggle=<F2>

" Language Specific
	" General
		inoremap <leader>for <esc>Ifor (int i = 0; i < <esc>A; i++) {<enter>}<esc>O<tab>
		inoremap <leader>if <esc>Iif (<esc>A) {<enter>}<esc>O<tab>
		

	" Java
		inoremap <leader>sys <esc>ISystem.out.println(<esc>A);
		vnoremap <leader>sys yOSystem.out.println(<esc>pA);

	" C++
		inoremap <leader>cout <esc>Istd::cout << <esc>A << std::endl;
		vnoremap <leader>cout yOstd::cout << <esc>pA << std:endl;

	" C
		inoremap <leader>out <esc>Iprintf(<esc>A);<esc>
		vnoremap <leader>out yOprintf(<esc>pA, );<esc>hi

	" Typescript
		autocmd BufNewFile,BufRead *.ts set syntax=javascript


" File and Window Management 
	inoremap <leader>s <Esc>:w<CR>
	nnoremap <leader>s :w<CR>

	inoremap <leader>q <ESC>:x<CR>
	nnoremap <leader>q :x<CR>
	nnoremap <leader>t :tabnew 

" Return to the same line you left off at
	augroup line_return
		au!
		au BufReadPost *
			\ if line("'\"") > 0 && line("'\"") <= line("$") |
			\	execute 'normal! g`"zvzz' |
			\ endif
	augroup END

" Future stuff
	"Swap line
	"Insert blank below and above
