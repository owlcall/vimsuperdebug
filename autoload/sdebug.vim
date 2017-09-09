
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

autocmd VimLeavePre * call SDebug#Quit()

function! SDebug#Launch()
	"TODO: Save information about the current buffer
	" Open a new custom buffer
	"below 16new
	"redraw!
	
	python vim.command("tabe")
	python OpenViewSource()
	python vim.command("below 16 split")
	python OpenViewBacktrace()
	python Launch()
	redraw
	python Breakpoint("main.cpp", 49)
	python Run("/Users/owl/git/bravo/bin/bravo")
	python Refresh()
endfunc

function! SDebug#Quit()
	python Quit()
	"TODO: Cleanup after ourselves, return to last tab/window/buffer we were in
endfunc

function! SDebug#NavBacktrace()
	python NavBacktrace()
endfunc

function! SDebug#SetBreakpoint(source, line)
	"python 
endfunc

function! SDebug#SetBreakpointHere()
	python Breakpoint()
endfunc

function! SDebug#Pause()
	python Pause()
endfunc

function! SDebug#Resume()
	python Resume()
endfunc

function! SDebug#StepOver()
	python StepOver()
endfunc

function! SDebug#StepInto()
	python StepInto()
endfunc

function! SDebug#StepOut()
	python StepOut()
endfunc



