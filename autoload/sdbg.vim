
"echo "Loading autoload"

" Exit when already loaded (or "compatible" mode set)
if exists("g:superdebug_loaded") || &cp
	finish
endif

" Internal variables
let g:superdebug_loaded = 1

" User-customizable variables


" Load Python script
if filereadable($VIMRUNTIME."/autoload/python/plugin.py")
	pyfile $VIMRUNTIME/autoload/python/plugin.py
else
	" when we use pathogen for instance
	let $CUR_DIRECTORY=expand("<sfile>:p:h")
	echo $CUR_DIRECTORY

	if filereadable($CUR_DIRECTORY."/python/plugin.py")
		pyfile $CUR_DIRECTORY/python/plugin.py
	else
		call confirm('failed to load super debug python scripts; ensure the module is installed correctly and try again.\n', 'OK')
		quit
	endif
endif

autocmd VimLeavePre * call sdbg#DBGQuit()

function! sdbg#DBGLaunch()
	"TODO: Save information about the current buffer
	" Open a new custom buffer
	"below 16new
	"redraw!
	python Launch()
endfunc

function! sdbg#DBGQuit()
	python Quit()
	"TODO: Cleanup after ourselves, return to last tab/window/buffer we were in
endfunc

function! sdbg#DBGNavBacktrace()
	python NavBacktrace()
endfunc

function! sdbg#DBGSetBreakpoint(source, line)
	"python 
endfunc

function! sdbg#DBGPause()
	python Pause()
endfunc

function! sdbg#DBGResume()
	python Resume()
endfunc

function! sdbg#DBGStepOver()
	python StepOver()
endfunc

function! sdbg#DBGStepInto()
	python StepInto()
endfunc

function! sdbg#DBGStepOut()
	python StepOut()
endfunc



