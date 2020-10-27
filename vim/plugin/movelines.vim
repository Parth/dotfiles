" Global Plugin - automatically loaded for all files
"
" vscode line code-block, code-line movement keybindings
" https://vim.fandom.com/wiki/Moving_lines_up_or_down
"
" Use ALT + movement keys
" :help move

" use meta key bindings
" https://stackoverflow.com/a/27206531/1915935

" Using META KEY ^[ causes unexpected behaviour, delays and trigger move commands
" at undesirable occassions
"
" execute "set <M-j>=\ej"
" execute "set <M-k>=\ek"

nnoremap <Leader-j> :m .+1<CR>==
nnoremap <Leader-k> :m .-2<CR>==
vnoremap <Leader-j> :m '>+1<CR>gv=gv
vnoremap <Leader-k> :m '<-2<CR>gv=gv
inoremap <Leader-k> <Esc>:m .-2<CR>==gi
inoremap <Leader-j> <Esc>:m .+1<CR>==gi
