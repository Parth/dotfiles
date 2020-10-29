" Plugins Configurations
" Source this file after plugins are installed
"

" vim-emoji
" --------------------------------------------------------------------------------------------
set completefunc=emoji#complete

" Theme
" --------------------------------------------------------------------------------------------
set t_Co=256
let g:gruvbox_contrast_dark = 'hard'
let g:gruvbox_contrast_light = 'hard'
colorscheme gruvbox
set background=dark

" Plugin Airline
" --------------------------------------------------------------------------------------------
let g:airline#extensions#tabline#enabled = 1
" let g:airline_section_c
let g:airline_theme='simple'
let g:airline#extensions#tabline#left_sep = ' '
let g:airline#extensions#tabline#left_alt_sep = '|'
let g:airline#extensions#tabline#formatter = 'default'
let g:airline#extensions#tabline#buffer_nr_show = 1         "show buffer number
let g:rg_highlight = 1
" airline integrations
let g:airline#extensions#coc#enabled = 1
let g:airline#extensions#fzf#enabled = 1
let g:airline#extensions#quickfix#quickfix_text = 'Quickfix'

" ultisnip snippet manager
" --------------------------------------------------------------------------------------------
" Set ultisnips triggers
let g:UltiSnipsExpandTrigger="<tab>"                                            
let g:UltiSnipsJumpForwardTrigger="<tab>"                                       
let g:UltiSnipsJumpBackwardTrigger="<s-tab>"  
" If you want :UltiSnipsEdit to split your window.
let g:UltiSnipsEditSplit="vertical"

" vim-ripGrep
" ------------------------------------------------------------  
" open quickfix window in vertical split
" doesnt look nice, text too cluttered, cant read anything
" :vertical copen
