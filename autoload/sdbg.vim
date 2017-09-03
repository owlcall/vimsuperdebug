
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
	py3file $VIMRUNTIME/autoload/python/plugin.py
else
	" when we use pathogen for instance
	let $CUR_DIRECTORY=expand("<sfile>:p:h")
	echo $CUR_DIRECTORY

	if filereadable($CUR_DIRECTORY."/python/plugin.py")
		py3file $CUR_DIRECTORY/python/plugin.py
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
	python3 Launch()
endfunc

function! sdbg#DBGQuit()
	python3 Quit()
	"TODO: Cleanup after ourselves, return to last tab/window/buffer we were in
endfunc

function! sdbg#DBGNavBacktrace()
	python3 NavBacktrace()
endfunc

function! sdbg#DBGSetBreakpoint(source, line)
	"python3 
endfunc

function! sdbg#DBGPause()
	python3 Pause()
endfunc

function! sdbg#DBGResume()
	python3 Resume()
endfunc

function! sdbg#DBGStepOver()
	python3 StepOver()
endfunc

function! sdbg#DBGStepInto()
	python3 StepInto()
endfunc

function! sdbg#DBGStepOut()
	python3 StepOut()
endfunc



