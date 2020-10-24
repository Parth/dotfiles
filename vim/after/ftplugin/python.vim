" filetype=python
"
" applies only to local buffer
setlocal path=.,**
setlocal wildignore=*.pyc,*/__pycache__/*

" linting
set shiftwidth=4 tabstop=4 softtabstop=4 expandtab=4 autoindent smartindent
set colorcolumn=80

" include search
setlocal include=^\\s*import
setlocal define=^\\s*\\<\\(def\\\|class\\)\\>

" (1) convert import con.metric            => conv/metric.py
" (2) from con import conversion as conv   => conv/conversion.py conv.py
function! PyInclude(fname)
endfunction

