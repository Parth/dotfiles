" set compiler
"

let current_compiler = 'go'
CompilerSet makeprg=go\ build\ ./...

" cmd/demo/main.go:43:4: undefined: mt
CompilerSet errorformat=%E%f:%l%c:%m
