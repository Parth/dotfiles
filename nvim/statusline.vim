" Build statusline yourself
" :help statusline
"
set cursorline
set statusline=
set statusline+=\ %r       "if file is read-only
set statusline+=\ %M       "is file modifyable
set statusline+=\ %y       "type of file
set statusline+=\ %F       "full file path
set statusline+=\ %b       "values of char under cursor

" right leaning
set statusline+=%=
set statusline+=\ %p%%       "percentage scroll
set statusline+=\ %l/%L:%c   "total number of line
set statusline+=\ [%n]       "buffer number

" Add colors to status line?
