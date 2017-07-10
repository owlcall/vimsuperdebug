
"echo "Loading autoload"

" Exit when already loaded (or "compatible" mode set)
if exists("g:superdebug_loaded") || &cp
	finish
endif

" Internal variables
let g:superdebug_loaded = 1

" User-customizable variables


" Load Python script
if filereadable($VIMRUNTIME."/autoload/python/superdbg.py")
	py3file $VIMRUNTIME/autoload/python/superdbg.py
else
	" when we use pathogen for instance
	let $CUR_DIRECTORY=expand("<sfile>:p:h")
	echo $CUR_DIRECTORY

	if filereadable($CUR_DIRECTORY."/python/superdbg.py")
		py3file $CUR_DIRECTORY/python/superdbg.py
	else
		call confirm('failed to load super debug python scripts; ensure the module is installed correctly and try again.\n', 'OK')
		quit
	endif
endif

autocmd VimLeavePre * call sdbg#DBGQuit()

" Objective of this function is to pop open a new buffer and associate it with
" the debugger callstack, which is a long running process.
function! sdbg#DBGLaunch()
	" Save information about the current buffer
	" Open a new custom buffer
	"below 16new
	"redraw!
	python3 Launch()
endfunc

" Quit debugger
function! sdbg#DBGQuit()
	python3 Quit()

	" Close current buffer
	" Return to the last accessed buffer
endfunc

" Backtrace navigation
function! sdbg#DBGBacktraceGoTo()
	python3 BacktraceGoTo()
endfunc

" Set breakpoint
function! sdbg#DBGBreakpoint()
endfunc

" Interrupt existing program being debugged
function! sdbg#DBGInterrupt()
endfunc






