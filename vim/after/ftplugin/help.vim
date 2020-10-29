" open Help files in vertical split
" ------------------------------------------------------------ 
" Use command-line abbreviations to expand help to vertical help
"
" Make buffer comfortable to read on 14inch laptop screen

augroup vertical_help
autocmd!
autocmd BufWinEnter <buffer> wincmd H | vertical resize 80
augroup END

