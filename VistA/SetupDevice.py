;---------------------------------------------------------------------------
; Copyright 2011 The Open Source Electronic Health Record Agent
;
; Licensed under the Apache License, Version 2.0 (the "License");
; you may not use this file except in compliance with the License.
; You may obtain a copy of the License at
;
;     http://www.apache.org/licenses/LICENSE-2.0
;
; Unless required by applicable law or agreed to in writing, software
; distributed under the License is distributed on an "AS IS" BASIS,
; WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
; See the License for the specific language governing permissions and
; limitations under the License.
;---------------------------------------------------------------------------
;initialization -- turn match off to make comparisons more lenient
case match: off

;set the title
title: Setup Device
logfile:<P1>

on error: $Exit
; set up a timer for 10 minutes (10*60*10), should be more than enough to finish
timer 6000

wait for:>
;switch to the right namespace
send: znspace "${NAMESPACE}"<CR>
wait for:${NAMESPACE}>
;---------------------------------------------------------------------
;- SECTION TO SET UP DEVICE
;---------------------------------------------------------------------
send:S DUZ=1 D Q^DI<CR>
wait for:Select OPTION:
send:1<CR>
wait for:INPUT TO WHAT FILE:
send:DEVICE<CR>
wait for:EDIT WHICH FIELD
send:$I<CR>
wait for:THEN EDIT FIELD
send:SIGN-ON/SYSTEM DEVICE<CR>
wait for:THEN EDIT FIELD
send:<CR>
wait for:Select DEVICE NAME:
send:NULL<CR>
wait for:CHOOSE 1
send:1<CR>
wait for:$I:
send://./nul<CR>
wait for:SIGN-ON/SYSTEM DEVICE:
send:NO<CR>
wait for: Select DEVICE NAME:
send:CONSOLE<CR>
wait for: Select OPTION:
send:<CR>
wait for:CHOOSE 1
send:1<CR>
wait for:$I:
send:|TRM|<CR>
wait for:SIGN-ON/SYSTEM DEVICE:
send:YES<CR>
wait for:${NAMESPACE}>
$Exit:
    timer 0
    ; close the log file
    closelog
    ; exit the terminal
    terminate
