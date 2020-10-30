if has("autocmd")
   "source vimrc after write automatically
    ""autocmd BufWritePost .vimrc source $MYVIMRC

    " Filetype specific
    " autocmd Filetype tex setl updatetime=1
    " autocmd Filetype html,xml set listchars-=tab:>.
    " autocmd Filetype python setlocal expandtab tabstop=4 shiftwidth=4 textwidth=80 fileformat=unix
    autocmd FileType json nmap <LocalLeader>pp :%!python -m json.tool<CR>

    " show whitespaces
    " autocmd ColorScheme * highlight ExtraWhitespace ctermbg=red guibg=red
    " autocmd InsertLeave * match ExtraWhitespace /\s\+$/
    " autocmd BufEnter * :syntax sync fromstart

    " remove trailing space before writing
    " autocmd BufWritePre * %s/\s\+$//e

    " Retain code-folds
    " autocmd BufWinLeave *.vim*,*.py,*.adoc mkview
    " autocmd BufWinEnter *.vim*,*.py,*.adoc silent loadview

    " autocmd FileType vim,zsh,conf setlocal foldmethod=marker

    " cursor line and relative numbering when set focus
    " augroup toggle_cursorline
    "     autocmd!
    "     autocmd InsertEnter * :setlocal cursorline
    "     autocmd InsertLeave * :setlocal nocursorline
    " augroup END
    "
    " set cursor behavious
    " --------------------------------------------------
    autocmd InsertEnter * set cursorline!
    autocmd InsertLeave * set cursorline
endif
