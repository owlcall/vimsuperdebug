
echo "Loading autoload"

" Exit when already loaded (or "compatible" mode set)
if exists("g:superdebug_loaded") || &cp
	finish
endif

let g:superdebug_loaded = 1

" Objective of this function is to pop open a new buffer and associate it with
" the debugger callstack, which is a long running process.
function! sdbg#DBGLaunch()
	echo "DBGLaunch called!"

	" Open a new custom buffer
	"
endfunc

